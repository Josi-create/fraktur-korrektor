"""Ein Buch als E-Book sichern (#59): Fließtext, Kapitel und Inhaltsverzeichnis aus den Überschriften, Seitenzahlen der
Druckausgabe, Fußnoten als Links, das PDF daneben – und beim Öffnen des EPUB die Empfehlung, das PDF zu nehmen."""
import os, re, json, shutil, zipfile, subprocess
import xml.etree.ElementTree as ET
import pytest
from conftest import ROOT, make_book, png
from test_ocr import wait
import epubbuch, korrlib

MARK = '<span class="seite" epub:type="pagebreak" role="doc-pagebreak" id="seite-%s" aria-label="%s">[%s]</span>'


def data(pages, labels=None, **kw):
    return dict(dict(pages=pages, labels=labels or {pg: None for pg in pages}, foot={}, kopf={}, title='Probebuch'), **kw)


def text(r):
    return '\n'.join(body for name, title, body in r['files'])


def noteref(pg, k, shown):
    return '<sup><a class="nr" epub:type="noteref" role="doc-noteref" id="ref-%s-%d" href="#fn-%s-%d">%s</a></sup>' % (pg, k, pg, k, shown)


def test_fliesstext_absaetze_und_seitenmarken():
    pages = {'001': ['# 5', 'Stalins Bauernopfer 5', 'Die Kolonisten zogen nach Ruß¬', 'land und der Weg war weit.', '<p>Die Zu¬'],
             '002': ['# ', 'kunft lag vor ihnen, das Staats-', 'Archiv und das Umwelt-', 'und Heimatrecht.', '<p>Der Vater.', '6', 'i ~'],
             '003': ['# '],  # Tafel ohne Text: nur die Seitenmarke
             '004': ['# 8', '<p>Der Sohn.']}
    r = epubbuch.build(data(pages, {'001': '5', '002': '6', '003': '7', '004': '8'}, foot={'002': 5}, kopf={'001': {1}}))
    t = text(r)
    assert t == '\n'.join([
        '<div class="seite">%s</div>' % (MARK % ('001', 5, 5)),
        '<p class="erst">Die Kolonisten zogen nach Rußland und der Weg war weit.</p>',
        # das getrennte Wort über die Seitengrenze: die Marke hinter seiner zweiten Hälfte
        '<p>Die Zukunft%s lag vor ihnen, das Staats-Archiv und das Umwelt- und Heimatrecht.</p>' % (MARK % ('002', 6, 6)),
        '<p>Der Vater.</p>',
        '<div class="seite">%s</div>' % (MARK % ('003', 7, 7)),
        '<div class="seite">%s</div>' % (MARK % ('004', 8, 8)),
        '<p>Der Sohn.</p>'])  # Kolumnentitel, Kopfzeile, Seitenzahl unten und das Rauschen darunter fehlen
    assert r['pagelist'] == [('5', 'text-001.xhtml#seite-001'), ('6', 'text-001.xhtml#seite-002'), ('7', 'text-001.xhtml#seite-003'),
                             ('8', 'text-001.xhtml#seite-004')]
    assert r['stats'] == dict(paragraphs=4, headings=0, pages=4, files=1, notes=0, linked=0, marked=4, fallback=False)
    # ohne bekannte Seitenzahl keine Marke – eine erfundene wäre schlimmer als keine
    r = epubbuch.build(data(pages, {'001': '5', '002': None, '003': None, '004': '8'}))
    assert 'seite-002' not in text(r) and r['stats']['marked'] == 2


