"""Zweispaltiger Satz (#37): Zeitungen und Lexika werden spaltenweise gelesen, einspaltige Seiten und die
nebeneinanderstehenden Fußnoten bleiben, wie sie waren."""
import types, random
import pagexml, ocr

# Seite im Transkribus-Maßstab (2480 x 3508): Haupttext von x=200 bis 2280, Spalten 200–1180 und 1300–2280
L = lambda text, x0, x1, bl, **kw: dict(text=text, x0=x0, x1=x1, y0=bl - 40, y1=bl + 10, bl=bl, **kw)


def spalten(n=5, schief=0, y=400, links=(200, 1180), rechts=(1300, 2280), gap=52):
    li = [L('L%d' % k, links[0], links[1], y + gap * k) for k in range(n)]
    re = [L('R%d' % k, rechts[0], rechts[1], y + gap * k + schief) for k in range(n)]
    return li, re


def texte(lines):
    return [d['text'] for d in lines]


def test_zwei_spalten_mit_ueberschrift():
    li, re = spalten(5, schief=6)  # die rechte Spalte liegt sechs Pixel tiefer: leicht schiefer Scan
    kopf = [L('— 12 —', 1100, 1380, 150), L('Zweites Kapitel', 700, 1780, 300)]
    lines = kopf + li + re
    random.Random(1).shuffle(lines)
    pagexml.classify(lines)
    assert texte(lines) == ['— 12 —', 'Zweites Kapitel'] + ['L%d' % k for k in range(5)] + ['R%d' % k for k in range(5)]
    assert [d['kind'] for d in lines] == ['head'] + ['body'] * 11
    assert pagexml.page_text(lines)[:3] == ['# — 12 —', 'Zweites Kapitel', 'L0']


def test_breite_zeile_trennt_abschnitte():
    # Über beide Spalten: Absatz oben, dann zwei Spalten, dann wieder eine Zeile über beide Spalten
    oben = [L('Ganz breit %d' % k, 200, 2280, 300 + 52 * k) for k in range(2)]
    li, re = spalten(4, y=500)
    unten = [L('Wieder breit', 200, 2280, 800)]
    lines = oben + li + re + unten
    pagexml.classify(lines)
    assert texte(lines) == ['Ganz breit 0', 'Ganz breit 1', 'L0', 'L1', 'L2', 'L3', 'R0', 'R1', 'R2', 'R3', 'Wieder breit']


def test_rechte_spalte_endet_frueher():
    li, re = spalten(8)
    re = re[:3]  # der Artikel endet oben rechts, darunter ist die Seite leer
    lines = re + li
    pagexml.classify(lines)
    assert texte(lines) == ['L%d' % k for k in range(8)] + ['R0', 'R1', 'R2']


def test_einspaltig_unveraendert():
    lines = [L('Zeile %d' % k, 200, 2280 if k % 3 else 1500, 400 + 52 * k) for k in range(8)]
    lines[3]['bl'] += 4  # ein wenig schief
    random.Random(2).shuffle(lines)
    pagexml.classify(lines)
    assert texte(lines) == ['Zeile %d' % k for k in range(8)]


def test_zweispaltige_fussnoten_bleiben_zeilenweise():
    # Kurze Fußnoten stehen zu zweit nebeneinander, durchnummeriert links–rechts–links; Zeilenabstand kleiner
    body = [L('Haupttext %d' % k, 200, 2280, 400 + 52 * k) for k in range(6)]
    fn = [L('%d) Ebd. S. %d.' % (2 * k + 1, k), 200, 1100, 900 + 40 * k) for k in range(3)] + \
         [L('%d) Vgl. oben.' % (2 * k + 2), 1300, 2200, 900 + 40 * k) for k in range(3)]
    lines = body + fn
    random.Random(3).shuffle(lines)
    pagexml.classify(lines)
    assert [d['kind'] for d in lines] == ['body'] * 6 + ['fn'] * 6
    assert texte(lines)[6:] == ['1) Ebd. S. 0.', '2) Vgl. oben.', '3) Ebd. S. 1.', '4) Vgl. oben.', '5) Ebd. S. 2.', '6) Vgl. oben.']


