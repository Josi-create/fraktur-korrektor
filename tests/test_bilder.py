"""Abbildungen und Tafeln (#76): Rahmen im Seitenbild (bilder.json), Bildunterschrift (<figcaption>), Vorschlag für den
Rahmen, Ausschnitte im E-Book – und dass die Rahmen mit dem PDF und beim Zusammenführen mitwandern."""
import os, json, zlib, struct
import xml.etree.ElementTree as ET
import pytest
from conftest import make_book
from test_server import words
from test_epubbuch import data, text, epub_files, epubcheck, MARK
from test_ocr import wait
import korrlib, epubbuch


def bild(w, h, dunkel=()):
    """Ein PNG in Graustufen: weiß, mit schwarzen Rechtecken (x0, y0, x1, y1)."""
    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d))
    rows = []
    for y in range(h):
        row = bytearray(b'\xff' * w)
        for x0, y0, x1, y1 in dunkel:
            if y0 <= y < y1:
                row[x0:x1] = bytes(x1 - x0)
        rows.append(b'\0' + bytes(row))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 0, 0, 0, 0)) + \
        chunk(b'IDAT', zlib.compress(b''.join(rows))) + chunk(b'IEND', b'')


def rahmen(x0, y0, x1, y1):
    return dict(x0=x0, y0=y0, x1=x1, y1=y1)


def zeilen(*ys):
    """Zeilenlage je Textzeile: 40 Pixel hoch ab y, None für eine Zeile ohne Lage."""
    return [None if y is None else dict(x0=100, x1=900, y0=y, y1=y + 40) for y in ys]


def job(lib, path, body):
    j = wait(lib, lib.lpost(path, body)[1]['job'])
    assert j['state'] == 'done', j
    return j['result']


# ---- Rahmen setzen und entfernen

def test_abbildung_markieren_und_entfernen(app):
    assert app.get('/api/page/001')[1]['bilder'] == []
    before = app.text('001'), open(os.path.join(app.folder, 'lines.json'), encoding='utf-8').read()
    # von rechts unten nach links oben aufgezogen und über den Rand hinaus: geordnet und auf das Seitenbild (500 × 750) begrenzt
    code, d = app.post('/api/bild/001', dict(kind='add', rect=dict(x0=440.4, y0=520, x1=60, y1=-5)))
    assert code == 200 and d['bilder'] == [rahmen(60, 0, 440, 520)] and d['lines'] == before[0]
    assert app.log()[-1][1:] == ['bild+', '001', '0', '', '60,0,440,520']
    assert json.load(open(os.path.join(app.folder, 'bilder.json'), encoding='utf-8')) == {'001': [rahmen(60, 0, 440, 520)]}
    # derselbe Rahmen noch einmal: nichts Neues, auch nicht im Protokoll
    n = len(app.log())
    assert app.post('/api/bild/001', dict(kind='add', rect=rahmen(60, 0, 440, 520)))[1]['bilder'] == d['bilder'] and len(app.log()) == n
    # eine zweite, weiter oben beginnende steht davor: von oben nach unten
    d = app.post('/api/bild/001', dict(kind='add', rect=rahmen(300, 600, 480, 700)))[1]
    assert d['bilder'] == [rahmen(60, 0, 440, 520), rahmen(300, 600, 480, 700)]
    # ein Klick statt eines Rahmens, Unsinn, eine Seite, die es nicht gibt
    assert app.post('/api/bild/001', dict(kind='add', rect=rahmen(100, 100, 103, 400)))[0] == 400
    assert app.post('/api/bild/001', dict(kind='add', rect='nix'))[0] == 400 and app.post('/api/bild/001', dict(kind='add'))[0] == 400
    assert app.post('/api/bild/009', dict(kind='add', rect=rahmen(60, 0, 440, 520)))[0] == 404
    # entfernen: nur ein Rahmen, den es so gibt – sonst sieht die Seite anders aus als im Browser
    assert app.post('/api/bild/001', dict(kind='delete', rect=rahmen(61, 0, 440, 520)))[0] == 409
    code, d = app.post('/api/bild/001', dict(kind='delete', rect=rahmen(60, 0, 440, 520)))
    assert code == 200 and d['bilder'] == [rahmen(300, 600, 480, 700)] and app.log()[-1][1:] == ['bild-', '001', '0', '60,0,440,520', '']
    assert app.post('/api/bild/001', dict(kind='delete', rect=rahmen(300, 600, 480, 700)))[1]['bilder'] == []
    # Text und Zeilenlage sind unberührt; die leere Datei bleibt stehen (im gesicherten PDF ersetzt sie den Stand davor)
    assert (app.text('001'), open(os.path.join(app.folder, 'lines.json'), encoding='utf-8').read()) == before
    assert json.load(open(os.path.join(app.folder, 'bilder.json'), encoding='utf-8')) == {}
    assert app.get('/api/page/002')[1]['bilder'] == []