def test_kapitel_und_inhaltsverzeichnis():
    pages = {'001': ['<h1>Erstes Kapitel.</h1>', '<h1>Die Reise nach Odes¬</h1>', '<h1>sa.</h1>', 'Text eins.'],
             '002': ['# 2', '<h3>Unterabschnitt</h3>', 'Text zwei.', '<h1>Zweites Kapitel</h1>', 'Text drei.']}
    r = epubbuch.build(data(pages, {'001': None, '002': '2'}))
    assert [f[0] for f in r['files']] == ['text-001.xhtml', 'text-002.xhtml']  # jedes Kapitel der obersten Stufe eine Datei
    assert '<h1 id="h-001-0">Erstes Kapitel.<br/>Die Reise nach Odessa.</h1>' in r['files'][0][2]
    assert r['files'][0][1] == 'Erstes Kapitel. Die Reise nach Odessa.' and r['files'][1][1] == 'Zweites Kapitel'
    assert r['files'][1][2].startswith('<h1 id="h-002-3">Zweites Kapitel</h1>\n<p class="erst">Text drei.</p>')
    # dieselben Einträge wie die Übersicht I und die Lesezeichen des PDFs, die Tiefe ohne übersprungene Ebene
    assert [(d, e['text'], e['href'], e['page']) for d, e in r['toc']] == [
        (1, 'Erstes Kapitel. Die Reise nach Odessa.', 'text-001.xhtml#h-001-0', None),
        (2, 'Unterabschnitt', 'text-001.xhtml#h-002-1', '2'), (1, 'Zweites Kapitel', 'text-002.xhtml#h-002-3', '2')]
    assert [tx for pg, i, lv, tx in korrlib.headings(pages)] == [e['text'] for d, e in r['toc']]
    assert epubbuch.depths([2, 2, 3, 1, 3, 6]) == [1, 1, 2, 1, 2, 3]
    inhalt = epubbuch._inhalt('Probebuch', r['toc'])
    assert ('<li><a href="text-001.xhtml#h-001-0">Erstes Kapitel. Die Reise nach Odessa.</a><ol><li><a href="text-001.xhtml#h-002-1">'
            'Unterabschnitt</a> <span class="s">2</span></li></ol></li>') in inhalt


def test_ohne_ueberschriften_nach_groesse_geteilt(monkeypatch):
    monkeypatch.setattr(epubbuch, 'GROSS', 200)
    pages = {'%03d' % n: ['<p>Absatz auf Seite %d mit etwas Text, damit die Datei wächst.' % n] for n in range(1, 11)}
    r = epubbuch.build(data(pages))
    assert len(r['files']) > 2 and all(b.startswith('<p') for n, t, b in r['files'])


def test_fussnoten_werden_links():
    pages = {'001': ['# 7', 'Er kam an<sup>1</sup> und ging 2) wieder, sagte er*. Vgl. S. 12) und (siehe 3)',
                     'und Teil 4), dann weiter¬', '---', '1 Erste Note.', '2) Zweite Note, die weiter¬', 'geht.', '* Stern.',
                     '3) Ohne Verweis, die auf der nächsten Seite', '4) Vierte.', '5) Noch eine, die'],
             '002': ['# 8', 'geht.', '---', 'weitergeht.', '6) Sechste.']}
    r = epubbuch.build(data(pages))
    t = text(r)
    assert ('<p class="erst">Er kam an%s und ging%s wieder, sagte er%s. Vgl. S. 12) und (siehe 3) und Teil%s, dann weitergeht.</p>'
            % (noteref('001', 1, '1'), noteref('001', 2, '2)'), noteref('001', 3, '*'), noteref('001', 5, '4)'))) in t
    # verknüpft: EPUB-Fußnote mit Rücksprung; ohne Verweis: sichtbar, damit nichts verloren geht – auch über die Seite hinweg
    assert '<aside class="fn" epub:type="footnote" role="doc-footnote" id="fn-001-1"><p><a class="nr" href="#ref-001-1">1</a> Erste Note.</p></aside>' in t
    assert '<p><a class="nr" href="#ref-001-2">2)</a> Zweite Note, die weitergeht.</p>' in t
    assert '<div class="fn" id="fn-001-4"><p>3) Ohne Verweis, die auf der nächsten Seite</p></div>' in t
    assert '<div class="fn" id="fn-001-6"><p>5) Noch eine, die weitergeht.</p></div>' in t
    assert '<div class="fn" id="fn-002-1"><p>6) Sechste.</p></div>' in t
    assert t.index('id="fn-001-1"') > t.index('dann weitergeht.</p>')  # hinter dem Absatz, in dem die Seite endet
    assert (r['stats']['notes'], r['stats']['linked']) == (7, 4)


