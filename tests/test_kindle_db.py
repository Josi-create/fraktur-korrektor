"""Neuere Kindles (Firmware ab 5.19): Markierungen aus der Datenbank, der Text aus dem KFX-Buch (#61)."""
import os
import pytest
import kfx, kindle
from kfxbau import book, pos, note, database, container

PARAS = ['Die Kolonisten zogen nach Osten.', 'Der Weg war weit, und die Wagen waren schwer.', 'In Tiflis wartete man.']
DOC = 'D0A108F4C57D409AB49207AD20EF81EB'      # eigenes Dokument (per Send to Kindle)
SHOP = 'B0FAKE0001'                           # gekauft: verschlüsselt
MS = 1788207392225                            # 31. August 2026


def test_kfx_lesen(tmp_path):
    p = tmp_path / 'x.kfx'
    p.write_bytes(book('Die Reise', 'Muster, Hans', DOC, PARAS, pages=[(0, 0, '7'), (1, 4, '8')]))
    b = kfx.read(str(p))
    assert (b.title, b.author, b.ident) == ('Die Reise', 'Muster, Hans', DOC)
    s = pos(PARAS, 1)
    assert b.quote(s, s + len('Der Weg war weit') - 1) == 'Der Weg war weit'
    # über einen Absatz hinweg: Leerraum statt zusammengeklebter Wörter
    assert b.quote(pos(PARAS, 0, 20), pos(PARAS, 1, 6)) == 'nach Osten. Der Weg'
    # Zeilen eines Scans als eigene Absätze: das getrennte Wort wird wieder eins, ein Gedankenstrich bleibt
    lines = ['Die Kolo-', 'nisten zogen –', 'nach Osten.']
    p.write_bytes(book('Zeilen', 'X', DOC, lines))
    assert kfx.read(str(p)).quote(pos(lines, 0), pos(lines, 2, 10)) == 'Die Kolonisten zogen – nach Osten.'
    assert b.location(0) == 1 and b.location(pos(PARAS, 1)) == pos(PARAS, 1) // 10 + 1
    assert (b.page(pos(PARAS, 0, 3)), b.page(pos(PARAS, 1, 3)), b.page(pos(PARAS, 1, 4))) == ('7', '7', '8')
    p.write_bytes(book('Gekauft', 'X', SHOP, PARAS, drm=1))
    with pytest.raises(kfx.Locked):
        kfx.read(str(p))
    p.write_bytes(b'DRMION' + b'\0' * 100)
    with pytest.raises(kfx.Locked):
        kfx.read(str(p))
    p.write_bytes(b'kein Buch')
    with pytest.raises(ValueError):
        kfx.read(str(p))


def test_dateiname():
    assert kindle._ident('Altes Land_ Roman_B00R6UC8WK.kfx') == ('B00R6UC8WK', 'Altes Land: Roman')
    assert kindle._ident('Die Listensammlerin_ Roman _ Von der Preisträgerin_B00ECLK63Y.kfx') == \
        ('B00ECLK63Y', 'Die Listensammlerin: Roman | Von der Preisträgerin')
    assert kindle._ident('Kronos\' Kinder_ Roman_B07CKSZB9B_sample.kfx')[0] == 'B07CKSZB9B'
    assert kindle._ident('Fatma - Immanuel Walker_%s.kfx' % DOC) == (DOC, 'Fatma - Immanuel Walker')
    assert kindle._ident('irgendwas.kfx')[0] == ''


def kindle_ordner(tmp_path, clippings=None, rows=None):
    """Ein Kindle, wie er als Laufwerk erscheint (oder wie ihn `fetch` holt)."""
    root = tmp_path / 'Kindle'
    items = root / 'documents' / 'Downloads' / 'Items01'
    os.makedirs(items)
    (items / ('Die Reise_%s.kfx' % DOC)).write_bytes(book('Die Reise', 'Muster, Hans', DOC, PARAS))
    (items / ('Ein Roman_ Spannend_%s.kfx' % SHOP)).write_bytes(b'DRMION')
    if clippings is not None:
        (root / 'documents' / 'My Clippings.txt').write_bytes(clippings.encode('utf-8'))
    d, s = '%s-PDOC-CR!AAA-1' % DOC, '%s-EBOK-CR!BBB-1' % SHOP
    h = lambda n, a, b, ms=MS: note('HIGHLIGHT', pos(PARAS, n, a), pos(PARAS, n, b), ms)
    database(str(root / 'system' / 'ksdk' / '.annotations' / 'amzn1.account.X' / kindle.DB), rows if rows is not None else [
        ('server_view', d, 'h1', h(1, 0, 15), None),                                       # »Der Weg war weit«
        ('server_view', d, 'h2', h(0, 0, 31, MS - 10 ** 9), None),                         # erster Absatz, früher
        ('server_view', d, 'n1', note('NOTE', pos(PARAS, 1, 15), pos(PARAS, 1, 15), MS + 1, 'Vgl. Stumpp'), None),
        ('server_view', d, 'b1', note('BOOKMARK', pos(PARAS, 2), pos(PARAS, 2), MS), None),
        ('server_view', d, 'h3', h(2, 0, 7), None),
        ('local_edit', d, 'h3', h(2, 0, 7), 'DELETE'),                                     # gelöscht, noch nicht abgeglichen
        ('staging_server_view', d, 'h4', h(2, 3, 9), None),                                # unterwegs zu Amazon
        ('server_view', s, 'k1', note('HIGHLIGHT', 10, 20, MS), None),
        ('server_view', s, 'k2', note('HIGHLIGHT', 30, 40, MS), None),
        ('server_view', s, 'k0', note('HIGHLIGHT', 5, 8, 1700000000000), None)])          # 2023: steht in My Clippings.txt
    return str(root)