def test_abbildung_ohne_seitenbild(app):
    os.remove(os.path.join(app.folder, 'img', '002.png'))
    assert app.post('/api/bild/002', dict(kind='add', rect=rahmen(60, 0, 440, 520)))[0] == 400
    assert app.get('/api/bildvorschlag/002')[1] == dict(rect=None) and app.get('/api/bildvorschlag/009')[0] == 404


# ---- Bildunterschrift

def test_bildunterschrift_auszeichnen():
    assert korrlib.caption('Abb. 1: Die Kolonie') == '<figcaption>Abb. 1: Die Kolonie</figcaption>'
    assert korrlib.caption('<p>Abb. <em>1</em>') == '<figcaption>Abb. <em>1</em></figcaption>'  # ein Block für sich: kein Absatzanfang
    assert korrlib.caption('<figcaption>Abb. 1</figcaption>') == 'Abb. 1' and korrlib.caption('  ') == '  '
    assert korrlib.mask('<figcaption>ber</figcaption>') == ' ' * 12 + 'ber' + ' ' * 13  # die Wortprüfung übergeht sie


def test_bildunterschrift_ueber_die_schnittstelle(app):
    t = app.text('001')
    code, d = app.post('/api/markup/001', dict(kind='caption', line=4, old=t[4]))
    assert code == 200 and d['lines'][4] == '<figcaption>ber Heimat gedachten.</figcaption>' and len(d['lines']) == len(t)
    assert words(d) == ['ber', 'baß', 'ber'] and d['flags'][-1]['start'] == len('<figcaption>')  # das rote Wort sitzt auf dem Wort
    assert None not in d['geo'][1:5] and app.log()[-1][1] == 'edit'
    # eine Bildunterschrift ist weder Absatzanfang noch Überschrift
    cap = d['lines'][4]
    assert app.post('/api/markup/001', dict(kind='para', line=4, old=cap))[0] == 400
    assert app.post('/api/markup/001', dict(kind='heading', line=4, level=1, old=cap))[0] == 400
    # und eine Überschrift, die Kopfzeile oder der Fußnotenstrich keine Bildunterschrift
    h = app.post('/api/markup/001', dict(kind='heading', line=1, level=2, old=t[1]))[1]['lines'][1]
    assert app.post('/api/markup/001', dict(kind='caption', line=1, old=h))[0] == 400
    assert app.post('/api/markup/001', dict(kind='caption', line=0, old=t[0]))[0] == 400
    assert app.post('/api/markup/001', dict(kind='caption', line=5, old='---'))[0] == 400
    assert app.post('/api/markup/001', dict(kind='caption', line=4, old='veraltet'))[0] == 409  # extern geändert
    # ein Absatzanfang fällt weg; noch einmal nimmt es zurück
    p = app.post('/api/markup/001', dict(kind='para', line=3, old=t[3]))[1]['lines'][3]
    assert app.post('/api/markup/001', dict(kind='caption', line=3, old=p))[1]['lines'][3] == '<figcaption>%s</figcaption>' % t[3]
    assert app.post('/api/markup/001', dict(kind='caption', line=4, old=cap))[1]['lines'][4] == t[4]