def test_fussnoten_folgezeilen_und_zaehlung():
    """Eine Zahl beginnt nur eine neue Fußnote, wenn sie zur Zählung passt; »*)« im Text bei nummerierten Fußnoten ist oft
    eine falsch gelesene »1)«; in einem fortlaufend gezählten Buch ist »2 Bde.« oben im Fußnotenblock eine Folgezeile."""
    pages = {'001': ['Text*) und mehr 2).', '---', '1) Anfang, zitiert nach', '12 Pferde und Wagen.', '2) Zweite.'],
             '002': ['Text 3) und 4).', '---', '3) Dritte.', '4) Vierte.'],
             '003': ['Text 5).', '---', '5) Fünfte, zitiert nach'],
             '004': ['Text 6).', '---', '2 Bde., Stuttgart 1850.', '6) Sechste.']}
    f = epubbuch._Flow(pages, {pg: None for pg in pages}, {}, {})
    f.run()
    assert [(x['id'], x['mark'], x['text'], bool(x['ref'])) for v in f.notes.values() for x in v] == [
        ('fn-001-1', '1)', 'Anfang, zitiert nach 12 Pferde und Wagen.', True), ('fn-001-2', '2)', 'Zweite.', True),
        ('fn-002-1', '3)', 'Dritte.', True), ('fn-002-2', '4)', 'Vierte.', True),
        ('fn-003-1', '5)', 'Fünfte, zitiert nach 2 Bde., Stuttgart 1850.', True), ('fn-004-1', '6)', 'Sechste.', True)]


def test_fussnoten_hinter_zahlen_und_ohne_vorgaenger():
    """»von 1815 1)« und »(1752) aus 3)« sind Fußnotenzeichen; »4)« passt auch zu »4 …« unten. Eine Nummer oben im
    Fußnotenblock, vor der nichts weiterlaufen kann, beginnt eine Fußnote, auch wenn sie nicht zur Zählung passt."""
    pages = {'001': ['Verlust von 1815 11): und 1819/20 12). Das Jahr (1752) aus 13), Einstellung 14) zeigt 15).', '---',
                     '11) Elf.', '12) Zwölf.', '13) Dreizehn.', '14 Vierzehn.', '15) Fünfzehn.'],
             '002': ['Ohne Fußnoten.'],
             '003': ['Neue Zählung 2).', '---', '2) Zwei, neu gezählt.']}  # fortlaufend gezählt: 2 passt nicht zu 15
    f = epubbuch._Flow(pages, {pg: None for pg in pages}, {}, {})
    f.run()
    assert [(x['mark'], x['text'], bool(x['ref'])) for v in f.notes.values() for x in v] == [
        ('11)', 'Elf.', True), ('12)', 'Zwölf.', True), ('13)', 'Dreizehn.', True), ('14', 'Vierzehn.', True),
        ('15)', 'Fünfzehn.', True), ('2)', 'Zwei, neu gezählt.', True)]


def test_tabelle_und_auszeichnung_wohlgeformt():
    rows = korrlib.make_table(['Ort', 'Familien', 'Rohrbach', '32'], 2, head=True)
    pages = {'001': ['<p>Ein <em>betontes Wort ohne Ende & ein <b>fettes</em> Wort</b>, 3 < 4.'] + rows + ['Danach.'],
             '002': ['<p><tr><td>verdorben</td>', '<table><td>ohne Reihe</td></table>', '</em>Schluss.']}
    r = epubbuch.build(data(pages))
    t = text(r)
    assert '<p class="erst">Ein <em>betontes Wort ohne Ende &amp; ein <b>fettes</b></em> Wort, 3 &lt; 4.</p>' in t
    assert '<table><tr><th>Ort</th><th>Familien</th></tr><tr><td>Rohrbach</td><td>32</td></tr></table>\n<p class="erst">Danach.</p>' in t
    assert '<p>verdorben</p>\n<table><tr><td>ohne Reihe</td></tr></table>\n<p class="erst">Schluss.</p>' in t
    for name, title, body in r['files']:
        ET.fromstring(epubbuch._doc(title, body).split('\n', 2)[2])  # wohlgeformt: Lese-Apps zeigen sonst nichts an


