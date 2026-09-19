"""Einheitliches Öffnen: Erkennen, was eine Datei oder ein Ordner enthält; EPUB allein und EPUB + PDF."""
import os, time, zipfile
import pytest
import finder, epub
from conftest import make_book, png
from test_library import make_export
from test_ocr import make_searchable_pdf, wait

PARAS = ['Die Kolonisten zogen nach Rußland, und der Weg war weit.', 'Sie dachten an die Zukunft und an die Heimat, die sie verlassen hatten.',
         '„Wohin geht die Reise?“ fragte der Vater. Niemand wußte es genau, doch alle hofften auf ein besseres Leben.']


def make_epub(path, chapters, title='Probe-Epub'):
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('mimetype', 'application/epub+zip')
        z.writestr('META-INF/container.xml', '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>'
                   '<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
        items = ''.join('<item id="c%d" href="c%d.xhtml" media-type="application/xhtml+xml"/>' % (n, n) for n in range(len(chapters)))
        refs = ''.join('<itemref idref="c%d"/>' % n for n in range(len(chapters)))
        z.writestr('OEBPS/content.opf', '<package xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/"><metadata>'
                   '<dc:title>%s</dc:title></metadata><manifest>%s</manifest><spine>%s</spine></package>' % (title, items, refs))
        for n, paras in enumerate(chapters):
            z.writestr('OEBPS/c%d.xhtml' % n, '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>x</title><style>p{}</style></head><body>'
                       + ''.join('<p>%s</p>' % p for p in paras) + '</body></html>')


def test_gleichlautend():
    k = finder.stem_key
    assert k('Fatma - Immanuel Walker.epub') == k('Fatma - Immanuel Walker (durchsuchbar).pdf') == k('Fatma - Immanuel Walker (kompakt).pdf')
    assert k('Merkwuerdige_Reisebeschreibung_1818.epub') == k('Merkwuerdige_Reisebeschreibung_1818_OCR.pdf')
    assert k('Fatma.epub') != k('Fatima.pdf')


def test_ordner_untersuchen(tmp_path):
    fitz = pytest.importorskip('fitz')
    root = tmp_path / 'Mein Buch'
    make_book(str(root / 'ocr' / 'korr'))
    (root / 'ocr' / 'korr' / 'korrekturen.log').write_text('a\tedit\t001\t2\talt\tneu\nb\tedit\t001\t3\talt\tneu\n', encoding='utf-8')
    make_book(str(root / 'ocr' / 'korr_roh'))
    make_export(str(root / 'export.zip'), images=False)
    (root / 'bilder').mkdir()
    for n in range(2):
        (root / 'bilder' / ('s%d.png' % n)).write_bytes(png(10, 10))
    (root / 'bilder' / 's2.jpg').write_bytes(b'x')
    make_searchable_pdf(str(root / 'Probe (durchsuchbar).pdf'), fitz)
    make_epub(str(root / 'Probe.epub'), [PARAS])
    found = finder.scan(str(root))['found']
    assert [(f['kind'], f['name']) for f in found] == [
        ('book', 'Mein Buch – korr'), ('book', 'korr_roh'), ('transkribus', 'Probebuch 1818'), ('epub', 'Probe-Epub'),
        ('pdf', 'Probe (durchsuchbar)'), ('images', 'bilder')]
    b, _, t, e, p, i = found
    assert b['corrections'] == 2 and b['pages'] == 2           # wo schon Arbeit steckt, steht vorn
    assert t['pages'] == 2 and not t['images'] and 'images_dir' not in t  # 3 Bilder passen nicht zu 2 Seiten
    assert e['pdf'] == p['path'] and e['pdf_text'] and e['pages'] == 3 and p['text']
    assert i['pages'] == 3
    # Bilderordner mit genau so vielen Bildern wie Seiten: passt zum Export ohne Bilder
    os.remove(root / 'bilder' / 's2.jpg')
    t = [f for f in finder.scan(str(root))['found'] if f['kind'] == 'transkribus'][0]
    assert t['images_dir'] == str(root / 'bilder')


def test_nach_scantailor_zaehlt_nur_das_ergebnis(tmp_path):
    """ScanTailor legt in out/cache Miniaturbilder ab – das sind keine Buchseiten. Und liegt das Ergebnis vor,
    ist der Eingabeordner mit den unbearbeiteten Seiten keine Wahl mehr."""
    st = tmp_path / 'Buch' / 'scantailor'
    (st / 'out' / 'cache' / 'thumbs').mkdir(parents=True)
    for n in range(4):
        (st / ('seite_%03d.png' % n)).write_bytes(png(10, 10))                      # Eingabe für ScanTailor
    for n in range(8):
        (st / 'out' / ('seite_%03d.png' % n)).write_bytes(png(10, 10))              # aufbereitetes Ergebnis
        (st / 'out' / 'cache' / 'thumbs' / ('t%d.png' % n)).write_bytes(png(6, 6))  # Zwischenkram
    found = finder.scan(str(tmp_path))['found']
    assert [(f['kind'], f['pages'], f.get('scantailor')) for f in found] == [('images', 8, True)]


def test_datei_untersuchen(tmp_path):
    fitz = pytest.importorskip('fitz')
    make_book(str(tmp_path / 'b'))
    make_searchable_pdf(str(tmp_path / 'Probe_OCR.pdf'), fitz)
    make_epub(str(tmp_path / 'Probe.epub'), [PARAS])
    make_export(str(tmp_path / 'export.zip'))
    one = lambda p: [(f['kind'], f.get('pdf') and os.path.basename(f['pdf'])) for f in finder.scan(str(tmp_path / p))['found']]
    assert one('b/001.txt') == one('b/lines.json') == [('book', None)]
    assert one('Probe.epub') == [('epub', 'Probe_OCR.pdf')]
    assert one('Probe_OCR.pdf') == [('epub', 'Probe_OCR.pdf'), ('pdf', None)]  # das gleichlautende EPUB wird mit angeboten
    assert one('export.zip') == [('transkribus', None)]
    assert one('b/img/001.png') == [('images', None)]
    (tmp_path / 'brief.docx').write_bytes(b'x')
    assert one('brief.docx') == []
    with pytest.raises(ValueError):
        finder.scan(str(tmp_path / 'gibtsnicht'))


def test_epub_lesen_und_textbuch(tmp_path):
    make_epub(str(tmp_path / 'x.epub'), [PARAS, ['Zweites Kapitel.'] * 40], title='Mein Titel')
    title, chapters = epub.read(str(tmp_path / 'x.epub'))
    assert title == 'Mein Titel' and chapters[0] == PARAS and len(chapters[1]) == 40  # <head>/<style> zählen nicht zum Text
    r = epub.text_book(str(tmp_path / 'x.epub'), str(tmp_path / 'out'))
    assert r == dict(pages=4, title='Mein Titel')  # jedes Kapitel beginnt eine Seite, lange Kapitel werden geteilt
    lines = open(tmp_path / 'out' / '001.txt', encoding='utf-8').read().split('\n')
    assert lines[0] == '# ' and lines[1].startswith('Die Kolonisten') and max(map(len, lines)) <= 68


def test_epub_text_auf_pdf_zeilen(tmp_path):
    """Geometrie und Zeilenfall aus dem PDF, Wortlaut aus dem EPUB – auch über getrennte Wörter und Lücken hinweg."""
    book = tmp_path / 'buch'; book.mkdir()
    (book / '001.txt').write_text('\n'.join([
        '# — 7 —',
        '| Die Kolonisten zogen nach Rußlanb, unb ber Weg',      # OCR-Fehler, Randzeichen
        'war weit. Sie dachten an die Zu¬',
        'kunft und an bie Heimat, die sie ver¬',
        'lassen hallen. ·Wohin geht die Reise?· fragte',          # falsche Anführungszeichen
        'ber Vater. Niemand wußte es genau, doch alle',
        'hofften auf ein besseres Leben.',
        '---',
        '1) Vgl. die Quellen im Anhang des Buches.']) + '\n', encoding='utf-8')
    make_epub(str(tmp_path / 'x.epub'), [['Vorwort des Herausgebers, das im Buch nicht steht.'] * 30, PARAS])
    r = epub.transplant(str(tmp_path / 'x.epub'), str(book))
    lines = (book / '001.txt').read_text(encoding='utf-8').split('\n')[:-1]
    assert lines == ['# — 7 —',
                     'Die Kolonisten zogen nach Rußland, und der Weg',
                     'war weit. Sie dachten an die Zu¬',
                     'kunft und an die Heimat, die sie ver¬',
                     'lassen hatten. „Wohin geht die Reise?“ fragte',
                     'der Vater. Niemand wußte es genau, doch alle',
                     'hofften auf ein besseres Leben.',
                     '---',
                     '1) Vgl. die Quellen im Anhang des Buches.']   # Fußnote steht nicht im EPUB: bleibt
    assert r['matched'] == round(6 / 7, 3)


def test_epub_und_pdf_ueber_die_schnittstelle(lib, tmp_path):
    fitz = pytest.importorskip('fitz')
    make_searchable_pdf(str(tmp_path / 'Probe (durchsuchbar).pdf'), fitz)  # Text im PDF: "… Rußland, und der"
    make_epub(str(tmp_path / 'Probe.epub'), [[p.replace('Rußland', 'RUSSLAND') for p in PARAS]] * 3, title='Probe')
    f = lib.lpost('/api/scan', dict(path=str(tmp_path)))[1]['found'][0]
    assert f['kind'] == 'epub' and f['pdf_text']
    j = wait(lib, lib.lpost('/api/import_epub', dict(source=f['path'], pdf=f['pdf'], textlayer=True, target=str(tmp_path / 'ziel')))[1]['job'])
    assert j['state'] == 'done', j
    r = j['result']
    assert r['title'] == 'Probe' and r['pages'] == 3 and r['matched'] > 0.6 and r['quality']['conf'] is None
    page = lib.lget('/buch/%s/api/page/001' % r['id'])[1]
    assert 'RUSSLAND' in page['lines'][1] and page['img'].endswith('.jpg') and page['geo'][1]  # Wortlaut EPUB, Bild und Zeilen PDF
    # schon bekannte Bücher werden als solche erkannt
    b = lib.lpost('/api/scan', dict(path=str(tmp_path / 'ziel')))[1]['found'][0]
    assert b['kind'] == 'book' and b['known'] and b['id'] == r['id']
    # EPUB allein: Textbuch ohne Bilder
    j = wait(lib, lib.lpost('/api/import_epub', dict(source=f['path'], target=str(tmp_path / 'ziel2')))[1]['job'])
    assert j['state'] == 'done' and j['result']['pages'] == 3 and j['result']['quality'] is None
    assert lib.lget('/buch/%s/api/page/001' % j['result']['id'])[1]['img'] is None
    (tmp_path / 'kaputt.epub').write_bytes(b'kein zip')
    j = wait(lib, lib.lpost('/api/import_epub', dict(source=str(tmp_path / 'kaputt.epub')))[1]['job'])
    assert (j['state'], j['error']) == ('error', 'kein_epub')
    assert lib.lpost('/api/scan', dict(path=str(tmp_path / 'fehlt')))[0] == 400


def test_eben_eingelesenes_verwerfen(lib, tmp_path):
    """»Text neu erkennen lassen« ersetzt das eben Eingelesene – aber nie ein Buch, in dem schon Arbeit steckt."""
    fitz = pytest.importorskip('fitz')
    make_searchable_pdf(str(tmp_path / 'p.pdf'), fitz)
    r = wait(lib, lib.lpost('/api/import_ocr', dict(source=str(tmp_path / 'p.pdf'), textlayer=True, target=str(tmp_path / 'ziel')))[1]['job'])['result']
    lib.lpost('/buch/%s/api/bookmark' % r['id'], dict(page='002', line=1))       # nur geöffnet und geblättert: darf weg
    assert lib.lpost('/api/discard', dict(id=r['id']))[0] == 200
    assert lib.lget('/api/library')[1]['books'] == [] and not os.path.exists(tmp_path / 'ziel')
    r = wait(lib, lib.lpost('/api/import_ocr', dict(source=str(tmp_path / 'p.pdf'), textlayer=True, target=str(tmp_path / 'ziel')))[1]['job'])['result']
    lib.lpost('/buch/%s/api/whitelist' % r['id'], dict(word='Kolonisten'))        # hier steckt Arbeit: bleibt
    assert lib.lpost('/api/discard', dict(id=r['id'])) == (400, dict(error='hat_arbeit'))
    assert os.path.exists(tmp_path / 'ziel' / '001.txt')
    make_book(str(tmp_path / 'fremd'))                                           # nicht vom Programm eingelesen: bleibt
    bid = lib.lpost('/api/open', dict(folder=str(tmp_path / 'fremd')))[1]['id']
    assert lib.lpost('/api/discard', dict(id=bid))[0] == 400 and os.path.exists(tmp_path / 'fremd' / '001.txt')


def test_vorschlag_nach_erscheinungsjahr(lib, tmp_path):
    fitz = pytest.importorskip('fitz')
    d = fitz.open()
    for n, lines in enumerate([['Neue Wege', '© 2010 Verlag am Fluss'], ['Er sagte, dass der Fluss breit sei, und dass die Schifffahrt ruhe.'] * 3]):
        pg = d.new_page(width=420, height=595)
        for k, l in enumerate(lines):
            pg.insert_text((40, 80 + 22 * k), l, fontsize=11, fontname='tiro')
    d.save(str(tmp_path / 'neu.pdf')); d.close()
    r = wait(lib, lib.lpost('/api/import_ocr', dict(source=str(tmp_path / 'neu.pdf'), textlayer=True, target=str(tmp_path / 'ziel')))[1]['job'])['result']
    assert (r['year'], r['dics']) == (2010, ['1901', 'neu'])
    assert lib.lget('/buch/%s/api/settings' % r['id'])[1] == dict(year=2010, dics=['1901', 'neu'])
    assert lib.lget('/buch/%s/api/page/002' % r['id'])[1]['flags'] == []   # dass, Fluss, Schifffahrt: nichts rot
    assert r['quality']['level'] == 'gruen'                               # die Ampel hängt nicht an der Rechtschreibung


def test_vorschlag_wird_fuer_aeltere_importe_nachgeholt(tmp_path):
    """Bücher im Bücherordner des Programms, die noch keine buch.json haben (z. B. EPUB-Textbücher von früher)."""
    import json, server
    home = tmp_path / 'buecher'
    book = home / 'Neues Buch'; book.mkdir(parents=True)
    (book / '001.txt').write_text('# \nNeue Wege\n© 2010 Verlag am Fluss\n', encoding='utf-8')
    fremd = tmp_path / 'fremd'; fremd.mkdir()
    (fremd / '001.txt').write_text('# \n© 2010 Verlag am Fluss\n', encoding='utf-8')
    old = server.books_dir
    server.books_dir = lambda: str(home)
    try:
        assert server.Book(str(book)).settings == dict(year=2010, dics=['1901', 'neu'])
        assert json.load(open(book / 'buch.json', encoding='utf-8'))['year'] == 2010
        assert server.Book(str(fremd)).settings == dict(year=None, dics=['1901']) and not (fremd / 'buch.json').exists()  # von Hand angelegt: bleibt
    finally:
        server.books_dir = old