# ---- Vorschlag für den Rahmen

def test_vorschlag_bedruckte_flaeche_ohne_text(tmp_path):
    pytest.importorskip('fitz')
    import scans
    zeile1, zeile2, abb, schatten = (80, 100, 560, 112), (80, 130, 560, 142), (150, 300, 500, 650), (0, 0, 14, 900)
    p = tmp_path / 'seite.png'
    p.write_bytes(bild(640, 900, [zeile1, zeile2, abb, schatten]))
    r = scans.figure_box(str(p), [zeile1, zeile2])
    assert r and all(abs(a - b) <= 12 for a, b in zip(r, abb)), r  # der Schatten am Rand zählt nicht, die Textzeilen auch nicht
    assert scans.figure_box(str(p), [zeile1, zeile2, abb]) is None  # schon markiert: nichts mehr zu finden
    leer = tmp_path / 'leer.png'
    leer.write_bytes(bild(640, 900))
    assert scans.figure_box(str(leer)) is None
    fleck = tmp_path / 'fleck.png'
    fleck.write_bytes(bild(640, 900, [(300, 400, 312, 410)]))  # ein Fleck ist keine Abbildung
    assert scans.figure_box(str(fleck)) is None


def test_vorschlag_ueber_die_schnittstelle(app):
    pytest.importorskip('fitz')
    assert app.get('/api/bildvorschlag/001')[1] == dict(rect=None)  # eine weiße Seite
    # Seite 002 (500 × 750, halbe Größe der Zeilenlage): die Zeilen stehen bei y = 50–70 und 80–100, darunter ein Bild
    with open(os.path.join(app.folder, 'img', '002.png'), 'wb') as f:
        f.write(bild(500, 750, [(50, 50, 450, 70), (50, 80, 450, 100), (100, 300, 400, 600)]))
    r = app.get('/api/bildvorschlag/002')[1]['rect']
    assert r and all(abs(r[k] - v) <= 12 for k, v in rahmen(100, 300, 400, 600).items()), r
    assert app.post('/api/bild/002', dict(kind='add', rect=r))[0] == 200
    assert app.get('/api/bildvorschlag/002')[1] == dict(rect=None)  # die markierte Abbildung wird nicht noch einmal vorgeschlagen
    # Text ohne Zeilenlage: Der Vorschlag wäre der Text selbst – dann keiner
    app.post('/api/bild/002', dict(kind='delete', rect=r))
    geo = json.load(open(os.path.join(app.folder, 'lines.json'), encoding='utf-8'))
    del geo['002']
    json.dump(geo, open(os.path.join(app.folder, 'lines.json'), 'w', encoding='utf-8'))
    import server
    assert server.Book(app.folder).figure_guess('002') is None


# ---- E-Book

BUCH = {'001': ['# 5', '<p>Der erste Absatz beginnt hier und', 'geht unter dem Bild weiter.<sup>1</sup>', '<figcaption>Abb. 1: Die Ko¬</figcaption>',
                '<figcaption>lonie am <em>Schwarzen</em> Meer.</figcaption>', '<p>Zweiter Absatz.', '---', '1 Eine Fußnote.'],
        '002': ['# '],  # Tafel: nichts als das Bild
        '003': ['# 7', '<p>Dritter Absatz, der über', 'das Bild hinwegläuft.', '<p>Vierter.'],
        '004': ['# 8', '<figcaption>Kopfbild & Zier.</figcaption>', '<h1>Kapitel</h1>', 'Text.'],
        '005': ['<p>Fünfter.', '<figcaption>Lose Unterschrift.</figcaption>'],
        '006': ['# ']}  # leer oder eine Tafel, die noch niemand markiert hat
