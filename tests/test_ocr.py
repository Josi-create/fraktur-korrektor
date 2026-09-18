"""PDF/Bilder einlesen: Textaufbereitung, Tesseract-Ausgabe lesen, Ampel, Aufträge.
Der Durchlauf mit echtem Tesseract läuft nur, wo Tesseract mit dem Modell deu installiert ist."""
import os, time, types
import pytest
import ocr

TSV = '\n'.join(['level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext'] + [
    '\t'.join(map(str, r)) for r in [
        (1, 1, 0, 0, 0, 0, 0, 0, 2480, 3508, -1, ''),
        (4, 1, 1, 1, 1, 0, 300, 400, 1800, 60, -1, ''),
        (5, 1, 1, 1, 1, 1, 300, 400, 200, 60, 95.0, 'Die'),
        (5, 1, 1, 1, 1, 2, 520, 402, 500, 58, 90.0, 'Koloniſten'),
        (5, 1, 1, 1, 1, 3, 1040, 400, 300, 60, 92.0, 'zogen'),
        (5, 1, 1, 1, 1, 4, 1700, 400, 400, 60, 50.0, 'Zu⸗'),
        (5, 1, 1, 1, 2, 1, 300, 480, 300, 60, 91.0, 'kunft'),
        (5, 1, 1, 1, 2, 2, 620, 480, 200, 60, 93.0, 'lag'),
        (5, 1, 1, 1, 2, 3, 840, 480, 100, 60, 30.0, ' '),
    ]])


def test_clean_und_trennungen():
    assert ocr.clean('Koloniſten waͤren ⸗') == 'Kolonisten wären -'
    assert ocr.hyphens(['die Zu-', 'kunft lag', 'Amts- und', 'Stadt=', 'schreiber', 'Ende-']) == \
        ['die Zu¬', 'kunft lag', 'Amts- und', 'Stadt¬', 'schreiber', 'Ende-']
    assert ocr.hyphens(['Nord-', 'Amerika']) == ['Nord-', 'Amerika']  # groß weiter: kein Trennstrich


def test_tesseract_ausgabe_lesen(monkeypatch):
    seen = {}

    def run(cmd, **kw):
        seen['cmd'] = cmd
        return types.SimpleNamespace(returncode=0, stdout=TSV.encode('utf-8'), stderr=b'')
    monkeypatch.setattr(ocr.subprocess, 'run', run)
    lines, words = ocr.ocr_image('tesseract', 'x.png', 'frak2021', 'C:/modelle')
    assert [l['text'] for l in lines] == ['Die Kolonisten zogen Zu-', 'kunft lag']
    assert (lines[0]['x0'], lines[0]['x1'], lines[0]['y0'], lines[0]['y1'], lines[0]['bl']) == (300, 2100, 400, 460, 460)
    assert [w for w in words if w[2]] == [(50.0, 'Zu-', True)]  # Zeilenende nur bei Zeilen mit mindestens vier Wörtern
    # eigener Modellordner: die Ausgabeart muss als Parameter kommen, die Konfigurationsdatei "tsv" gäbe es dort nicht
    assert seen['cmd'][-2:] == ['-c', 'tessedit_create_tsv=1'] and 'C:/modelle' in seen['cmd']


def test_seitenwerte_und_ampel():
    good = [(95.0, 'Die', False), (90.0, 'Kolonisten', False), (92.0, 'zogen', False), (60.0, 'weit', True)]
    q = ocr.page_quality(good)
    assert q['words'] == 4 and q['dict'] == 1.0 and 85 < q['conf'] < 95 and q['ends'] > 30
    assert ocr.page_quality([]) == dict(conf=0.0, words=0, dict=0.0, ends=0.0)
    page = lambda conf, dq, ends=0.0, words=200: dict(conf=conf, dict=dq, ends=ends, words=words)
    assert ocr.rating({'001': page(91, 0.95), '002': page(88, 0.90)})['level'] == 'gruen'
    assert ocr.rating({'001': page(81, 0.83), '002': page(82, 0.82, ends=25)}) == dict(level='gelb', conf=81.5, dict=0.825, weak=[], ends=['002'])
    r = ocr.rating({'001': page(70, 0.60), '002': page(72, 0.65), '003': page(0, 0, words=3)})
    assert r['level'] == 'rot' and r['weak'] == ['001', '002']  # die fast leere Seite zählt nicht
    assert ocr.rating({})['level'] == 'rot'


def test_modellwahl(monkeypatch, tmp_path):
    monkeypatch.setattr(ocr, 'TESSDATA', str(tmp_path))
    monkeypatch.setattr(ocr, '_langs', lambda tess, d=None: ['frak2021'] if d else ['deu', 'osd', 'deu_frak'])
    assert ocr.pick_model('t') == ('frak2021', str(tmp_path))
    assert ocr.pick_model('t', 'antiqua') == ('deu', None)
    monkeypatch.setattr(ocr, '_langs', lambda tess, d=None: [] if d else ['eng'])
    assert ocr.pick_model('t') == (None, None)


