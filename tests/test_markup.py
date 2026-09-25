"""Auszeichnung im Text (#38): Tabellen aus getrennten Zeilen, Überschriften – XHTML wie im EPUB, Zeilenzahl bleibt."""
import korrlib
from test_server import words

EIMER = ['im Jahre 1811', '16 842 Eimer,', '1812-', '12 409', '1813-', '5400', '1814-', '2411']   # das Beispiel aus dem Issue


def test_tabelle_aus_getrennten_zeilen():
    t = korrlib.make_table(EIMER, 2)
    assert t == ['<table><tr><td>im Jahre 1811</td>', '<td>16 842 Eimer,</td></tr>', '<tr><td>1812-</td>', '<td>12 409</td></tr>',
                 '<tr><td>1813-</td>', '<td>5400</td></tr>', '<tr><td>1814-</td>', '<td>2411</td></tr></table>']
    assert len(t) == len(EIMER)                                   # jede Zeile bleibt eine Zeile: die Bildzuordnung hält
    import xml.etree.ElementTree as ET
    rows = ET.fromstring(''.join(t)).findall('tr')                # zusammengesetzt ist es gültiges XHTML
    assert [[c.text for c in r] for r in rows][:2] == [['im Jahre 1811', '16 842 Eimer,'], ['1812-', '12 409']]
    assert korrlib.make_table(t, 2) == t                          # noch einmal anwenden ändert nichts
    assert [korrlib.TABLETAG.sub('', l) for l in t] == EIMER      # und es lässt sich spurlos zurücknehmen


def test_tabelle_kopfzeile_leerzeilen_und_rest():
    t = korrlib.make_table(['Jahr', 'Eimer', 'Preis', '', '1811', '16842', '3 fl', '1812'], 3, head=True)
    assert t == ['<table><tr><th>Jahr</th>', '<th>Eimer</th>', '<th>Preis</th></tr>', '', '<tr><td>1811</td>', '<td>16842</td>', '<td>3 fl</td></tr>',
                 '<tr><td>1812</td><td></td><td></td></tr></table>']   # Leerzeile bleibt leer, die letzte Reihe wird aufgefüllt
    lines = ['Text davor'] + t + ['Text danach']
    assert [korrlib.table_block(lines, i) for i in (0, 1, 5, 8, 9)] == [None, (1, 8), (1, 8), (1, 8), None]


def test_ueberschrift():
    assert korrlib.heading('Erstes Kapitel', 2) == '<h2>Erstes Kapitel</h2>'
    assert korrlib.heading('<h2>Erstes Kapitel</h2>', 3) == '<h3>Erstes Kapitel</h3>'
    assert korrlib.heading('<h3>Erstes Kapitel</h3>', 0) == 'Erstes Kapitel' and korrlib.heading('  ', 1) == '  '


def test_ueberschriften_fuer_das_inhaltsverzeichnis(app):
    """Taste I und die Lesezeichen im PDF: alle Überschriften in Lesereihenfolge; zwei Zeilen derselben Ebene untereinander
    sind eine Überschrift (auch über eine Trennung hinweg), Schrift-Auszeichnung fällt weg, eine Leerzeile trennt."""
    pages = {'002': ['# 8', '<h1>Drittes Kapitel.</h1>', '<h1>Die Reise nach <em>Odessa</em>.</h1>', 'Text.', '<h2>Die Ge¬</h2>', '<h2>fahren</h2>'],
             '001': ['# 7', '<h1>Vorwort</h1>', '', '<h1>zur zweiten Auflage</h1>', '<h2>Anmerkung</h2>', '<h1></h1>']}
    assert korrlib.headings(pages) == [('001', 1, 1, 'Vorwort'), ('001', 3, 1, 'zur zweiten Auflage'), ('001', 4, 2, 'Anmerkung'),
                                       ('002', 1, 1, 'Drittes Kapitel. Die Reise nach Odessa.'), ('002', 4, 2, 'Die Gefahren')]
    assert app.get('/api/headings')[1]['items'] == []
    old = app.text('002')[1]
    app.post('/api/markup/002', dict(kind='heading', line=1, level=1, old=old))
    assert app.get('/api/headings')[1]['items'] == [dict(page='002', line=1, level=1, text=old, printed='6')]  # gedruckte Seite aus »# 6«