LABELS = {'001': '5', '002': '6', '003': '7', '004': '8', '005': None, '006': None}
FIGS = {'001': [rahmen(100, 160, 900, 580)], '002': [rahmen(0, 0, 1000, 1500)], '003': [rahmen(100, 160, 500, 280)],
        '004': [rahmen(300, 60, 700, 200)]}
GEO = {'001': zeilen(50, 100, 600, 660, 710, 800, None, 900), '002': zeilen(50), '003': zeilen(50, 100, 300, 360),
       '004': zeilen(20, 220, 300, 360)}


def test_abbildungen_im_fliesstext():
    r = epubbuch.build(data(BUCH, LABELS, figures=FIGS, geo=GEO, images={pg: 'scan.png' for pg in BUCH}))
    fn = '<sup><a class="nr" epub:type="noteref" role="doc-noteref" id="ref-001-1" href="#fn-001-1">1</a></sup>'
    assert r['files'][0][2] == '\n'.join([
        '<div class="seite">%s</div>' % (MARK % ('001', 5, 5)),
        '<p class="erst">Der erste Absatz beginnt hier und geht unter dem Bild weiter.%s</p>' % fn,
        # die Unterschrift gehört nicht zum Absatz; mit ihrer Abbildung steht sie hinter ihm, der Alternativtext ist ihr Wortlaut
        '<figure id="abb-001-1"><img src="bilder/abb-001-1.jpg" alt="Abb. 1: Die Kolonie am Schwarzen Meer."/>'
        '<figcaption>Abb. 1: Die Kolonie am <em>Schwarzen</em> Meer.</figcaption></figure>',
        '<p>Zweiter Absatz.</p>',
        '<aside class="fn" epub:type="footnote" role="doc-footnote" id="fn-001-1"><p><a class="nr" href="#ref-001-1">1</a> Eine Fußnote.</p></aside>',
        # die Tafel: hinter ihrer Seitenzahl, vor der nächsten
        '<div class="seite">%s</div>' % (MARK % ('002', 6, 6)),
        '<figure id="abb-002-1"><img src="bilder/abb-002-1.jpg" alt="Abbildung auf Seite 6"/></figure>',
        '<div class="seite">%s</div>' % (MARK % ('003', 7, 7)),
        # mitten im Absatz steht keine Abbildung: Sie folgt ihm
        '<p>Dritter Absatz, der über das Bild hinwegläuft.</p>',
        '<figure id="abb-003-1"><img src="bilder/abb-003-1.jpg" alt="Abbildung auf Seite 7"/></figure>',
        '<p>Vierter.</p>'])
    # die Abbildung über der Kapitelüberschrift gehört mit ihrer Seitenzahl zum neuen Kapitel
    assert r['files'][1][2] == '\n'.join([
        '<div class="seite">%s</div>' % (MARK % ('004', 8, 8)),
        '<figure id="abb-004-1"><img src="bilder/abb-004-1.jpg" alt="Kopfbild &amp; Zier."/><figcaption>Kopfbild &amp; Zier.</figcaption></figure>',
        '<h1 id="h-004-2">Kapitel</h1>',
        '<p class="erst">Text.</p>',
        '<p>Fünfter.</p>',
        '<p class="legende">Lose Unterschrift.</p>'])  # ohne Abbildung bleibt die Unterschrift ein Absatz für sich
    st = r['stats']
    assert (st['figures'], st['loose'], st['textless'], st['paragraphs']) == (4, 1, ['006'], 6)
    for name, title, body in r['files']:
        ET.fromstring(epubbuch._doc(title, body).split('\n', 2)[2])