def test_aufraeumen_laesst_scantailor_projekt_stehen(tmp_path):
    out = tmp_path / 'Buch'
    (out / 'img').mkdir(parents=True); (out / 'scantailor' / 'out').mkdir(parents=True)
    for n in ('001.txt', 'lines.json', 'img/001.jpg', 'scantailor/out/seite_001.tif'):
        (out / n).write_text('x')
    ocr.cleanup(str(out))
    assert sorted(p.name for p in out.iterdir()) == ['scantailor'] and (out / 'scantailor' / 'out' / 'seite_001.tif').exists()


def test_pdf_seiten_exportieren(tmp_path):
    fitz = pytest.importorskip('fitz')
    d = fitz.open()
    for n in range(3):
        d.new_page(width=300, height=400).insert_text((40, 60), 'Seite %d' % (n + 1))
    d.save(str(tmp_path / 'x.pdf')); d.close()
    seen = []
    assert ocr.export_pages(str(tmp_path / 'x.pdf'), str(tmp_path / 'st'), lambda done, total, msg: seen.append((done, total, msg))) == 3
    assert sorted(os.listdir(tmp_path / 'st')) == ['seite_001.png', 'seite_002.png', 'seite_003.png'] and seen[-1] == (3, 3, 'export')
    assert ocr.pdf_count(str(tmp_path / 'x.pdf')) == 3
    ocr.render_pdf(str(tmp_path / 'x.pdf'), 0, str(tmp_path / 'p.jpg'))
    assert ocr.image_size(str(tmp_path / 'p.jpg')) == (1250, 1667)  # 300 dpi


def wait(lib, job):
    for _ in range(1200):
        j = lib.lget('/api/job/' + job)[1]
        if j['state'] != 'running':
            return j
        time.sleep(0.1)
    raise AssertionError('Auftrag wird nicht fertig')


def test_auftraege_und_fehler(lib, tmp_path):
    assert set(lib.lget('/api/tools')[1]) == {'tesseract', 'model', 'antiqua', 'scantailor', 'pdf'}
    assert lib.lget('/api/job/00000000')[0] == 404
    j = wait(lib, lib.lpost('/api/import_ocr', dict(source=str(tmp_path / 'fehlt.pdf')))[1]['job'])
    assert (j['state'], j['error']) == ('error', 'quelle_fehlt')
    (tmp_path / 'bilder').mkdir()
    j = wait(lib, lib.lpost('/api/scantailor', dict(source=str(tmp_path / 'bilder')))[1]['job'])
    assert j['state'] == 'error' and j['error'] in ('nur_pdf', 'kein_scantailor')  # je nachdem, ob ScanTailor installiert ist
    assert lib.lpost('/api/set_tool', dict(tool='rm', path=str(tmp_path)))[0] == 400


def test_durchlauf_mit_tesseract(lib, tmp_path):
    fitz = pytest.importorskip('fitz')
    tess = ocr.find_tesseract()
    if not tess or 'deu' not in ocr._langs(tess):
        pytest.skip('Tesseract mit Modell deu ist nicht installiert')
    d = fitz.open()
    for n in range(2):
        pg = d.new_page(width=420, height=595)
        pg.insert_text((150, 50), '— %d —' % (n + 7), fontsize=11, fontname='tiro')
        for k, l in enumerate(['Die Kolonisten zogen nach Rußland, und der', 'Weg war weit. Sie dachten an die Zu-', 'kunft und an die Heimat, die sie verlassen', 'hatten, und an das Land, das vor ihnen lag.']):
            pg.insert_text((50, 100 + 22 * k), l, fontsize=13, fontname='tiro')
    d.save(str(tmp_path / 'probe.pdf')); d.close()
    job = lib.lpost('/api/import_ocr', dict(source=str(tmp_path / 'probe.pdf'), title='Probe', script='antiqua', target=str(tmp_path / 'ziel')))[1]['job']
    j = wait(lib, job)
    assert j['state'] == 'done', j
    r = j['result']
    assert (r['title'], r['pages']) == ('Probe', 2) and r['quality']['level'] in ('gruen', 'gelb')
    assert [b['quality'] for b in lib.lget('/api/library')[1]['books']] == [r['quality']['level']]
    page = lib.lget('/buch/%s/api/page/001' % r['id'])[1]
    assert page['lines'][0].startswith('#') and page['lines'][2].endswith('Zu¬') and page['lines'][3].startswith('kunft')
    assert page['img'].endswith('/img/001.jpg') and None not in page['geo'][1:] and page['flags'] == []