def test_wortpruefung_uebergeht_die_auszeichnung():
    toks, joined = korrlib.joined_tokens(['<table><tr><td>ber Eimer</td>', '<td>Zu¬</td>', '<h2>kunft</h2>', 'a < b und <unbekannt>'])
    assert toks[0] == [(15, 'ber'), (19, 'Eimer')]                # Positionen gelten für die echte Zeile
    assert [w for s, w in toks[3]] == ['a', 'b', 'und', 'unbekannt']  # nur bekannte Elemente zählen als Auszeichnung
    assert korrlib.corpus_freq({'001': ['<td>Eimer</td>']}) == {'Eimer': 1}


def test_tabelle_und_ueberschrift_ueber_die_schnittstelle(app):
    t = app.text('001')
    code, d = app.post('/api/markup/001', dict(kind='table', start=1, end=4, cols=2, old=t[1:5]))
    assert code == 200 and len(d['lines']) == len(t) and None not in d['geo'][1:5]
    assert d['lines'][1].startswith('<table><tr><td>Die Kolonisten') and d['lines'][4].endswith('</td></tr></table>')
    assert words(d) == ['ber', 'baß', 'ber']                       # td und tr sind keine Wörter; die echten Fehler bleiben
    assert [f['start'] for f in d['flags']][0] == len('<td>')      # die Markierung sitzt auf dem Wort, nicht auf der Auszeichnung
    assert app.text('001')[1:5] == d['lines'][1:5] and app.log()[-1][1] == 'edit'
    # Serienkorrektur findet das Wort auch in der Zelle
    items = app.get('/api/occurrences?word=ber')[1]['items']
    app.post('/api/series', dict(word='ber', new='der', items=items))
    assert app.text('001')[2] == '<td>der Weg war weit. Die Zu¬</td></tr>'
    assert app.post('/api/markup/001', dict(kind='heading', line=2, level=1, old=app.text('001')[2]))[0] == 400   # keine Überschrift in einer Tabelle
    # zurücknehmen: von irgendeiner Zeile der Tabelle aus
    code, d = app.post('/api/markup/001', dict(kind='untable', line=3))
    assert code == 200 and d['lines'][1] == 'Die Kolonisten zogen nach Rußland und' and '<' not in ''.join(d['lines'][1:5])
    assert app.post('/api/markup/001', dict(kind='untable', line=3))[0] == 400            # dort ist keine Tabelle mehr
    # Überschrift
    old = app.text('002')[1]
    d = app.post('/api/markup/002', dict(kind='heading', line=1, level=2, old=old))[1]
    assert d['lines'][1] == '<h2>%s</h2>' % old
    assert app.post('/api/markup/002', dict(kind='heading', line=1, level=0, old='veraltet'))[0] == 409   # extern geändert
    assert app.post('/api/markup/001', dict(kind='table', start=4, end=6, cols=2, old=app.text('001')[4:7]))[0] == 409  # über den Fußnotentrenner hinweg