def test_ohne_absatzmarken():
    """Buch ohne <p>: Absatz nach einer kurzen Zeile mit Satzzeichen am Ende, und an Leerzeilen (Textbuch aus einem EPUB)."""
    pages = {'001': ['Eine lange Zeile, die im Druck bis zum Rand', 'reicht und weitergeht, bis der Satz zu Ende.',
                     'Ist. Dann kommt eine neue Zeile, die lang ist', 'und kurz endet.', 'Nächster Absatz nach Rand,', '',
                     'nach einer Leerzeile.']}
    r = epubbuch.build(data(pages))
    assert r['stats']['fallback'] and re.findall(r'<p[^>]*>(.*?)</p>', text(r)) == [
        'Eine lange Zeile, die im Druck bis zum Rand reicht und weitergeht, bis der Satz zu Ende. Ist. Dann kommt eine neue '
        'Zeile, die lang ist und kurz endet.', 'Nächster Absatz nach Rand,', 'nach einer Leerzeile.']


def epub_files(path):
    with zipfile.ZipFile(path) as z:
        return z.infolist(), {n: z.read(n) for n in z.namelist()}


def sample(tmp_path):
    img = tmp_path / '001.png'
    img.write_bytes(png(300, 450))
    pages = {'001': ['# 5', '<h2>Vorwort</h2>', 'Der Text<sup>1</sup> beginnt.', '---', '1 Eine Fußnote.'],
             '002': ['# 6', '<h2>Erstes Kapitel</h2>', '<h3>Die Reise</h3>', '<p>Weiter & fort.']}
    return data(pages, {'001': '5', '002': '6'}, author='Georg Leibbrandt', year=1928, kennung='0123456789abcdef0123456789abcdef',
                cover=str(img))


def test_aufbau_des_epub(tmp_path):
    out = str(tmp_path / 'Probebuch.epub')
    r = epubbuch.write(sample(tmp_path), out, '0.9')
    assert r['file'] == out and r['cover'] and r['files'] == 2 and not os.path.exists(out + '.tmp')
    infos, files = epub_files(out)
    assert infos[0].filename == 'mimetype' and infos[0].compress_type == zipfile.ZIP_STORED and files['mimetype'] == b'application/epub+zip'
    assert set(files) == {'mimetype', 'META-INF/container.xml', 'OEBPS/content.opf', 'OEBPS/nav.xhtml', 'OEBPS/toc.ncx', 'OEBPS/stil.css',
                          'OEBPS/titel.xhtml', 'OEBPS/inhalt.xhtml', 'OEBPS/text-001.xhtml', 'OEBPS/text-002.xhtml', 'OEBPS/umschlag.jpg'}
    for n, b in files.items():
        if n.endswith(('.xhtml', '.opf', '.ncx', '.xml')):
            ET.fromstring(b)
    opf = files['OEBPS/content.opf'].decode('utf-8')
    for s in ('<dc:identifier id="uid">urn:uuid:01234567-89ab-cdef-0123-456789abcdef</dc:identifier>', '<dc:title>Probebuch</dc:title>',
              '<dc:creator>Georg Leibbrandt</dc:creator>', '<dc:language>de</dc:language>', 'properties="cover-image"',
              '<meta property="schema:accessibilityFeature">printPageNumbers</meta>', '<meta property="pageBreakSource">Druckausgabe 1928</meta>',
              '<itemref idref="titel"/>\n<itemref idref="inhalt"/>\n<itemref idref="text-001"/>\n<itemref idref="text-002"/>',
              'properties="nav"', 'Fraktur-Korrektor 0.9'):
        assert s in opf, s
    assert '<itemref idref="nav"' not in opf  # das Verzeichnis für die Lese-App, sichtbar ist die Seite »Inhalt«
    nav = files['OEBPS/nav.xhtml'].decode('utf-8')
    assert '<li><a href="text-001.xhtml#h-001-1">Vorwort</a></li><li><a href="text-002.xhtml#h-002-1">Erstes Kapitel</a><ol>' in nav
    assert '<nav epub:type="page-list" id="seiten" hidden="hidden"><h1>Seiten</h1><ol><li><a href="text-001.xhtml#seite-001">5</a></li>' in nav
    assert 'epub:type="landmarks"' in nav and 'navPoint' in files['OEBPS/toc.ncx'].decode('utf-8')
    titel = files['OEBPS/titel.xhtml'].decode('utf-8')
    assert '<h1>Probebuch</h1>' in titel and 'Georg Leibbrandt' in titel and '1928' in titel
    assert files['OEBPS/umschlag.jpg'][:2] == b'\xff\xd8'
    assert '<p class="erst">Weiter &amp; fort.</p>' in files['OEBPS/text-002.xhtml'].decode('utf-8')
    assert epubbuch.kennung(out) == '0123456789abcdef0123456789abcdef'
    # beim Einlesen als Textbuch (EPUB ohne PDF) gehören die Seitenmarken nicht zum Text
    import epub
    title, chapters = epub.read(out)
    assert title == 'Probebuch' and not any('[5]' in p or '[6]' in p for c in chapters for p in c)
    assert any('Der Text1 beginnt.' in p for c in chapters for p in c)


