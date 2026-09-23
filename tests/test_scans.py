"""Scans vorbereiten (#42): Doppelseiten erkennen und teilen, Schieflage messen und geraderichten – mit synthetischen
Seiten (schwarze Zeilenbalken auf Weiß, mit PyMuPDF gezeichnet), nie mit echten Buchdaten."""
import os, json
import pytest
import scans

fitz = pytest.importorskip('fitz')


def page(w, h, blocks, gutter=None):
    """Weiße Seite mit Textblöcken (x0, x1) aus Zeilenbalken; gutter = (x0, x1) eines dunklen Falzschattens."""
    d = fitz.open()
    p = d.new_page(width=w, height=h)
    for x0, x1 in blocks:
        for k, y in enumerate(range(int(h * 0.12), int(h * 0.88), 40)):
            p.draw_rect(fitz.Rect(x0, y, x1 - (90 if k % 3 == 0 else 0), y + 18), color=0, fill=0)
    if gutter:
        p.draw_rect(fitz.Rect(gutter[0], 0, gutter[1], h), color=0, fill=0)
    return p.get_pixmap(colorspace=fitz.csGRAY)


SINGLE = lambda: page(1200, 1600, [(150, 1050)])
DOUBLE = lambda: page(2400, 1600, [(150, 1050), (1350, 2250)])


def test_einzelseite_wird_nicht_geteilt():
    d = scans.detect_double(SINGLE())
    assert d['double'] is False and d['split'] is None
    # querliegend, aber nur eine Textspalte (Tabelle, Karte): auch keine Doppelseite
    assert scans.detect_double(page(2400, 1600, [(300, 2100)]))['double'] is False


def test_doppelseite_helle_bundmitte():
    d = scans.detect_double(DOUBLE())
    assert d['double'] and abs(d['split'] - 0.5) < 0.03
    # Bund nicht in der Mitte: das Profil findet ihn trotzdem
    d = scans.detect_double(page(2400, 1600, [(100, 900), (1150, 2300)]))
    assert d['double'] and abs(d['split'] - 1025 / 2400) < 0.03


def test_doppelseite_dunkle_falz():
    d = scans.detect_double(page(2400, 1600, [(150, 1050), (1350, 2250)], gutter=(1180, 1220)))
    assert d['double'] and abs(d['split'] - 0.5) < 0.02


def test_teilen_mit_feinjustierung():
    links, rechts = scans.split_page(DOUBLE(), 0.46)  # Vorgabe daneben, die Falz liegt bei 0,5
    assert abs(links.width - 1200) < 60 and links.width + rechts.width == 2400 and links.height == 1600
    assert scans.detect_double(links)['double'] is False


def test_schieflage_messen_und_geraderichten():
    assert scans.skew_angle(SINGLE()) == 0.0
    for a in (2.5, -1.7, 4.0):
        schief = scans.rotate(SINGLE(), a)
        assert schief.width == 1200 and schief.height == 1600
        m = scans.skew_angle(schief)
        assert abs(m + a) <= 0.2, (a, m)  # gemessen wird der Gegenwinkel
        assert abs(scans.skew_angle(scans.rotate(schief, m))) <= 0.2


def test_leere_seite_ist_gerade():
    assert scans.skew_angle(page(1200, 1600, [])) == 0.0


def _bilder(folder, n=4, angle=2.0):
    os.makedirs(folder)
    for k in range(n):
        scans.rotate(DOUBLE(), angle).save(os.path.join(folder, 'foto_%02d.jpg' % (k + 1)), jpg_quality=90)


def test_untersuchen_und_aufbereiten(tmp_path):
    src = str(tmp_path / 'fotos')
    _bilder(src)
    r = scans.inspect(src)
    assert r['pages'] == 4 and r['double'] and abs(r['split'] - 0.5) < 0.03 and 1.7 <= r['skew'] <= 2.3 and r['needed']
    seen = []
    out = str(tmp_path / 'aufbereitet')
    p = scans.prepare(src, out, split=r['split'], deskew=True, progress=lambda d, t, m: seen.append((d, t, m)))
    assert (p['pages'], p['split'], p['rotated']) == (8, 4, 8) and seen[-1] == (4, 4, 'scans')
    files = sorted(f for f in os.listdir(out) if f.endswith('.jpg'))
    assert files == ['seite_%03d.jpg' % k for k in range(1, 9)]
    einzel = scans.load_gray(os.path.join(out, 'seite_001.jpg'))
    assert einzel.height == 1600 and abs(einzel.width - 1200) < 60
    assert abs(scans.skew_angle(einzel)) <= 0.3 and scans.detect_double(einzel)['double'] is False
    j = json.load(open(os.path.join(out, 'aufbereitung.json'), encoding='utf-8'))
    assert j['geteilt'] == 4 and j['seiten'][0]['teil'] == 'links' and j['seiten'][1]['teil'] == 'rechts' and j['seiten'][1]['seite'] == 1