def test_zeile_teilen_und_verbinden_mit_bildzuordnung(app):
    import json, os
    t = app.text('001')
    old = t[1]                                                     # 'Die Kolonisten zogen nach Rußland und'
    g0 = app.get('/api/page/001')[1]['geo'][1]
    pos = old.index(' nach')
    code, d = app.post('/api/lines/001', dict(kind='split', line=1, old=old, text=old.replace('zogen', 'gingen'), pos=pos + 1))
    assert code == 200 and d['lines'][1:3] == ['Die Kolonisten gingen', 'nach Rußland und'] and len(d['lines']) == len(t) + 1
    a, b = d['geo'][1], d['geo'][2]                                # der Bildausschnitt ist mitgeteilt: gleiche Höhe, nebeneinander
    assert None not in d['geo'][1:6] and (a['y0'], a['y1']) == (b['y0'], b['y1']) == (g0['y0'], g0['y1'])
    assert a['x0'] == g0['x0'] and a['x1'] == b['x0'] and b['x1'] == g0['x1'] and g0['x0'] < a['x1'] < g0['x1']
    assert d['geo'][3]['y0'] > a['y0']                             # die folgenden Zeilen behalten ihre Bildzeile
    assert app.log()[-1][1] == 'teilen'
    assert len(json.load(open(os.path.join(app.folder, 'lines.json'), encoding='utf-8'))['001']['lines']) == 7  # vorher 6
    # wieder verbinden: alles wie vorher (bis auf die Korrektur)
    code, d = app.post('/api/lines/001', dict(kind='join', line=1, old=d['lines'][1:3]))
    assert code == 200 and d['lines'] == [t[0], 'Die Kolonisten gingen nach Rußland und'] + t[2:] and d['geo'][1] == g0
    # getrenntes Wort: beim Verbinden fällt das ¬ weg. Die Zeilen stehen auch im Bild untereinander: erst nach Rückfrage
    assert app.post('/api/lines/001', dict(kind='join', line=2, old=app.text('001')[2:4]))[0] == 422
    d = app.post('/api/lines/001', dict(kind='join', line=2, old=app.text('001')[2:4], force=True))[1]
    assert d['lines'][2] == 'ber Weg war weit. Die Zukunft lag vor ihnen, baß sie' and None not in d['geo'][1:4]
    # Schutz: extern geändert, Kopfzeile, Fußnotentrenner, Teilen am Rand
    cur = app.text('001')
    assert app.post('/api/lines/001', dict(kind='split', line=1, old='veraltet', text='x y', pos=1))[0] == 409
    assert app.post('/api/lines/001', dict(kind='split', line=0, old=cur[0], text=cur[0], pos=1))[0] == 409
    assert app.post('/api/lines/001', dict(kind='join', line=3, old=cur[3:5]))[0] == 409            # Zeile 4 ist '---'
    assert app.post('/api/lines/001', dict(kind='split', line=1, old=cur[1], text=cur[1], pos=0))[0] == 400


