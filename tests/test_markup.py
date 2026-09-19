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
