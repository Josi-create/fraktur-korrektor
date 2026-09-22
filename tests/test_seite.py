"""Eine einzelne Seite ersetzen (#52): neues Seitenbild, nur diese Seite neu erkennen, die alte Fassung gesichert."""
import os, json, zipfile
import pytest
from conftest import make_book, png
from test_ocr import wait
import ocr

fitz = pytest.importorskip('fitz')


def test_seite_aus_pdf_ersetzen(lib, tmp_path):
    tools = lib.lget('/api/tools')[1]
    if tools['tesseract'] and not tools['antiqua']:
        pytest.skip('Tesseract ohne Modell deu: der Test soll nichts herunterladen')
    make_book(str(tmp_path / 'Buch'))
    bid = lib.lpost('/api/open', dict(folder=str(tmp_path / 'Buch')))[1]['id']
    b = '/buch/' + bid
    # ein PDF mit sichtbarem Text: mit Tesseract wird er gelesen, ohne Tesseract aus der Textebene übernommen
    d = fitz.open()
    for n in range(2):
        pg = d.new_page(width=420, height=595)
        for k, l in enumerate(['Die Kolonisten zogen nach Russland', 'und der Weg war weit und schwer.', 'Seite %d' % (n + 1)]):
            pg.insert_text((40, 120 + 40 * k), l, fontsize=20, fontname='helv')
    d.save(str(tmp_path / 'neu.pdf')); d.close()
    vorher = lib.lget(b + '/api/page/001')[1]
    j = wait(lib, lib.lpost(b + '/api/replace_page', dict(page='001', source=str(tmp_path / 'neu.pdf'), n=2, script='antiqua'))[1]['job'])
    assert j['state'] == 'done', j
    r = j['result']
    assert r['page'] == '001' and r['backup'].startswith('vorher-') and r['lines'] >= 1
    nachher = lib.lget(b + '/api/page/001')[1]
    assert nachher['lines'] != vorher['lines'] and nachher['img'].endswith('001.jpg') and nachher['size'][0] > 1500  # 420 pt bei 300 dpi
    assert 'Kolonisten' in ' '.join(nachher['lines']) and 'Vater' not in ' '.join(nachher['lines'])
    assert not os.path.exists(tmp_path / 'Buch' / 'img' / '001.png') and nachher['geo'] and len(nachher['geo']) == len(nachher['lines'])
    geo = json.load(open(tmp_path / 'Buch' / 'lines.json', encoding='utf-8'))
    assert geo['001']['w'] == nachher['size'][0] and geo['002']['w'] == 1000  # die andere Seite ist unberührt
    assert lib.lget(b + '/api/page/002')[1]['lines'] == ['# 6', 'Der Vater und ber Sohn.']
    with zipfile.ZipFile(tmp_path / 'Buch' / r['backup']) as z:
        assert {'001.txt', 'lines.json', 'img/001.png'} <= set(z.namelist()) and '002.txt' not in z.namelist()
    log = [l.split('\t') for l in open(tmp_path / 'Buch' / 'korrekturen.log', encoding='utf-8').read().splitlines()]
    assert log[-1][1:5] == ['seite', '001', '0', '001.png'] and log[-1][5] == 'neu.pdf S. 2'
    # Frühere Fassung: Text, Zeilenlage und Bild kommen zurück
    assert lib.lpost('/api/restore', dict(id=bid, name=r['backup']))[0] == 200
    zurueck = lib.lget(b + '/api/page/001')[1]
    assert zurueck['lines'] == vorher['lines'] and zurueck['img'].endswith('001.png') and zurueck['size'] == [500, 750]
    assert not os.path.exists(tmp_path / 'Buch' / 'img' / '001.jpg')
    # Fehler verständlich: PDF-Seite, die es nicht gibt; Datei, die es nicht gibt; Seite, die es nicht gibt
    j = wait(lib, lib.lpost(b + '/api/replace_page', dict(page='001', source=str(tmp_path / 'neu.pdf'), n=9))[1]['job'])
    assert (j['state'], j['error']) == ('error', 'keine_seiten')
    j = wait(lib, lib.lpost(b + '/api/replace_page', dict(page='001', source=str(tmp_path / 'fehlt.png')))[1]['job'])
    assert (j['state'], j['error']) == ('error', 'quelle_fehlt')
    j = wait(lib, lib.lpost(b + '/api/replace_page', dict(page='009', source=str(tmp_path / 'neu.pdf')))[1]['job'])
    assert (j['state'], j['error']) == ('error', 'quelle_fehlt')


def test_bild_ohne_tesseract(tmp_path, monkeypatch):
    """Eine Bilddatei hat keine Textebene – ohne Tesseract geht das nicht, und der Text der Seite bleibt heil."""
    monkeypatch.setattr(ocr, 'find_tesseract', lambda: None)
    folder = str(tmp_path / 'Buch')
    make_book(folder)
    (tmp_path / 'neu.png').write_bytes(png(300, 400))
    with pytest.raises(ValueError, match='kein_tesseract'):
        ocr.recognize_page(folder, '001', str(tmp_path / 'neu.png'))
    assert open(os.path.join(folder, '001.txt'), encoding='utf-8').read().startswith('# 5')
    with pytest.raises(ValueError, match='quelle_fehlt'):
        ocr.recognize_page(folder, '001', os.path.join(folder, '001.txt'))
