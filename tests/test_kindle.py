"""Markierungen vom Kindle (#61): My Clippings.txt lesen, Zettel für Obsidian anlegen."""
import os, json
import kindle, finder
from conftest import make_book

# Ausgedachte Einträge im Format des Geräts: deutsch und englisch, mit BOM und CRLF wie auf dem Kindle
CLIPPINGS = '﻿' + '\r\n'.join([
    'Die Reise nach Rußland (Muster, Hans)',
    '- Ihre Markierung auf Seite 12 | bei Position 180-181 | Hinzugefügt am Montag, 3. März 2025 22:15:32',
    '',
    'Die Kolonisten zogen nach Osten.',
    '==========',
    '﻿Die Reise nach Rußland (Muster, Hans)',
    '- Ihre Markierung auf Seite 12 | bei Position 180-183 | Hinzugefügt am Montag, 3. März 2025 22:16:02',
    '',
    'Die Kolonisten zogen nach Osten. Der Weg war weit.',  # erweitert: der kürzere Eintrag davor fällt weg
    '==========',
    'Die Reise nach Rußland (Muster, Hans)',
    '- Ihre Notiz auf Seite 12 | bei Position 183 | Hinzugefügt am Montag, 3. März 2025 22:16:40',
    '',
    'Vgl. Stumpp, S. 40',
    '==========',
    'Die Reise nach Rußland (Muster, Hans)',
    '- Ihr Lesezeichen auf Seite 30 | bei Position 400 | Hinzugefügt am Dienstag, 4. März 2025 08:00:00',
    '',
    '',
    '==========',
    'Die Reise nach Rußland (Muster, Hans)',
    '- Ihre Markierung bei Position 90-91 | Hinzugefügt am Dienstag, 4. März 2025 08:01:00',
    '',
    'Vorwort des Herausgebers.',
    '==========',
    'Die Reise nach Rußland (Muster, Hans)',
    '- Ihre Notiz auf Seite 50 | bei Position 700 | Hinzugefügt am Dienstag, 4. März 2025 09:00:00',
    '',
    'Eigener Gedanke ohne Markierung.',
    '==========',
    'A Book (with Brackets) (Doe, Jane)',
    '- Your Highlight on page 5 | Location 60-62 | Added on Friday, 7 March 2025 10:00:00',
    '',
    'Call me Ishmael.',
    '==========',
    'A Book (with Brackets) (Doe, Jane)',
    '- Highlight Loc. 433-34 | Added on Friday, 7 March 2025 10:05:00',
    '',
    '<You have reached the clipping limit for this item>',
    '==========',
    ''])


def write(tmp_path, text=CLIPPINGS, name='My Clippings.txt'):
    p = tmp_path / name
    p.write_bytes(text.encode('utf-8'))
    return str(p)


def test_lesen_und_ordnen(tmp_path):
    e = kindle.read(write(tmp_path))
    assert [x['kind'] for x in e] == ['highlight', 'highlight', 'note', 'bookmark', 'highlight', 'note', 'highlight', 'highlight']
    assert (e[0]['book'], e[0]['author'], e[0]['page'], e[0]['loc']) == ('Die Reise nach Rußland', 'Muster, Hans', '12', (180, 181))
    assert (e[6]['book'], e[6]['author'], e[6]['loc']) == ('A Book (with Brackets)', 'Doe, Jane', (60, 62))
    assert e[7]['loc'] == (433, 434)  # ältere Geräte kürzen das Ende ab
    books = kindle.books(e)
    assert [(b['title'], b['highlights'], b['notes']) for b in books] == [('A Book (with Brackets)', 2, 0), ('Die Reise nach Rußland', 3, 2)]
    its, cut = kindle.items(e, books[1]['key'])
    assert cut == 0
    assert [(i['text'], i['note'], i['page'], i['loc']) for i in its] == [
        ('Vorwort des Herausgebers.', '', None, (90, 91)),
        ('Die Kolonisten zogen nach Osten. Der Weg war weit.', 'Vgl. Stumpp, S. 40', '12', (180, 183)),
        ('', 'Eigener Gedanke ohne Markierung.', '50', (700, 700))]
    its, cut = kindle.items(e, books[0]['key'])
    assert [i['text'] for i in its] == ['Call me Ishmael.'] and cut == 1