def test_abbildung_ohne_zeilenlage_und_ohne_ausschnitt():
    # ohne Zeilenlage: am Ende der Seite, eine Unterschrift nimmt die Abbildungen der Reihe nach
    pages = {'001': ['<p>Eins.', '<figcaption>Erste.</figcaption>', '<p>Zwei.', '<figcaption>Zweite.</figcaption>', '<p>Drei.']}
    figs = {'001': [rahmen(0, 0, 100, 100), rahmen(0, 200, 100, 300), rahmen(0, 400, 100, 500)]}
    t = text(epubbuch.build(data(pages, figures=figs)))
    assert [x for x in t.split('\n') if not x.startswith('<p')] == [
        '<figure id="abb-001-1"><img src="bilder/abb-001-1.jpg" alt="Erste."/><figcaption>Erste.</figcaption></figure>',
        '<figure id="abb-001-2"><img src="bilder/abb-001-2.jpg" alt="Zweite."/><figcaption>Zweite.</figcaption></figure>',
        '<figure id="abb-001-3"><img src="bilder/abb-001-3.jpg" alt="Abbildung"/></figure>']
    assert t.endswith('<p>Drei.</p>\n' + '<figure id="abb-001-3"><img src="bilder/abb-001-3.jpg" alt="Abbildung"/></figure>')
    # ließ sich ein Ausschnitt nicht schneiden, fehlt die Abbildung – ihre Unterschrift bleibt
    r = epubbuch.build(data(pages, figures=figs, bildnamen={('001', 2): 'bilder/abb-001-2.png'}))
    assert '<p class="legende">Erste.</p>' in text(r) and '<img src="bilder/abb-001-2.png" alt="Zweite."/>' in text(r)
    assert 'abb-001-3' not in text(r) and (r['stats']['figures'], r['stats']['loose']) == (1, 1)


def test_epub_mit_abbildungen(tmp_path):
    fitz = pytest.importorskip('fitz')
    import server
    strich, foto = tmp_path / '001.png', tmp_path / '002.jpg'
    strich.write_bytes(bild(1000, 1500, [(200, 300, 800, 700)]))  # schwarzweißer Scan: als PNG kleiner
    gross = fitz.Pixmap(fitz.Pixmap(str(strich)), 2800, 4200)     # ein großer Scan: wird auf die Obergrenze verkleinert
    gross.save(str(foto), jpg_quality=80)
    d = data({pg: BUCH[pg] for pg in ('001', '002', '003')}, LABELS, figures={pg: FIGS[pg] for pg in ('001', '002', '003')},
             geo=GEO, images={'001': str(strich), '002': str(foto), '003': str(tmp_path / 'fehlt.png')}, kennung='0123456789abcdef0123456789abcdef')
    d['figures']['002'] = [rahmen(0, 0, 2800, 4200)]
    out = str(tmp_path / 'Probebuch.epub')
    r = epubbuch.write(d, out, '0.9')
    infos, files = epub_files(out)
    assert r['figures'] == 2 and {n for n in files if n.startswith('OEBPS/bilder/')} == {'OEBPS/bilder/abb-001-1.png', 'OEBPS/bilder/abb-002-1.jpg'}
    assert files['OEBPS/bilder/abb-001-1.png'][:8] == b'\x89PNG\r\n\x1a\n' and files['OEBPS/bilder/abb-002-1.jpg'][:2] == b'\xff\xd8'
    for name, size in (('abb-001-1.png', (800, 420)), ('abb-002-1.jpg', (1267, 1900))):  # der Ausschnitt; die Tafel höchstens 1400 × 1900
        (tmp_path / name).write_bytes(files['OEBPS/bilder/' + name])
        assert server.image_size(str(tmp_path / name)) == size
    opf = files['OEBPS/content.opf'].decode('utf-8')
    for s in ('<item id="abb-001-1" href="bilder/abb-001-1.png" media-type="image/png"/>', '<item id="abb-002-1" href="bilder/abb-002-1.jpg" media-type="image/jpeg"/>',
              '<meta property="schema:accessMode">visual</meta>', '<meta property="schema:accessModeSufficient">textual,visual</meta>'):
        assert s in opf, s
    body = files['OEBPS/text-001.xhtml'].decode('utf-8')
    ET.fromstring(body)
    assert '<img src="bilder/abb-001-1.png" alt="Abb. 1: Die Kolonie am Schwarzen Meer."/>' in body and '<img src="bilder/abb-002-1.jpg"' in body
    assert 'abb-003-1' not in body and 'abb-003' not in opf  # das Seitenbild fehlt: ohne diese Abbildung, das E-Book entsteht trotzdem
    assert 'figure img' in files['OEBPS/stil.css'].decode('utf-8')
    # ohne Abbildungen bleibt das Buch reiner Text
    ohne = str(tmp_path / 'Ohne.epub')
    epubbuch.write(data({'001': ['Text.']}), ohne)
    assert 'visual' not in epub_files(ohne)[1]['OEBPS/content.opf'].decode('utf-8')
    epubcheck(out)  # zuletzt: ohne epubcheck (außerhalb der CI) gilt der Test als übersprungen