CLIP = '\r\n'.join(['Die Reise (Muster, Hans)',
                    '- Ihre Markierung bei Position 1 | Hinzugefügt am Montag, 3. März 2025 22:15:32', '',
                    'Die Kolonisten zogen nach Osten.', '==========', ''])


def test_datenbank_und_buch(tmp_path):
    entries, info = kindle.load(kindle_ordner(tmp_path, CLIP))
    assert info['device']
    assert info['locked'] == [dict(title='Ein Roman: Spannend', n=2, why='drm')]  # k0 ist älter als My Clippings.txt
    books = kindle.books(entries)
    assert [(b['title'], b['highlights'], b['notes'], b['bookmarks']) for b in books] == [('Die Reise', 3, 1, 1)]
    its, cut = kindle.items(entries, books[0]['key'])
    # der erste Absatz steht in beiden Quellen und kommt einmal; die gelöschte Markierung fehlt, die Notiz hängt an ihrer
    assert [(i['text'], i['note']) for i in its] == [
        ('Die Kolonisten zogen nach Osten.', ''), ('Der Weg war weit', 'Vgl. Stumpp'), ('Tiflis', '')]
    assert its[1]['loc'] == (pos(PARAS, 1) // 10 + 1, pos(PARAS, 1, 15) // 10 + 1)
    # ohne My Clippings.txt zählt jede Markierung im gekauften Buch
    entries, info = kindle.load(kindle_ordner(tmp_path / 'b'))
    assert info['locked'] == [dict(title='Ein Roman: Spannend', n=3, why='drm')]
    # die Datei vom Laufwerk gewählt (über »Öffnen …«): die Datenbank kommt mit
    root = kindle_ordner(tmp_path / 'c', CLIP)
    assert kindle.load(os.path.join(root, 'documents', 'My Clippings.txt'))[1]['device']


def test_buch_fehlt_oder_kaputt(tmp_path):
    root = kindle_ordner(tmp_path)
    p = os.path.join(root, 'documents', 'Downloads', 'Items01', 'Die Reise_%s.kfx' % DOC)
    with open(p, 'wb') as f:
        f.write(container([('$348', '$538', {'$169': 'kaputt'})])[:200])
    entries, info = kindle.load(root)
    assert dict(title='Die Reise', n=4, why='missing') in info['locked']
    os.remove(p)
    entries, info = kindle.load(root)
    assert dict(title=DOC, n=4, why='missing') in info['locked']  # ohne Datei auch kein Titel


def test_scan_und_zettel(lib, tmp_path):
    root, vault = kindle_ordner(tmp_path), tmp_path / 'Vault'
    os.makedirs(vault)
    code, r = lib.lpost('/api/kindle_scan', dict(path=root))
    assert code == 200 and not r['copy'] and r['locked'][0]['why'] == 'drm'
    b = r['books'][0]
    folder = str(vault / 'Reise')
    code, r = lib.lpost('/api/kindle_notes', dict(path=root, key=b['key'], folder=folder, lang='de'))
    assert code == 200 and r['created'] == 3
    text = open(os.path.join(folder, sorted(n for n in os.listdir(folder) if n.startswith('02'))[0]), encoding='utf-8').read()
    assert text.startswith('**Anmerkung**\n\nVgl. Stumpp\n\n---\n\n> Der Weg war weit\n\nPosition %d–%d, [[0 Quellenangabe|Die Reise]]' % (
        pos(PARAS, 1) // 10 + 1, pos(PARAS, 1, 15) // 10 + 1))
    # noch einmal: nichts doppelt
    assert lib.lpost('/api/kindle_notes', dict(path=root, key=b['key'], folder=folder, lang='de'))[1]['created'] == 0
    # nur gekaufte Bücher mit neuen Markierungen: keine Liste, aber der Hinweis
    root = kindle_ordner(tmp_path / 'b', rows=[('server_view', '%s-EBOK-CR!BBB-1' % SHOP, 'k1', note('HIGHLIGHT', 1, 2, MS), None)])
    code, r = lib.lpost('/api/kindle_scan', dict(path=root))
    assert code == 200 and r['books'] == [] and r['locked'] == [dict(title='Ein Roman: Spannend', n=1, why='drm')]