def epubcheck(path):
    """epubcheck, wenn EPUBCHECK auf das JAR zeigt (in der CI unter Linux; Java aus JAVA oder dem Pfad) – sonst übersprungen."""
    jar = os.environ.get('EPUBCHECK')
    if not jar or not os.path.isfile(jar):
        pytest.skip('epubcheck nicht eingerichtet (Umgebungsvariable EPUBCHECK)')
    p = subprocess.run([os.environ.get('JAVA') or 'java', '-jar', jar, '-q', path], capture_output=True, text=True, encoding='utf-8', errors='replace')
    assert p.returncode == 0, p.stdout + p.stderr


def test_epubcheck_probe(tmp_path):
    out = str(tmp_path / 'Probebuch.epub')
    epubbuch.write(sample(tmp_path), out, '0.9')
    epubcheck(out)


def test_beispielbuch_als_epub(tmp_path):
    """Das mitgelieferte Beispielbuch (Goethes Faust, acht Seiten) – so, wie es der Server liest."""
    import server
    folder = str(tmp_path / 'beispiel')
    shutil.copytree(os.path.join(ROOT, 'beispiel'), folder, ignore=shutil.ignore_patterns('korrekturen.log', 'lesezeichen.json', 'whitelist.txt'))
    out = str(tmp_path / 'Faust.epub')
    r = epubbuch.save(server.Book(folder, 'Faust'), out, '0.9')
    assert r['pages'] == 8 and r['cover'] and r['paragraphs'] > 5
    epubcheck(out)


def job(lib, path, body):
    j = wait(lib, lib.lpost(path, body)[1]['job'])
    assert j['state'] == 'done', j
    return j['result']