def test_teilen_in_einer_tabelle_rueckt_die_spalten_zurecht(app):
    """Der Anlass: Die Texterkennung hat einen Zeilenwechsel nicht erkannt, zwei Zellen stehen in einer Zeile – ab dort
    verrutschen die Spalten. Teilen zählt die Tabelle neu durch."""
    import os
    rows = ['# 9', 'im Jahre 1811', '16 842 Eimer,', '1812- 12 409', '1813-', '5400', 'Text danach']
    with open(os.path.join(app.folder, '002.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(rows) + '\n')
    d = app.post('/api/markup/002', dict(kind='table', start=1, end=5, cols=2, old=rows[1:6]))[1]
    assert d['lines'][3:6] == ['<tr><td>1812- 12 409</td>', '<td>1813-</td></tr>', '<tr><td>5400</td><td></td></tr></table>']  # verrutscht
    line = d['lines'][3]
    code, d = app.post('/api/lines/002', dict(kind='split', line=3, old=line, text=line, pos=line.index(' 12 409') + 1))
    assert code == 200 and d['lines'][1:] == ['<table><tr><td>im Jahre 1811</td>', '<td>16 842 Eimer,</td></tr>', '<tr><td>1812-</td>', '<td>12 409</td></tr>',
                                              '<tr><td>1813-</td>', '<td>5400</td></tr></table>', 'Text danach']
    assert app.post('/api/lines/002', dict(kind='split', line=3, old=d['lines'][3], text=d['lines'][3], pos=2))[0] == 400  # mitten in <tr>
    assert app.post('/api/lines/002', dict(kind='split', line=3, old=d['lines'][3], text=d['lines'][3], pos=len('<tr><td>')))[0] == 400  # keine leere Zelle
    d = app.post('/api/lines/002', dict(kind='join', line=3, old=d['lines'][3:5]))[1]                                      # und zurück
    assert d['lines'][3:6] == ['<tr><td>1812- 12 409</td>', '<td>1813-</td></tr>', '<tr><td>5400</td><td></td></tr></table>']


def test_verbundene_zeilen_wieder_trennen(app):
    """Dreimal V auf untereinanderstehende Zeilen (so geschehen in einem echten Buch: vier gedruckte Zeilen in einer):
    Umschalt+V trennt sie nach dem Protokoll wieder, jede Zeile bekommt ihren Teil des Bildrahmens zurück."""
    t = app.text('001')
    g0 = app.get('/api/page/001')[1]['geo']
    for _ in range(3):
        cur = app.text('001')
        assert app.post('/api/lines/001', dict(kind='join', line=1, old=cur[1:3], force=True))[0] == 200
    long_ = app.text('001')[1]
    assert long_ == 'Die Kolonisten zogen nach Rußland und ber Weg war weit. Die Zukunft lag vor ihnen, baß sie ber Heimat gedachten.'
    for _ in range(3):
        code, d = app.post('/api/lines/001', dict(kind='unjoin', line=1, old=app.text('001')[1]))
        assert code == 200 and app.log()[-1][1] == 'teilen'
    assert d['lines'] == t and d['geo'] == g0  # der hohe Rahmen ist waagrecht zurückgeteilt, genau auf die Zeilen
    assert app.post('/api/lines/001', dict(kind='unjoin', line=1, old=t[1]))[0] == 400    # nie verbunden
    # Umschalt+Enter mitten in einer mehrzeiligen Zeile teilt den Rahmen ebenfalls waagrecht
    for _ in range(2):
        cur = app.text('001')
        app.post('/api/lines/001', dict(kind='join', line=1, old=cur[1:3], force=True))
    j = app.text('001')[1]
    code, d = app.post('/api/lines/001', dict(kind='split', line=1, old=j, text=j, pos=j.index('ber Weg')))
    assert code == 200 and d['geo'][1] == g0[1] and d['geo'][2]['y0'] == g0[2]['y0'] and d['geo'][2]['y1'] == g0[3]['y1']


def test_alte_verbindung_nach_zeilenabstand_trennen(tmp_path):
    """Aus einer früheren Programmfassung verbunden, ohne gemerkte Rahmen: Umschalt+V teilt den hohen Rahmen nach dem
    Zeilenabstand der übrigen Zeilen – bei gleichmäßigem Satz genau auf die gedruckten Zeilen."""
    import json, server
    from conftest import png
    folder = tmp_path / 'buch'
    (folder / 'img').mkdir(parents=True)
    rows = ['Zeile %d des Vorworts mit etwas Text.' % n for n in range(1, 11)]
    (folder / '001.txt').write_text('# 9\n' + '\n'.join(rows) + '\n', encoding='utf-8')
    geo = [dict(text='9', x0=100, x1=200, y0=40, y1=80, kind='head')]
    geo += [dict(text=r, x0=100, x1=900, y0=100 + 53 * n, y1=150 + 53 * n, kind='body') for n, r in enumerate(rows)]
    json.dump({'001': dict(w=1000, h=1500, lines=geo)}, open(folder / 'lines.json', 'w', encoding='utf-8'))
    (folder / 'img' / '001.png').write_bytes(png(500, 750))
    b = server.Book(str(folder))
    b.refresh()
    g0 = b.page_data('001')['geo']
    for _ in range(3):
        assert b.join_lines('001', 1, b.pages['001'][1:3], force=True)[1] is None
    for g in b.geo['001']['lines']:
        g.pop('vorher', None)  # so sah lines.json vor dieser Fassung aus
    for _ in range(3):
        assert b.unjoin_line('001', 1, b.pages['001'][1])[1] is None
    d = b.page_data('001')
    assert d['lines'][1:] == rows and d['geo'] == g0