def test_zwei_spalten_und_fussnoten_darunter():
    li, re = spalten(5)
    fn = [L('1) Anmerkung, erste Zeile', 200, 1500, 900), L('zweite Zeile der Anmerkung', 200, 1400, 940)]
    lines = re + li + fn
    pagexml.classify(lines)
    assert [d['kind'] for d in lines] == ['body'] * 10 + ['fn'] * 2
    assert texte(lines) == ['L%d' % k for k in range(5)] + ['R%d' % k for k in range(5)] + ['1) Anmerkung, erste Zeile', 'zweite Zeile der Anmerkung']


def test_inhaltsverzeichnis_bleibt_zeilenweise():
    # Kapitel links, Seitenzahl rechts: die Zahlen sind schmal, das sind keine Spalten
    lines = []
    for k in range(6):
        lines += [L('Kapitel %d' % k, 200, 1200, 400 + 52 * k), L('%d' % (10 + k), 2150, 2280, 400 + 52 * k)]
    pagexml.classify(lines)
    assert texte(lines) == [t for k in range(6) for t in ('Kapitel %d' % k, '%d' % (10 + k))]


def test_unterschrift_neben_gedicht_und_absaetze_untereinander():
    gedicht = [L('Vers %d' % k, 200, 1100, 400 + 52 * k) for k in range(6)]
    # eine einzelne Zeile rechts daneben: keine Spalte
    lines = gedicht + [L('Goethe', 1800, 2100, 660)]
    pagexml.classify(lines)
    assert texte(lines) == ['Vers 0', 'Vers 1', 'Vers 2', 'Vers 3', 'Vers 4', 'Vers 5', 'Goethe']
    # zwei schmale Absätze untereinander, der zweite eingerückt bis rechts: nicht nebeneinander, also keine Spalten
    lines = [L('links %d' % k, 200, 1100, 400 + 52 * k) for k in range(4)] + [L('rechts %d' % k, 1300, 2200, 700 + 52 * k) for k in range(4)]
    pagexml.classify(lines)
    assert texte(lines) == ['links %d' % k for k in range(4)] + ['rechts %d' % k for k in range(4)]


def test_drei_spalten_bleiben_wie_bisher():
    lines = []
    for k in range(5):
        lines += [L('A%d' % k, 200, 850, 400 + 52 * k), L('B%d' % k, 900, 1550, 400 + 52 * k), L('C%d' % k, 1600, 2280, 400 + 52 * k)]
    pagexml.classify(lines)
    assert texte(lines) == [t for k in range(5) for t in ('A%d' % k, 'B%d' % k, 'C%d' % k)]