def test_als_ebook_sichern_mit_abbildung(lib, tmp_path):
    """Der ganze Weg: Rahmen und Bildunterschrift im Reader, Vorschau im Dialog, E-Book – und das PDF daneben trägt die
    Rahmen im Arbeitsstand, ein daraus eingelesenes Buch hat sie wieder."""
    pytest.importorskip('fitz')
    folder = tmp_path / 'Probebuch'
    make_book(str(folder))
    (folder / '003.txt').write_text('# \n', encoding='utf-8')  # eine Tafel: nur das Bild
    (folder / 'img' / '003.png').write_bytes(bild(500, 750, [(100, 150, 400, 600)]))
    (folder / '004.txt').write_text('# \n', encoding='utf-8')  # eine leere Seite
    (folder / 'img' / '004.png').write_bytes(bild(500, 750))
    bid = lib.lpost('/api/open', dict(folder=str(folder)))[1]['id']
    b = '/buch/' + bid
    p = lib.lpost('/api/epub_preview', dict(id=bid))[1]
    assert (p['figures'], p['loose'], p['textless']) == (0, 0, ['003'])  # die Tafel wird genannt, die leere Seite nicht
    assert lib.lpost(b + '/api/bild/003', dict(kind='add', rect=rahmen(0, 0, 500, 750)))[0] == 200
    assert lib.lpost(b + '/api/bild/001', dict(kind='add', rect=rahmen(60, 150, 440, 240)))[0] == 200
    assert lib.lpost(b + '/api/markup/001', dict(kind='caption', line=4, old='ber Heimat gedachten.'))[0] == 200
    p = lib.lpost('/api/epub_preview', dict(id=bid))[1]
    assert (p['figures'], p['loose'], p['textless']) == (2, 0, [])
    r = job(lib, '/api/export_epub', dict(id=bid, target=str(tmp_path), pdf=True))
    assert r['figures'] == 2
    files = epub_files(r['file'])[1]
    body = files['OEBPS/text-001.xhtml'].decode('utf-8')
    assert '<img src="bilder/abb-001-1.png" alt="ber Heimat gedachten."/><figcaption>ber Heimat gedachten.</figcaption></figure>' in body
    assert '<figure id="abb-003-1"><img src="bilder/abb-003-1.png" alt="Abbildung"/></figure>' in body
    # das PDF daneben: ein daraus eingelesenes Buch kennt die Rahmen
    neu = job(lib, '/api/import_pdfbuch', dict(source=r['pdf']['file'], target=str(tmp_path / 'laptop')))['id']
    assert lib.lget('/buch/%s/api/page/003' % neu)[1]['bilder'] == [rahmen(0, 0, 500, 750)]
    assert lib.lget('/buch/%s/api/page/001' % neu)[1]['bilder'] == [rahmen(60, 150, 440, 240)]
    epubcheck(r['file'])  # zuletzt, siehe oben


