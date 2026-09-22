"""Ein Buch als PDF sichern und auf einem anderen Rechner wieder einlesen (#58): Seitenbilder, Textebene, Arbeitsstand."""
import os, json
import pytest
from conftest import make_book, png
from test_ocr import wait

fitz = pytest.importorskip('fitz')


def job(lib, path, body):
    j = wait(lib, lib.lpost(path, body)[1]['job'])
    assert j['state'] == 'done', j
    return j['result']


def test_hin_und_zurueck(lib, tmp_path):
    import finder, pdfbuch
    make_book(str(tmp_path / 'Probebuch'))
    # ein JPEG-Seitenbild dazu: das muss byteidentisch wieder herauskommen
    pix = fitz.Pixmap(fitz.csGRAY, fitz.IRect(0, 0, 500, 750), 0)
    pix.clear_with(200)
    os.remove(str(tmp_path / 'Probebuch' / 'img' / '002.png'))
    pix.save(str(tmp_path / 'Probebuch' / 'img' / '002.jpg'), jpg_quality=80)
    bid = lib.lpost('/api/open', dict(folder=str(tmp_path / 'Probebuch')))[1]['id']
    b = '/buch/' + bid
    # Arbeit hineinlegen: Korrektur, Wortliste, Lesezeichen, Auszeichnung
    old = lib.lget(b + '/api/page/001')[1]['lines'][2]
    lib.lpost(b + '/api/edit/001', dict(edits=[dict(line=2, old=old, new='der Weg war weit. Die Zu¬')]))
    lib.lpost(b + '/api/whitelist', dict(word='Kolonisten'))
    lib.lpost(b + '/api/bookmark', dict(page='002', line=1))
    lib.lpost(b + '/api/markup/001', dict(kind='heading', line=1, old='Die Kolonisten zogen nach Rußland und', level=2))

    r = job(lib, '/api/export_pdf', dict(id=bid, target=str(tmp_path)))
    pdf = str(tmp_path / 'Probebuch.pdf')
    assert r['file'] == pdf and r['pages'] == 2 and r['images'] == 2 and r['corrections'] == 3 and r['size'] > 1000  # Korrektur, Whitelist, Überschrift
    kennung = json.load(open(tmp_path / 'Probebuch' / 'buch.json', encoding='utf-8'))['kennung']
    assert kennung and len(kennung) == 32
    with fitz.open(pdf) as d:
        assert d.page_count == 2 and d.metadata['title'] == 'Probebuch' and d.metadata['creator'].startswith('Fraktur-Korrektor')
        assert d.embfile_names() == ['fraktur-korrektor.zip']
        text = d[0].get_text()
        assert 'Kolonisten zogen nach Rußland' in text and 'der Weg war weit' in text and '<h2>' not in text and '# 5' not in text
        assert 'Vgl. die Quellen' in text  # Fußnote
        assert '1) Vgl' in d[0].get_text() and d[0].get_text('words')  # Suchen im Reader findet die Stellen
        # die Textebene liegt an der Stelle der Zeile: Zeile 1 (Rahmen y 160–200 von 1500, Bild 750 hoch -> 80–100 px -> 19,2–24 pt)
        w = [x for x in d[0].get_text('words') if x[4] == 'Kolonisten'][0]
        assert 18 < w[1] < 21 and 22.5 < w[3] < 24.5 and 12 < w[0] < 24, w  # x: Rahmen ab 100 px -> 12 pt, dann „Die “
        assert d[1].get_images()[0][8] == 'DCTDecode'
    m = pdfbuch.info(pdf)
    assert m['titel'] == 'Probebuch' and m['kennung'] == kennung and m['korrekturen'] == 3 and m['seiten'] == {'001': '001.png', '002': '002.jpg'}
    assert pdfbuch.info(str(tmp_path / 'Probebuch' / '001.txt')) is None

    # das Programm erkennt sein PDF – als Fund mit der Arbeit darin, und als schon bekanntes Buch
    f = lib.lpost('/api/scan', dict(path=pdf))[1]['found']
    assert len(f) == 1 and f[0]['kind'] == 'pdfbuch' and f[0]['corrections'] == 3 and f[0]['pages'] == 2 and f[0]['known'] and f[0]['name'] == 'Probebuch'
    assert finder.scan(str(tmp_path))['found'][0]['kind'] == 'book'  # der Ordner selbst: das Buch mit Korrekturen geht vor

    # auf dem »anderen Rechner«: einlesen
    r2 = job(lib, '/api/import_pdfbuch', dict(source=pdf, target=str(tmp_path / 'drueben')))
    out = str(tmp_path / 'drueben')
    assert (r2['folder'], r2['pages'], r2['images'], r2['corrections'], r2['bookmark'], r2['title']) == (out, 2, 2, 3, '002', 'Probebuch')
    for n in ('001.txt', '002.txt', 'lines.json', 'whitelist.txt', 'lesezeichen.json', 'korrekturen.log', 'buch.json'):
        assert open(os.path.join(out, n), 'rb').read() == open(str(tmp_path / 'Probebuch' / n), 'rb').read(), n
    assert open(os.path.join(out, 'img', '002.jpg'), 'rb').read() == open(str(tmp_path / 'Probebuch' / 'img' / '002.jpg'), 'rb').read()
    assert fitz.Pixmap(os.path.join(out, 'img', '001.png')).width == 500
    assert not os.path.exists(os.path.join(out, 'fraktur-korrektor.json'))
    p = lib.lget('/buch/%s/api/page/001' % r2['id'])[1]
    assert p['lines'][1] == '<h2>Die Kolonisten zogen nach Rußland und</h2>' and p['geo'][1] and p['img'].endswith('001.png')
    assert lib.lget('/buch/%s/api/settings' % r2['id'])[1]['kennung'] == kennung
    assert [x['title'] for x in lib.lget('/api/library')[1]['books']] == ['Probebuch', 'Probebuch']
    # noch einmal: überschreibt nicht
    assert job(lib, '/api/import_pdfbuch', dict(source=pdf, target=out))['folder'] == out + ' (2)'