PAGE_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<PcGts xmlns="http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15">
 <Page imageFilename="s.png" imageWidth="2480" imageHeight="3508">%s</Page></PcGts>'''
REGION = '<TextRegion id="%s"><Coords points="%d,300 %d,300 %d,1200 %d,1200"/>%s</TextRegion>'
LINE = ('<TextLine id="%(id)s"><Coords points="%(x0)d,%(y0)d %(x1)d,%(y0)d %(x1)d,%(y1)d %(x0)d,%(y1)d"/>'
        '<Baseline points="%(x0)d,%(bl)d %(x1)d,%(bl)d"/><TextEquiv><Unicode>%(text)s</Unicode></TextEquiv></TextLine>')


def test_page_xml_mit_zwei_textregionen(tmp_path):
    def region(rid, x0, x1, texte, schief=0):
        ls = ''.join(LINE % dict(id='%s_%d' % (rid, k), x0=x0, x1=x1, y0=360 + 52 * k + schief, y1=412 + 52 * k + schief,
                                 bl=400 + 52 * k + schief, text=t) for k, t in enumerate(texte))
        return REGION % (rid, x0, x1, x1, x0, ls)
    # Transkribus schreibt die Regionen in seiner Reihenfolge – hier absichtlich die rechte zuerst
    xml = PAGE_XML % (region('r2', 1300, 2280, ['Nord-', 'amerika ist', 'weit weg.']) +
                      region('r1', 200, 1180, ['Die Kolo-', 'nisten zogen', 'nach Ruß-', 'land.'], schief=5))
    f = str(tmp_path / '0001_s.xml')
    with open(f, 'w', encoding='utf-8') as o:
        o.write(xml)
    W, H, img, lines = pagexml.parse_page(f)
    assert texte(lines) == ['Die Kolo-', 'nisten zogen', 'nach Ruß-', 'land.', 'Nord-', 'amerika ist', 'weit weg.']
    assert [d['id'] for d in lines] == ['r1_0', 'r1_1', 'r1_2', 'r1_3', 'r2_0', 'r2_1', 'r2_2']


TSV_HEAD = 'level\tpage_num\tblock_num\tpar_num\tline_num\tword_num\tleft\ttop\twidth\theight\tconf\ttext'


def tsv_block(blk, x0, texte, schief=0):
    rows = []
    for k, t in enumerate(texte):
        y = 400 + 60 * k + schief
        rows.append((4, 1, blk, 1, k + 1, 0, x0, y, 900, 50, -1, ''))
        for i, w in enumerate(t.split()):
            rows.append((5, 1, blk, 1, k + 1, i + 1, x0 + 450 * i, y, 400, 50, 90.0, w))
    return rows


def test_tesseract_bloecke_spaltenweise(monkeypatch):
    # Tesseract (psm 3) liefert je Spalte einen Block; die Zeilen kommen mit ihrer Lage, die Ordnung macht classify
    rows = tsv_block(1, 200, ['Die Kolo-', 'nisten zogen', 'nach Ruß-', 'land fort.']) + \
        tsv_block(2, 1300, ['Nord-', 'amerika ist', 'weit weg', 'von hier.'], schief=7)
    tsv = '\n'.join([TSV_HEAD] + ['\t'.join(map(str, r)) for r in rows])
    monkeypatch.setattr(ocr.subprocess, 'run', lambda cmd, **kw: types.SimpleNamespace(returncode=0, stdout=tsv.encode('utf-8'), stderr=b''))
    lines, words = ocr.ocr_image('tesseract', 'x.png', 'frak2021')
    ocr.page_lines(lines, 3508)
    # Trennstriche gelten innerhalb der Spalte: »Kolo¬ / nisten«, aber nicht von »land fort.« nach »Nord-«
    assert texte(lines) == ['Die Kolo¬', 'nisten zogen', 'nach Ruß¬', 'land fort.', 'Nord¬', 'amerika ist', 'weit weg', 'von hier.']
    assert pagexml.page_text(lines) == ['# ', 'Die Kolo¬', 'nisten zogen', 'nach Ruß¬', 'land fort.', 'Nord¬', 'amerika ist', 'weit weg', 'von hier.']


def test_textebene_zwei_spalten():
    # Wörter einer PDF-Textebene (x0, y0, x1, y1, text, grundlinie) in zwei Spalten, im PDF zeilenweise verschränkt
    words = []
    for k in range(4):
        bl = 400 + 60 * k
        for i, w in enumerate(('L%d' % k, 'links', 'Text')):
            words.append((200 + 250 * i, bl - 40, 400 + 250 * i, bl + 8, w, bl))
        for i, w in enumerate(('R%d' % k, 'rechts', 'Text')):
            words.append((1300 + 250 * i, bl - 40, 1500 + 250 * i, bl + 8, w, bl))
    lines = ocr.group_words(words)
    ocr.page_lines(lines, 3508)
    assert texte(lines) == ['L%d links Text' % k for k in range(4)] + ['R%d rechts Text' % k for k in range(4)]
