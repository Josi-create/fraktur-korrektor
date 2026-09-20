"""Ein Buch weiterbearbeiten, statt jedes Mal ein neues anzulegen: Transkribus-Text nachlegen, Bilder ergänzen,
die anderen Programme vorbereiten. Die Seitenzuordnung ist der heikle Teil – fehlt im Export eine Seite, darf
nicht der halbe Text neben dem falschen Bild landen."""
import os, json, glob, struct, zipfile
import pytest
import ocr, pagexml
from conftest import png
from test_library import PAGE_XML, LINE
from test_ocr import wait

# Genug eigene Wörter je Seite, damit sich die Seiten am Wortlaut auseinanderhalten lassen
TEXTE = {
    '001': ['Vorsatzblatt der Bibliothek Muenster'],
    '002': ['Die Kolonisten zogen nach Rußland, denn', 'die Zukunft lag vor ihnen und der Weg', 'war weit und beschwerlich gewesen.'],
    '003': ['Der Vater sprach zum Sohne über Ernte,', 'Wetter und Saatgut in Bessarabien,', 'während draußen der Regen fiel.'],
    '004': ['Kirchenbücher, Auswanderung und Heimat', 'beschäftigten die Gemeinde jahrzehntelang,', 'wie die Chronik ausführlich berichtet.'],
}