def test_gerade_einzelseiten_bleiben_unveraendert(tmp_path):
    src = tmp_path / 'scans'
    src.mkdir()
    SINGLE().save(str(src / 'a.png'))
    r = scans.inspect(str(src))
    assert not r['double'] and r['skew'] == 0.0 and not r['needed']
    p = scans.prepare(str(src), str(tmp_path / 'out'), split=None, deskew=True)
    assert (p['pages'], p['split'], p['rotated']) == (1, 0, 0)
    assert os.listdir(tmp_path / 'out') == ['aufbereitung.json', 'seite_001.png']


def test_pdf_als_quelle(tmp_path):
    d = fitz.open()
    for k in range(2):
        pg = d.new_page(width=600, height=400)
        pg.insert_image(pg.rect, pixmap=scans.rotate(DOUBLE(), -1.5))
    d.save(str(tmp_path / 'fotos.pdf'))
    d.close()
    r = scans.inspect(str(tmp_path / 'fotos.pdf'))
    assert r['pages'] == 2 and r['double'] and r['needed']
    assert scans.preview(str(tmp_path / 'fotos.pdf'), 0)[:2] == b'\xff\xd8'
    p = scans.prepare(str(tmp_path / 'fotos.pdf'), str(tmp_path / 'out'), split=r['split'])
    assert p['pages'] == 4 and p['rotated'] == 4


def test_leere_quelle(tmp_path):
    (tmp_path / 'leer').mkdir()
    with pytest.raises(ValueError, match='keine_seiten'):
        scans.inspect(str(tmp_path / 'leer'))


# ---- über den Server: Prüfung, Vorschau, Auftrag, und der Ordner »aufbereitet« als bevorzugte Quelle

def wait(lib, job):
    import time
    for _ in range(1200):
        j = lib.lget('/api/job/' + job)[1]
        if j['state'] != 'running':
            return j
        time.sleep(0.1)
    raise AssertionError('Auftrag wird nicht fertig')


def test_server_pruefen_vorschau_und_auftrag(lib, tmp_path):
    src = str(tmp_path / 'fotos')
    _bilder(src, n=3)
    assert lib.lpost('/api/scans_check', dict(source=str(tmp_path / 'fehlt')))[0] == 400
    code, r = lib.lpost('/api/scans_check', dict(source=src))
    assert code == 200 and r['double'] and r['needed'] and r['pages'] == 3
    code, body = lib.raw('/api/scan_preview?source=%s&n=%d' % (src, r['first']))
    assert code == 200 and body[:2] == b'\xff\xd8'
    assert lib.raw('/api/scan_preview?source=%s&n=99' % src)[0] == 404
    j = wait(lib, lib.lpost('/api/prepare_scans', dict(source=src, title='Fotos', split=r['split'], deskew=True, target=str(tmp_path / 'ziel')))[1]['job'])
    assert j['state'] == 'done', j
    out = j['result']
    assert (out['pages'], out['split'], out['rotated']) == (6, 3, 6)
    assert out['folder'] == str(tmp_path / 'ziel' / 'aufbereitet') and out['book'] == str(tmp_path / 'ziel')
    # Untersuchen des künftigen Buchordners: die vorbereiteten Seiten sind der Fund
    found = lib.lpost('/api/scan', dict(path=out['book']))[1]['found']
    assert found[0]['kind'] == 'images' and found[0]['prepared'] and found[0]['pages'] == 6
    # ein zweiter Durchlauf überschreibt nichts
    j = wait(lib, lib.lpost('/api/prepare_scans', dict(source=src, title='Fotos', split=None, deskew=False, target=str(tmp_path / 'ziel')))[1]['job'])
    assert j['state'] == 'done' and os.path.basename(j['result']['folder']) == 'aufbereitet (2)'
    j = wait(lib, lib.lpost('/api/prepare_scans', dict(source=str(tmp_path / 'fehlt')))[1]['job'])
    assert (j['state'], j['error']) == ('error', 'quelle_fehlt')


def test_server_seitenbilder_eines_buchs(app):
    """»Scans vorbereiten« bei einem Buch der Bibliothek: das Ergebnis kommt in den Buchordner und wird beim
    Untersuchen empfohlen – wie das Ergebnis von ScanTailor."""
    import finder, glob, time
    src = os.path.join(app.folder, 'img')
    for f in glob.glob(os.path.join(app.folder, '*.txt')):  # das Buch ist älter als die vorbereiteten Seiten (Minutenauflösung)
        os.utime(f, (time.time() - 180, time.time() - 180))
    r = app.lpost('/api/scans_check', dict(source=src))[1]
    assert r['pages'] == 2 and not r['double'] and not r['needed']
    j = wait(app, app.lpost('/api/prepare_scans', dict(source=src, split=None, deskew=True))[1]['job'])
    assert j['state'] == 'done' and j['result']['folder'] == os.path.join(app.folder, 'aufbereitet') and j['result']['pages'] == 2
    found = finder.scan(app.folder)['found']
    assert [f['kind'] for f in found] == ['images', 'book'] and found[0]['prepared']