# ---- Zusammenführen (#66), Kopie, ersetzte Seite

def test_rahmen_beim_zusammenfuehren(lib, tmp_path):
    pytest.importorskip('fitz')
    make_book(str(tmp_path / 'Probebuch'))
    pc = lib.lpost('/api/open', dict(folder=str(tmp_path / 'Probebuch')))[1]['id']
    a, b, c = rahmen(60, 150, 440, 240), rahmen(60, 300, 440, 500), rahmen(100, 400, 400, 700)
    lib.lpost('/buch/%s/api/bild/001' % pc, dict(kind='add', rect=a))
    pdf = job(lib, '/api/export_pdf', dict(id=pc, target=str(tmp_path)))['file']
    lap = job(lib, '/api/import_pdfbuch', dict(source=pdf, target=str(tmp_path / 'laptop')))['id']
    # am Laptop: der erste Rahmen weg, zwei neue; am PC inzwischen derselbe neue Rahmen auf Seite 002 und eine Korrektur
    lib.lpost('/buch/%s/api/bild/001' % lap, dict(kind='delete', rect=a))
    lib.lpost('/buch/%s/api/bild/001' % lap, dict(kind='add', rect=b))
    lib.lpost('/buch/%s/api/bild/002' % lap, dict(kind='add', rect=c))
    (tmp_path / 'stick').mkdir()
    pdf2 = job(lib, '/api/export_pdf', dict(id=lap, target=str(tmp_path / 'stick')))['file']
    lib.lpost('/api/forget', dict(id=lap))
    lib.lpost('/buch/%s/api/bild/002' % pc, dict(kind='add', rect=c))
    lib.lpost('/buch/%s/api/edit/002' % pc, dict(edits=[dict(line=1, old='Der Vater und ber Sohn.', new='Der Vater und der Sohn.')]))
    r = job(lib, '/api/import_pdfbuch', dict(source=pdf2, into=pc, merge=True))
    # der Rahmen, den beide gesetzt haben, ist dieselbe Änderung – in derselben Sekunde sogar derselbe Protokolleintrag
    assert r['merged']['conflicts'] == 0 and r['merged']['applied'] == 2 and r['merged']['already'] in (0, 1)
    assert lib.lget('/buch/%s/api/page/001' % pc)[1]['bilder'] == [b] and lib.lget('/buch/%s/api/page/002' % pc)[1]['bilder'] == [c]
    # das Protokoll enthält jetzt alles, was das PDF enthält: Beim nächsten Wechsel genügt wieder das Ersetzen
    assert lib.lpost('/api/scan', dict(path=pdf2))[1]['found'][0]['update']['there'] == 0


def test_rahmen_einer_ersetzten_seite_verfallen(tmp_path, monkeypatch):
    import server
    monkeypatch.setattr(server, 'books_dir', lambda: str(tmp_path / 'buecher'))  # die Kopie nicht nach ~/Fraktur-Korrektor
    folder = str(tmp_path / 'buch')
    make_book(folder)
    book = server.Book(folder)
    assert book.figure('001', rahmen(60, 150, 440, 240))[0] and book.figure('002', rahmen(60, 150, 440, 240))[0]
    book.drop_figures('001')  # ihr Bild wurde ersetzt (#52): Die Bildpixel sind andere
    assert book.figures() == {'002': [rahmen(60, 150, 440, 240)]}
    rows = [l.split('\t') for l in open(book.klogpath, encoding='utf-8').read().splitlines()]
    assert [r[1:3] for r in rows] == [['bild+', '001'], ['bild+', '002'], ['bild-', '001']]
    # die Kopie eines Buchs (neuer Text aus Transkribus daneben) nimmt die Rahmen mit: Die Seitenbilder sind dieselben
    out = server.copy_book(folder, 'Kopie')
    assert server.Book(out).figures() == book.figures()
