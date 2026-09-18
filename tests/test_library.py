"""Bibliothek, Transkribus-Import, Hilfe, Sprachdateien."""
import os, re, json, zipfile
from conftest import ROOT, make_book, png

PAGE_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15">
 <Page imageFilename="%(img)s" imageWidth="2480" imageHeight="3508"><TextRegion id="r1">
%(lines)s
 </TextRegion></Page></PcGts>'''
LINE = ('  <TextLine id="l%(n)d"><Coords points="100,%(y0)d 900,%(y0)d 900,%(y1)d 100,%(y1)d"/>'
        '<Baseline points="100,%(bl)d 900,%(bl)d"/><TextEquiv><Unicode>%(text)s</Unicode></TextEquiv></TextLine>')


def make_export(path, images=True):
    """Transkribus-Export als ZIP: <docid>/<titel>/page/NNNN_name.xml, metadata.xml, optional Bilder."""
    pages = {'0001_scan': [(100, '— 7 —'), (400, 'Die Kolonisten zogen'), (470, 'nach Rußland.'), (800, '1) Vgl. die Quellen.'), (850, 'Zweite Zeile der Fußnote.')],
             '0002_scan': [(100, 'Der Vater und ber Sohn.')]}
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('4711/Probebuch/metadata.xml', '<trpDocMetadata><docId>4711</docId><title>Probebuch 1818</title></trpDocMetadata>')
        for name, lines in pages.items():
            xml = PAGE_XML % dict(img=name + '.png', lines='\n'.join(
                LINE % dict(n=n, y0=y, y1=y + 40, bl=y + 32, text=t) for n, (y, t) in enumerate(lines)))
            z.writestr('4711/Probebuch/page/%s.xml' % name, xml)
            if images:
                z.writestr('4711/Probebuch/%s.png' % name, png(1240, 1754))  # halbe Größe -> Maßstab 0.5


def test_start_mit_ordner_leitet_zum_buch(app):
    code, html = app.raw('/')  # urllib folgt der Umleitung nach /buch/<id>
    assert code == 200 and b'id="pagesel"' in html
    books = app.lget('/api/library')[1]['books']
    assert [(b['title'], b['pages']) for b in books] == [('buch', 2)]


def test_bibliothek_oeffnen_und_vergessen(lib, tmp_path):
    assert b'id="books"' in lib.raw('/')[1]
    info = lib.lget('/api/library')[1]
    assert info['books'] == [] and info['local'] and info['version']
    assert lib.lpost('/api/open', dict(folder=str(tmp_path)))== (400, dict(error='kein_buch'))
    make_book(str(tmp_path / 'Mein Buch' / 'ocr' / 'korr'))
    code, r = lib.lpost('/api/open', dict(folder=str(tmp_path / 'Mein Buch')))  # übergeordneter Ordner genügt
    assert code == 200
    assert [b['title'] for b in lib.lget('/api/library')[1]['books']] == ['Mein Buch']
    assert lib.lget('/buch/%s/api/overview' % r['id'])[1]['title'] == 'Mein Buch'
    lib.lpost('/api/forget', dict(id=r['id']))
    assert lib.lget('/api/library')[1]['books'] == []
    assert lib.lget('/buch/%s/api/overview' % r['id'])[0] == 404
    assert os.path.exists(tmp_path / 'Mein Buch' / 'ocr' / 'korr' / '001.txt')  # Dateien bleiben


def test_zwei_buecher_nebeneinander(app, tmp_path):
    make_book(str(tmp_path / 'zweites'))
    other = '/buch/' + app.lpost('/api/open', dict(folder=str(tmp_path / 'zweites')))[1]['id']
    old = app.text('002')[1]
    app.post('/api/edit/002', dict(edits=[dict(line=1, old=old, new='Geändert.')]))
    assert app.get('/api/page/002')[1]['lines'][1] == 'Geändert.'
    assert app.lget(other + '/api/page/002')[1]['lines'][1] == old


def test_transkribus_import(lib, tmp_path):
    z = str(tmp_path / 'export.zip')
    make_export(z)
    code, r = lib.lpost('/api/import_transkribus', dict(source=z, title='', target=str(tmp_path / 'ziel')))
    assert code == 200 and (r['title'], r['pages'], r['images'], r['warnings']) == ('Probebuch 1818', 2, 2, [])
    d = lib.lget('/buch/%s/api/page/001' % r['id'])[1]
    assert d['lines'] == ['# — 7 —', 'Die Kolonisten zogen', 'nach Rußland.', '---', '1) Vgl. die Quellen.', 'Zweite Zeile der Fußnote.']
    assert d['geo'][1] == dict(x0=50, x1=450, y0=200, y1=220) and d['geo'][3] is None
    # zweiter Import desselben Ziels überschreibt nicht
    r2 = lib.lpost('/api/import_transkribus', dict(source=z, target=str(tmp_path / 'ziel')))[1]
    assert r2['folder'].endswith('ziel (2)')


def test_import_ohne_bilder_und_fehler(lib, tmp_path):
    z = str(tmp_path / 'export.zip')
    make_export(z, images=False)
    r = lib.lpost('/api/import_transkribus', dict(source=z, target=str(tmp_path / 'ziel')))[1]
    assert r['images'] == 0 and r['warnings'] == ['bilder_fehlen']
    d = lib.lget('/buch/%s/api/page/001' % r['id'])[1]
    assert d['img'] is None and d['geo'] is None and len(d['lines']) == 6
    assert lib.lpost('/api/import_transkribus', dict(source=str(tmp_path / 'fehlt.zip'))) == (400, dict(error='quelle_fehlt'))
    with zipfile.ZipFile(str(tmp_path / 'leer.zip'), 'w') as e:
        e.writestr('liesmich.txt', 'nichts')
    assert lib.lpost('/api/import_transkribus', dict(source=str(tmp_path / 'leer.zip'), target=str(tmp_path / 'z2'))) == (400, dict(error='keine_xml'))


def test_jpeg_groesse(tmp_path):
    import server
    p = tmp_path / 'x.jpg'
    p.write_bytes(b'\xff\xd8\xff\xe0\x00\x10JFIF\0\x01\x01\0\0\x01\0\x01\0\0' + b'\xff\xc0\x00\x11\x08' + (750).to_bytes(2, 'big') + (500).to_bytes(2, 'big') + b'\x03' + b'\0' * 9)
    assert server.image_size(str(p)) == (500, 750)


def test_hilfe(lib):
    for lang, word in (('de', 'Serienkorrektur'), ('en', 'Batch correction')):
        code, html = lib.raw('/hilfe/%s/usage' % lang)
        html = html.decode('utf-8')
        assert code == 200 and word in html and '<table>' in html and 'class="cur"' in html
    index = lib.raw('/hilfe/de/index')[1].decode('utf-8')
    assert 'href="usage"' in index and '.md"' not in index
    assert lib.raw('/hilfe/de/gibtsnicht')[0] == 404
    assert lib.raw('/hilfe/de/..%2Fserver')[0] == 404


def test_hilfeseiten_in_beiden_sprachen():
    de, en = (sorted(os.listdir(os.path.join(ROOT, 'docs', l))) for l in ('de', 'en'))
    assert de == en


def test_sprachdatei_vollstaendig():
    src = open(os.path.join(ROOT, 'i18n.js'), encoding='utf-8').read()
    de, en = (set(re.findall(r"(?:^  |', )(\w+): '", b, re.M)) for b in re.split(r'^en: \{', src.split('function t(')[0], flags=re.M))
    assert de == en and len(de) > 60
    used = set()
    for f in ('reader.html', 'bibliothek.html'):
        html = open(os.path.join(ROOT, f), encoding='utf-8').read()
        used |= set(re.findall(r"\bt\('(\w+)'", html)) | set(re.findall(r'data-t(?:-ph|-title)?="(\w+)"', html))
    used = {k for k in used if not k.endswith('_')}  # zusammengesetzte Schlüssel: t('err_' + code)
    assert used <= de, used - de
    assert {'err_kein_buch', 'err_quelle_fehlt', 'err_keine_xml', 'err_nur_lokal', 'err_unknown', 'warn_bilder_fehlen'} <= de


def test_t_wird_nicht_verdeckt():
    """Eine lokale Variable t würde die Übersetzungsfunktion t() verdecken (Laufzeitfehler erst im Browser)."""
    for f in ('reader.html', 'bibliothek.html'):
        html = open(os.path.join(ROOT, f), encoding='utf-8').read()
        assert not re.search(r'\b(?:let|const|var)\s+t\b|\bt\s*=>|\(t\)\s*=>|function\s*\w*\([^)]*\bt\b[^)]*\)', html), f