def make_book(folder, pages=TEXTE, images=True):
    os.makedirs(os.path.join(folder, 'img'), exist_ok=True)
    geo = {}
    for pg, lines in pages.items():
        with open(os.path.join(folder, pg + '.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('# \n' + '\n'.join(lines) + '\n')
        geo[pg] = dict(w=1000, h=1500, lines=[dict(text=l, x0=100, x1=900, y0=100 + 60 * n, y1=140 + 60 * n,
                                                   bl=132 + 60 * n, kind='body') for n, l in enumerate(lines)])
        if images:  # jede Seite ein anderes Bild, damit die Zuordnung prüfbar ist
            with open(os.path.join(folder, 'img', pg + '.png'), 'wb') as f:
                f.write(png(500 + int(pg), 750))
    with open(os.path.join(folder, 'lines.json'), 'w', encoding='utf-8') as f:
        json.dump(geo, f, ensure_ascii=False)
    return folder


def make_export(path, pages, images=False):
    """pages: {dateiname: [zeilen]} – der Export trägt die Namen der hochgeladenen Bilder."""
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('4711/Probebuch/metadata.xml', '<trpDocMetadata><title>Probebuch</title></trpDocMetadata>')
        for name, lines in pages.items():
            xml = PAGE_XML % dict(img=name + '.png', lines='\n'.join(
                LINE % dict(n=n, y0=100 + 60 * n, y1=140 + 60 * n, bl=132 + 60 * n, text=t + ' (Transkribus)') for n, t in enumerate(lines)))
            z.writestr('4711/Probebuch/page/%s.xml' % name, xml)
            if images:
                z.writestr('4711/Probebuch/%s.png' % name, png(1240, 1754))
    return str(path)


def test_zuordnung_ueber_die_gemerkten_namen(tmp_path):
    """Das Buch weiß aus quellen.json, wie seine Bilder hießen – dann ist die Zuordnung eindeutig."""
    folder = make_book(str(tmp_path / 'buch'))
    pagexml.save_origin(folder, {'001': 'seite_001_1L.tif', '002': 'seite_001_2R.tif',
                                 '003': 'seite_002_1L.tif', '004': 'seite_002_2R.tif'})
    src = make_export(tmp_path / 'export.zip', {'0007_seite_002_1L': TEXTE['003'], '0008_seite_002_2R': TEXTE['004']})
    r = pagexml.import_into(src, folder)
    assert r['how'] == 'namen' and r['replaced'] == 2 and r['kept'] == ['001', '002']
    assert 'Transkribus' in open(os.path.join(folder, '003.txt'), encoding='utf-8').read()
    assert 'Transkribus' not in open(os.path.join(folder, '001.txt'), encoding='utf-8').read()


def test_fehlende_erste_seite_verschiebt_nichts(tmp_path):
    """Der Fall aus dem Alltag: 58 Seiten im Buch, 57 im Export – die erste fehlt. Ohne Namen muss der Wortlaut
    entscheiden, sonst stünde ab hier jeder Text neben dem falschen Bild."""
    folder = make_book(str(tmp_path / 'buch'))
    src = make_export(tmp_path / 'export.zip', {'0001_fremd_a': TEXTE['002'], '0002_fremd_b': TEXTE['003'], '0003_fremd_c': TEXTE['004']})
    r = pagexml.import_into(src, folder)
    assert r['how'] == 'text' and r['replaced'] == 3 and r['kept'] == ['001']
    for pg in ('002', '003', '004'):
        neu = open(os.path.join(folder, pg + '.txt'), encoding='utf-8').read()
        assert 'Transkribus' in neu and TEXTE[pg][0] in neu  # dieselbe Seite, nicht die des Nachbarn
    assert 'Transkribus' not in open(os.path.join(folder, '001.txt'), encoding='utf-8').read()


def test_seitenbilder_und_arbeit_bleiben(tmp_path):
    folder = make_book(str(tmp_path / 'buch'))
    open(os.path.join(folder, 'whitelist.txt'), 'w', encoding='utf-8').write('Bessarabien\n')
    open(os.path.join(folder, 'korrekturen.log'), 'w', encoding='utf-8').write('a\tedit\t002\t1\talt\tneu\n')
    src = make_export(tmp_path / 'export.zip', {'0001_a': TEXTE['001'], '0002_b': TEXTE['002'],
                                                '0003_c': TEXTE['003'], '0004_d': TEXTE['004']})
    r = pagexml.import_into(src, folder)
    assert len(glob.glob(os.path.join(folder, 'img', '*.png'))) == 4      # Bilder unangetastet
    assert os.path.exists(os.path.join(folder, 'whitelist.txt'))
    assert r['backup'] and os.path.exists(os.path.join(folder, r['backup']))
    with zipfile.ZipFile(os.path.join(folder, r['backup'])) as z:          # die alte Fassung ist gesichert
        assert '002.txt' in z.namelist() and 'korrekturen.log' in z.namelist()
        assert 'Transkribus' not in z.read('002.txt').decode('utf-8')
    geo = json.load(open(os.path.join(folder, 'lines.json'), encoding='utf-8'))
    assert len(geo) == 4 and geo['002']['w'] == 2480                       # Geometrie aus dem Export


def test_export_passt_nicht_zum_buch(tmp_path):
    """Lieber ehrlich abbrechen als Text neben das falsche Bild legen."""
    folder = make_book(str(tmp_path / 'buch'))
    src = make_export(tmp_path / 'export.zip', {'0001_x': ['Ein ganz anderes Werk über Segelschiffe'],
                                                '0002_y': ['Takelage, Rahsegel und Kompaßrose ausführlich']})
    with pytest.raises(ValueError, match='seiten_passen_nicht'):
        pagexml.import_into(src, folder)


def test_seitenbilder_nachlegen(tmp_path):
    """Transkribus-Export ohne Bilder: die Bilder kommen später dazu, zugeordnet über ihre Namen."""
    pytest.importorskip('fitz')
    folder = make_book(str(tmp_path / 'buch'), images=False)
    pagexml.save_origin(folder, {pg: 'scan_%s.png' % pg for pg in TEXTE})
    quelle = tmp_path / 'bilder'
    quelle.mkdir()
    for pg in TEXTE:
        (quelle / ('scan_%s.png' % pg)).write_bytes(png(500, 750))
    r = ocr.add_images(folder, str(quelle))
    assert r['added'] == 4 and r['how'] == 'namen'
    assert sorted(os.path.basename(f) for f in glob.glob(os.path.join(folder, 'img', '*'))) == \
        ['001.png', '002.png', '003.png', '004.png']


def breite(path):
    """Breite eines PNG – so lässt sich prüfen, welches Bild wo gelandet ist."""
    with open(path, 'rb') as f:
        return struct.unpack('>I', f.read(24)[16:20])[0]


def test_bilder_aus_einem_anderen_buch(tmp_path):
    """Der natürliche Weg: ein Buch mit Bildern, daneben der Transkribus-Text als eigenes Buch – und die Bilder
    sollen dazu. Dass im Bilderbuch eine Seite mehr liegt, darf nicht zur Absage führen."""
    alt = make_book(str(tmp_path / 'mit Bildern'))
    neu = make_book(str(tmp_path / 'aus Transkribus'), {'001': TEXTE['002'], '002': TEXTE['003'], '003': TEXTE['004']}, images=False)
    r = ocr.add_images(neu, os.path.join(alt, 'img'))
    assert r['added'] == 3 and r['how'] == 'text'
    for neu_pg, alt_pg in (('001', '002'), ('002', '003'), ('003', '004')):
        assert breite(os.path.join(neu, 'img', neu_pg + '.png')) == breite(os.path.join(alt, 'img', alt_pg + '.png'))


def test_bilder_aus_einem_anderen_buch_ueber_die_namen(tmp_path):
    """Kennen beide Bücher die ursprünglichen Namen ihrer Seitenbilder, braucht es keinen Textvergleich."""
    alt = make_book(str(tmp_path / 'mit Bildern'))
    pagexml.save_origin(alt, {pg: 'seite_%s.tif' % pg for pg in TEXTE})
    neu = make_book(str(tmp_path / 'aus Transkribus'), {'001': ['Ganz anderer Text'], '002': ['Und noch einer']}, images=False)
    pagexml.save_origin(neu, {'001': 'seite_003.tif', '002': 'seite_001.tif'})
    r = ocr.add_images(neu, alt)  # auch der Buchordner selbst ist eine gültige Angabe
    assert r['added'] == 2 and r['how'] == 'namen'
    assert breite(os.path.join(neu, 'img', '001.png')) == breite(os.path.join(alt, 'img', '003.png'))
    assert breite(os.path.join(neu, 'img', '002.png')) == breite(os.path.join(alt, 'img', '001.png'))


def test_bilder_merken_sich_ihre_herkunft(tmp_path):
    """Damit ein Transkribus-Export, der später zurückkommt, die Seiten wiederfindet."""
    pytest.importorskip('fitz')
    if not ocr.find_tesseract():
        pytest.skip('Tesseract fehlt')
    quelle = tmp_path / 'seiten'
    quelle.mkdir()
    for n in (1, 2):
        (quelle / ('seite_%03d_1L.png' % n)).write_bytes(png(600, 800))
    ocr.build(str(quelle), str(tmp_path / 'neu'))
    assert json.load(open(str(tmp_path / 'neu' / 'quellen.json'), encoding='utf-8')) == \
        {'001': 'seite_001_1L.png', '002': 'seite_002_1L.png'}


def test_textexport_statt_pagexml(tmp_path):
    """Transkribus gibt auf Wunsch reinen Text aus – eine Datei, in der zwei Leerzeilen die Seiten trennen.
    Bleibt die Zeilenzahl gleich, behalten die Zeilen ihre Lage im Bild."""
    folder = make_book(str(tmp_path / 'buch'))
    txt = tmp_path / 'Stumpp_1922.txt'
    txt.write_text('\n\n\n'.join('\n'.join(z + ' (Transkribus)' for z in TEXTE[pg]) for pg in ('002', '003', '004')), encoding='utf-8')
    r = pagexml.import_into(str(txt), folder)
    assert r['replaced'] == 3 and r['how'] == 'text' and r['kept'] == ['001'] and not r['nogeo']
    geo = json.load(open(os.path.join(folder, 'lines.json'), encoding='utf-8'))
    assert 'Transkribus' in geo['002']['lines'][0]['text']
    assert geo['002']['lines'][0]['x0'] == 100  # die Lage im Bild ist geblieben


def test_textexport_mit_anderer_zeilenzahl(tmp_path):
    """Schneidet die andere Erkennung die Zeilen anders, passt die alte Lage nicht mehr – dann lieber keine."""
    folder = make_book(str(tmp_path / 'buch'))
    txt = tmp_path / 'export.txt'
    seiten = [' '.join(TEXTE['002']) + ' (Transkribus)',                       # drei Zeilen zu einer verschmolzen
              '\n'.join(z + ' (Transkribus)' for z in TEXTE['003'])]
    txt.write_text('\n\n\n'.join(seiten), encoding='utf-8')
    r = pagexml.import_into(str(txt), folder)
    assert r['replaced'] == 2 and r['nogeo'] == ['002']
    geo = json.load(open(os.path.join(folder, 'lines.json'), encoding='utf-8'))
    assert '002' not in geo and '003' in geo


def test_textexport_je_seite_eine_datei(tmp_path):
    ordner = tmp_path / 'export'
    ordner.mkdir()
    for n, pg in enumerate(('002', '003'), 1):
        (ordner / ('%04d_seite.txt' % n)).write_text('\n'.join(TEXTE[pg]), encoding='utf-8')
    (ordner / 'log.txt').write_text('LOGFILE FOR EXPORT JOB 1', encoding='utf-8')  # zählt nicht als Seite
    seiten = pagexml.text_pages(str(ordner))
    assert [k for k, _ in seiten] == ['0001_seite.txt', '0002_seite.txt']
    assert seiten[0][1] == TEXTE['002']


def test_herkunft_aelterer_buecher(tmp_path):
    """Bücher von früher vermerken nicht, woher ihr Text stammt – das steht aber in den Zeilen: Transkribus
    nummeriert sie, die eingebaute Erkennung merkt sich statt dessen ihre Sicherheit."""
    import server
    folder = make_book(str(tmp_path / 'von frueher'))
    geo = json.load(open(os.path.join(folder, 'lines.json'), encoding='utf-8'))
    for pg in geo.values():
        for n, l in enumerate(pg['lines']):
            l['id'] = 'l%d' % n
    json.dump(geo, open(os.path.join(folder, 'lines.json'), 'w', encoding='utf-8'))
    assert server.guess_source(folder) == ['transkribus']
    for pg in geo.values():
        for l in pg['lines']:
            del l['id']
            l['conf'] = 88
    json.dump(geo, open(os.path.join(folder, 'lines.json'), 'w', encoding='utf-8'))
    assert server.guess_source(folder) == ['tesseract']


def test_kennzeichen_werden_nachgetragen(tmp_path):
    """Eine Bewertung von früher kennt nur das Modell – daraus wird die Herkunft, ohne neu zu rechnen."""
    import server
    folder = make_book(str(tmp_path / 'mit Ampel'))
    json.dump(dict(model='frak2021', rating=dict(level='gelb', conf=76.0, dict=0.8, weak=[], ends=[]), pages={}),
              open(os.path.join(folder, 'qualitaet.json'), 'w', encoding='utf-8'))
    assert server.ensure_marks(folder)['quelle'] == ['tesseract']
    assert json.load(open(os.path.join(folder, 'qualitaet.json'), encoding='utf-8'))['quelle'] == ['tesseract']


def test_ampel_fuer_text_ohne_konfidenz(tmp_path):
    """Transkribus sagt nicht, wie sicher es sich war – die Wörterbuchquote sagt es statt dessen."""
    # Seiten unter 20 Wörtern zählen für die Ampel nicht – also genug Text je Seite
    texte = {pg: TEXTE['002'] + TEXTE['003'] + TEXTE['004'] for pg in ('001', '002', '003')}
    folder = make_book(str(tmp_path / 'aus Transkribus'), texte)
    r = ocr.rate_book(folder, ['scantailor', 'transkribus'])
    assert r['conf'] is None and 0 <= r['dict'] <= 1 and r['level'] in ('gruen', 'gelb', 'rot')
    q = json.load(open(os.path.join(folder, 'qualitaet.json'), encoding='utf-8'))
    assert q['quelle'] == ['scantailor', 'transkribus'] and q['model'] == 'transkribus'


def test_ueber_den_server(lib, tmp_path):
    """Der Weg, den die Bibliothek geht: Buch eintragen, Text nachlegen, Ordner für Transkribus nennen."""
    folder = make_book(str(tmp_path / 'Mein Buch'))
    bid = lib.lpost('/api/open', dict(folder=folder))[1]['id']
    b = lib.lget('/api/library')[1]['books'][0]
    assert b['images'] == 4 and b['corrections'] == 0
    src = make_export(tmp_path / 'export.zip', {'0002_b': TEXTE['002'], '0003_c': TEXTE['003'], '0004_d': TEXTE['004']})
    r = wait(lib, lib.lpost('/api/add_transkribus', dict(id=bid, source=src))[1]['job'])['result']
    assert r['replaced'] == 3 and r['kept'] == ['001'] and r['how'] == 'text'
    seite = lib.lget('/buch/%s/api/page/002' % bid)[1]  # der Server zeigt den neuen Text, nicht den gemerkten alten
    assert 'Transkribus' in json.dumps(seite, ensure_ascii=False)


def test_ordner_fuer_das_andere_programm(tmp_path, monkeypatch):
    """»Für Transkribus vorbereiten« nennt den Bilderordner des Buchs. Zwischenablage und Dateifenster bleiben
    im Test außen vor – sonst ginge bei jedem Testlauf ein Finder-Fenster auf."""
    import server
    gezeigt = []
    monkeypatch.setattr(ocr, 'reveal', lambda f: gezeigt.append(f) or True)
    monkeypatch.setattr(ocr, 'to_clipboard', lambda x: True)
    folder = make_book(str(tmp_path / 'Mein Buch'))
    server.lib_touch(folder)
    r = server.prepare(server.book_id(folder), 'transkribus')
    assert r['folder'] == os.path.join(folder, 'img') and r['pages'] == 4 and r['out'] is None
    assert gezeigt == [os.path.join(folder, 'img')] and r['clipboard']


def test_fehlerhafte_anfragen(lib, tmp_path):
    assert lib.lpost('/api/add_transkribus', dict(id='deadbeef', source='x'))[1].get('job')  # Auftrag startet
    folder = make_book(str(tmp_path / 'buch'), images=False)
    bid = lib.lpost('/api/open', dict(folder=folder))[1]['id']
    assert lib.lpost('/api/prepare', dict(id=bid, tool='transkribus')) == (400, dict(error='keine_bilder'))