def test_als_ebook_sichern_mit_pdf_daneben(lib, tmp_path):
    fitz = pytest.importorskip('fitz')
    import pdfbuch
    make_book(str(tmp_path / 'Probebuch'))
    bid = lib.lpost('/api/open', dict(folder=str(tmp_path / 'Probebuch')))[1]['id']
    b = '/buch/' + bid
    lib.lpost(b + '/api/markup/001', dict(kind='heading', line=1, old='Die Kolonisten zogen nach Rußland und', level=2))
    p = lib.lpost('/api/epub_preview', dict(id=bid))[1]
    assert (p['pages'], p['headings'], p['notes'], p['marked'], p['autor'], p['title']) == (2, 1, 1, 2, '', 'Probebuch')
    assert lib.lpost('/api/epub_preview', dict(id='00000000'))[0] == 400

    # der Zielordner so, wie ihn der Dateidialog unter Windows liefert (»C:/…«): Pfade im Ergebnis sind die des Systems
    r = job(lib, '/api/export_epub', dict(id=bid, target=str(tmp_path).replace(os.sep, '/'), autor='  Georg   Leibbrandt ', pdf=True))
    epub_, pdf = str(tmp_path / 'Probebuch.epub'), str(tmp_path / 'Probebuch.pdf')
    assert r['file'] == epub_ and r['pdf']['file'] == pdf and r['folder'] == str(tmp_path) and r['pages'] == 2
    st = json.load(open(tmp_path / 'Probebuch' / 'buch.json', encoding='utf-8'))
    assert st['autor'] == 'Georg Leibbrandt' and epubbuch.kennung(epub_) == st['kennung'] == pdfbuch.info(pdf)['kennung']
    assert [x['autor'] for x in lib.lget('/api/library')[1]['books']] == ['Georg Leibbrandt']
    with fitz.open(pdf) as d:
        assert d.metadata['author'] == 'Georg Leibbrandt'
    opf = epub_files(epub_)[1]['OEBPS/content.opf'].decode('utf-8')
    assert '<dc:creator>Georg Leibbrandt</dc:creator>' in opf

    # noch einmal: ersetzt die eigenen Dateien; ohne autor bleibt der gemerkte
    r = job(lib, '/api/export_epub', dict(id=bid, target=str(tmp_path), pdf=True))
    assert (r['file'], r['pdf']['file']) == (epub_, pdf) and json.load(open(tmp_path / 'Probebuch' / 'buch.json', encoding='utf-8'))['autor'] == 'Georg Leibbrandt'
    # eine fremde Datei gleichen Namens: beide bekommen »(2)«, damit sie weiter zusammengehören
    os.remove(epub_)
    (tmp_path / 'Probebuch.epub').write_bytes(b'PK fremd')
    r = job(lib, '/api/export_epub', dict(id=bid, target=str(tmp_path), autor='', pdf=True))
    assert (r['file'], r['pdf']['file']) == (str(tmp_path / 'Probebuch (2).epub'), str(tmp_path / 'Probebuch (2).pdf'))
    assert json.load(open(tmp_path / 'Probebuch' / 'buch.json', encoding='utf-8'))['autor'] is None
    assert open(epub_, 'rb').read() == b'PK fremd'
    # nur das EPUB
    r = job(lib, '/api/export_epub', dict(id=bid, target=str(tmp_path / 'Probebuch')))
    assert r['file'] == str(tmp_path / 'Probebuch' / 'Probebuch.epub') and 'pdf' not in r
    assert not os.path.exists(str(tmp_path / 'Probebuch' / 'Probebuch.pdf'))

    # Öffnen des EPUB: Empfohlen wird das gesicherte PDF daneben (mit Seitenbildern und Arbeitsstand), das EPUB bleibt zweite Wahl
    f = lib.lpost('/api/scan', dict(path=str(tmp_path / 'Probebuch (2).epub')))[1]['found']
    assert [x['kind'] for x in f] == ['pdfbuch', 'epub'] and f[0]['path'] == str(tmp_path / 'Probebuch (2).pdf')
    assert f[0]['epub'] == str(tmp_path / 'Probebuch (2).epub') and f[0]['known'] and f[1]['pdfbuch'] == f[0]['path']


def test_fremdes_epub_ohne_eigenes_pdf(tmp_path):
    """Ein EPUB von anderswo neben einem gewöhnlichen PDF bleibt, wie es war: EPUB mit dem PDF als Scan."""
    import finder
    out = str(tmp_path / 'Buch.epub')
    epubbuch.write(data({'001': ['Text.']}), out)
    (tmp_path / 'Buch.pdf').write_bytes(b'%PDF-1.4 kein Buch')
    f = finder.scan_file(out)
    assert [x['kind'] for x in f] == ['epub'] and f[0]['kennung'] is None


def test_export_epub_braucht_ein_buch(lib):
    assert lib.lpost('/api/export_epub', dict(id='00000000'))[0] == 400