def test_sichern_ersetzt_nur_eigenes(lib, tmp_path):
    make_book(str(tmp_path / 'Buch'))
    bid = lib.lpost('/api/open', dict(folder=str(tmp_path / 'Buch')))[1]['id']
    (tmp_path / 'Buch.pdf').write_bytes(b'%PDF-1.4 fremd')  # eine fremde Datei desselben Namens bleibt
    r = job(lib, '/api/export_pdf', dict(id=bid, target=str(tmp_path)))
    assert r['file'] == str(tmp_path / 'Buch (2).pdf') and (tmp_path / 'Buch.pdf').read_bytes() == b'%PDF-1.4 fremd'
    r = job(lib, '/api/export_pdf', dict(id=bid, target=str(tmp_path)))  # dasselbe Buch noch einmal: ersetzt das eigene PDF
    assert r['file'] == str(tmp_path / 'Buch (2).pdf') and not (tmp_path / 'Buch (3).pdf').exists()
    j = wait(lib, lib.lpost('/api/export_pdf', dict(id=bid, target=str(tmp_path / 'gibtsnicht')))[1]['job'])
    assert (j['state'], j['error']) == ('error', 'kein_ordner')
    assert lib.lpost('/api/export_pdf', dict(id='deadbeef')) == (400, dict(error='quelle_fehlt'))
    # ohne Zielordner: neben den Buchordner
    r = job(lib, '/api/export_pdf', dict(id=bid))
    assert r['file'] == str(tmp_path / 'Buch (2).pdf')  # derselbe Ordner, dasselbe eigene PDF
    j = wait(lib, lib.lpost('/api/import_pdfbuch', dict(source=str(tmp_path / 'Buch.pdf')))[1]['job'])
    assert (j['state'], j['error']) == ('error', 'kein_pdfbuch')


def test_buch_ohne_bilder(lib, tmp_path):
    """Ein Textbuch (EPUB ohne PDF, Transkribus ohne Bilder) bekommt Seiten mit sichtbarem Text."""
    import pdfbuch, shutil
    make_book(str(tmp_path / 'Text'))
    shutil.rmtree(str(tmp_path / 'Text' / 'img'))
    bid = lib.lpost('/api/open', dict(folder=str(tmp_path / 'Text')))[1]['id']
    r = job(lib, '/api/export_pdf', dict(id=bid, target=str(tmp_path)))
    assert r['images'] == 0 and r['pages'] == 2
    with fitz.open(r['file']) as d:
        assert 'Kolonisten' in d[0].get_text() and not d[0].get_images() and d[0].rect.width == 595
    assert pdfbuch.info(r['file'])['seiten'] == {'001': None, '002': None}
    r2 = job(lib, '/api/import_pdfbuch', dict(source=r['file'], target=str(tmp_path / 'zurueck')))
    assert r2['images'] == 0 and lib.lget('/buch/%s/api/page/001' % r2['id'])[1]['img'] is None