def test_zettel_anlegen_und_nicht_doppelt(lib, tmp_path):
    src, vault = write(tmp_path), tmp_path / 'Vault'
    os.makedirs(vault)
    code, r = lib.lpost('/api/kindle_scan', dict(path=src))
    assert code == 200 and r['path'] == src
    b = next(b for b in r['books'] if b['title'] == 'Die Reise nach Rußland')
    assert b['folder'] == ''  # noch kein Buch mit Notizordner: der Nutzer wählt
    folder = str(vault / 'Reise')
    code, r = lib.lpost('/api/kindle_notes', dict(path=src, key=b['key'], folder=folder, lang='de'))
    assert code == 200 and (r['created'], r['skipped'], r['cut']) == (3, 0, 0)
    names = sorted(os.listdir(folder))
    assert names == ['0 Quellenangabe.md', '01 Position 90–91.md', '02 Seite 12.md', '03 Seite 50.md']
    assert open(os.path.join(folder, '02 Seite 12.md'), encoding='utf-8').read() == (
        '**Anmerkung**\n\nVgl. Stumpp, S. 40\n\n---\n\n> Die Kolonisten zogen nach Osten. Der Weg war weit.\n\n'
        'Seite 12, Position 180–183, [[0 Quellenangabe|Die Reise nach Rußland]]\n')
    assert open(os.path.join(folder, '01 Position 90–91.md'), encoding='utf-8').read().startswith('**Anmerkung**\n\n\n\n---\n\n> Vorwort')
    assert 'Autor: Muster, Hans' in open(os.path.join(folder, '0 Quellenangabe.md'), encoding='utf-8').read()
    # Nach dem Weiterlesen dieselbe Datei noch einmal: nur das Neue kommt dazu, die Nummern laufen weiter
    more = CLIPPINGS + '\r\n'.join(['Die Reise nach Rußland (Muster, Hans)',
                                    '- Ihre Markierung auf Seite 60 | bei Position 800-801 | Hinzugefügt am Mittwoch, 5. März 2025 20:00:00',
                                    '', 'Ein neuer Satz.', '==========', ''])
    write(tmp_path, more)
    code, r = lib.lpost('/api/kindle_notes', dict(path=src, key=b['key'], folder=folder, lang='de'))
    assert (r['created'], r['skipped']) == (1, 3)
    assert '04 Seite 60.md' in os.listdir(folder)


def test_wiedererkennen_genau(lib, tmp_path):
    # Wiedererkannt wird am ganzen Zitat samt Stelle – auch in einem Ordner mit eckigen Klammern im Namen. Ein kurzes Zitat,
    # das wie ein längeres anfängt, ist neu; eine Notiz »Osten« ist neu, obwohl ein Zitat das Wort enthält; eine Notiz, die
    # erst nach dem Übernehmen auf dem Kindle entstand, kommt als eigener Zettel, ohne den alten zu verändern
    vault = tmp_path / 'Vault [Entwurf]'
    os.makedirs(vault)
    src, folder = write(tmp_path), str(vault / 'Reise')
    key = kindle.books(kindle.read(src))[1]['key']
    assert lib.lpost('/api/kindle_notes', dict(path=src, key=key, folder=folder))[1]['created'] == 3
    first = {n: open(os.path.join(folder, n), encoding='utf-8').read() for n in os.listdir(folder)}
    later = lambda meta, text: ['Die Reise nach Rußland (Muster, Hans)', meta, '', text, '==========']
    write(tmp_path, CLIPPINGS + '\r\n'.join(
        later('- Ihre Markierung auf Seite 90 | bei Position 5000-5000 | Hinzugefügt am Freitag, 7. März 2025 10:00:00', 'Die Kolonisten') +
        later('- Ihre Notiz auf Seite 91 | bei Position 5100 | Hinzugefügt am Freitag, 7. März 2025 10:01:00', 'Osten') +
        later('- Ihre Notiz bei Position 91 | Hinzugefügt am Freitag, 7. März 2025 10:02:00', 'Später dazu geschrieben.') + ['']))
    r = lib.lpost('/api/kindle_notes', dict(path=src, key=key, folder=folder))[1]
    assert (r['created'], r['skipped']) == (3, 2)
    assert open(os.path.join(folder, '04 Position 90–91.md'), encoding='utf-8').read() == (
        '**Anmerkung**\n\nSpäter dazu geschrieben.\n\n---\n\nPosition 90–91, [[0 Quellenangabe|Die Reise nach Rußland]]\n')
    assert all(open(os.path.join(folder, n), encoding='utf-8').read() == t for n, t in first.items())  # nichts verändert
    r = lib.lpost('/api/kindle_notes', dict(path=src, key=key, folder=folder))[1]
    assert (r['created'], r['skipped']) == (0, 5) and len(os.listdir(folder)) == 7


def test_keine_kindle_datei_und_ordner_als_datei(lib, tmp_path):
    import server
    # Eine Transkription mit unterstrichenem Titel oder eine Liste mit Spiegelstrichen ist keine Kindle-Datei
    for text in ('Die Reise nach Rußland\n----------------------\nDie Kolonisten zogen nach Osten.\n', 'Einkauf\n- Brot\n- Milch\n'):
        assert kindle.read(write(tmp_path, text, 'notiz.txt')) == [] and finder.scan(str(tmp_path / 'notiz.txt'))['found'] == []
    # Ist der Zielordner in Wahrheit eine Datei, sagt das Programm es, statt die Verbindung abzubrechen
    (tmp_path / 'Vault').mkdir()
    (tmp_path / 'Vault' / 'Reise').write_text('x')
    key = kindle.books(kindle.read(write(tmp_path)))[0]['key']
    assert lib.lpost('/api/kindle_notes', dict(path=write(tmp_path), key=key, folder=str(tmp_path / 'Vault' / 'Reise'))) == \
        (400, dict(error='kindle_schreiben'))
    # Gleicher Titel in jeder Schrift – zwei verschiedene kyrillische Titel sind nicht »gleich«
    assert server.same_title('Война и мир', 'война и мир!') and not server.same_title('Война и мир', 'Путешествие')
    assert not server.same_title('', '')


def test_vorschlag_ordner_und_fehler(lib, tmp_path):
    # Ein Buch der Bibliothek hat schon einen Notizordner: der Kindle-Zettel kommt daneben, ein gleichnamiges Buch direkt hinein
    make_book(str(tmp_path / 'Die Reise nach Rußland'))
    bid = lib.lpost('/api/open', dict(folder=str(tmp_path / 'Die Reise nach Rußland')))[1]['id']
    lib.lpost('/buch/%s/api/settings' % bid, dict(notizen=str(tmp_path / 'Vault' / 'Recherche' / 'Reise')))
    code, r = lib.lpost('/api/kindle_scan', dict(path=write(tmp_path)))
    f = {b['title']: b['folder'] for b in r['books']}
    assert f['Die Reise nach Rußland'] == str(tmp_path / 'Vault' / 'Recherche' / 'Reise')
    assert f['A Book (with Brackets)'] == str(tmp_path / 'Vault' / 'Recherche' / 'A Book (with Brackets)')
    assert lib.lpost('/api/kindle_scan', dict(path=str(tmp_path / 'fehlt.txt'))) == (400, dict(error='quelle_fehlt'))
    assert lib.lpost('/api/kindle_scan', dict(path=write(tmp_path, 'nur Text', 'andere.txt'))) == (400, dict(error='keine_markierungen'))
    key = r['books'][0]['key']
    assert lib.lpost('/api/kindle_notes', dict(path=write(tmp_path), key=key, folder=str(tmp_path / 'gibt' / 'es' / 'nicht'))) == \
        (400, dict(error='kindle_ordner_fehlt'))
    assert lib.lpost('/api/kindle_notes', dict(path=write(tmp_path), key=key, folder='')) == (400, dict(error='kindle_ordner_leer'))


def test_oeffnen_erkennt_die_datei(tmp_path):
    src = write(tmp_path, name='My Clippings (1).txt')  # umbenannt im Download-Ordner: am Inhalt erkannt
    f = finder.scan(src)['found']
    assert [(x['kind'], x['books'], x['highlights']) for x in f] == [('kindle', 2, 5)]
    os.makedirs(tmp_path / 'Kindle' / 'documents')
    write(tmp_path / 'Kindle' / 'documents')
    assert [x['kind'] for x in finder.scan(str(tmp_path / 'Kindle'))['found']] == ['kindle']
    assert finder.scan(write(tmp_path, 'Nur ein Brief.', 'brief.txt'))['found'] == []
