"""Fußnoten ohne Fußnotenstrich: Die Erkennung hat sie nicht abgetrennt und ihre hochgestellten Nummern verlesen (»3!«,
»°«). Das Programm erkennt sie am großen Abstand davor und an der kleineren Schrift und setzt beim ersten Öffnen den
Strich, wie mit F."""
import os, json
from conftest import png

TEXT = 'Die Kolonisten zogen im Frühjahr nach Rußland, und der Weg dorthin war weit und beschwerlich für alle'  # ~100 Zeichen
FUSS = '3! Ebenda, S. 46; vgl. Stumpp, Die deutschen Kolonien im Schwarzmeergebiet, Stuttgart 1922, S. 6 und S. 12 f.'


def make(folder, footnotes=(True, True, True, False)):
    """Seiten mit acht Zeilen Haupttext (1800 Bildpunkte breit, Abstand 60); wo footnotes, danach nach großem Abstand zwei
    Fußnotenzeilen gleicher Breite mit mehr Zeichen (kleinere Schrift). Die letzte Seite hat stattdessen nach einem
    großen Abstand einen gewöhnlichen Absatz – das sind keine Fußnoten."""
    os.makedirs(os.path.join(folder, 'img'))
    geo = {}
    for n, fn in enumerate(footnotes):
        pg = '%03d' % (n + 1)
        body = [TEXT] * 8
        tail = [FUSS, FUSS[3:] + ' Weitere Angaben.'] if fn else [TEXT, TEXT]
        lines = ['# %d' % (5 + n)] + body + tail
        with open(os.path.join(folder, pg + '.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines) + '\n')
        gl, y = [dict(text=str(5 + n), x0=900, x1=1000, y0=40, y1=80, kind='head')], 100
        for k, t in enumerate(body + tail):
            if k == len(body):
                y += 150  # der Abstand vor dem Fußnotenblock (bzw. dem neuen Absatz)
            gl.append(dict(text=t, x0=100, x1=1900, y0=y, y1=y + 45, kind='body'))
            y += 60
        geo[pg] = dict(w=2000, h=3000, lines=gl)
        with open(os.path.join(folder, 'img', pg + '.png'), 'wb') as f:
            f.write(png(500, 750))
    json.dump(geo, open(os.path.join(folder, 'lines.json'), 'w', encoding='utf-8'))


def test_fussnoten_ohne_strich(tmp_path):
    import server
    make(str(tmp_path / 'buch'))
    b = server.Book(str(tmp_path / 'buch'))
    b.refresh()
    assert b.footnote_starts() == {'001': 9, '002': 9, '003': 9}
    assert b.auto_footnotes() == 3 and b.auto_footnotes() == 0
    d = b.page_data('001')
    assert d['lines'][9] == '---' and d['lines'][10].startswith('3! Ebenda') and len(d['geo']) == len(d['lines'])
    assert '---' not in b.pages['004']
    log = [l.split('\t') for l in open(b.klogpath, encoding='utf-8').read().splitlines()]
    assert [r[1] for r in log] == ['fnsep'] * 3 + ['fussnoten']  # gewöhnliche Einträge wie mit F, dazu die Merkzeile
    assert server.Book(str(tmp_path / 'buch')).auto_footnotes() == 0  # einmal je Buch
    # mit F auf der ersten Fußnote wieder entfernt
    assert b.fnsep('001', 10, b.pages['001'][10])['action'] == 'entfernt' and '---' not in b.pages['001']


def test_zu_wenige_seiten_mit_fussnoten(tmp_path):
    """Das Muster auf nur zwei Seiten – oder auf weniger als einem Zehntel der Seiten: Rauschen, keine Fußnoten."""
    import server
    make(str(tmp_path / 'zwei'), (True, True, False, False))
    z = server.Book(str(tmp_path / 'zwei'))
    z.refresh()
    assert len(z.pages) == 4 and z.footnote_starts() == {}
    make(str(tmp_path / 'selten'), (True, True, True) + (False,) * 30)
    s = server.Book(str(tmp_path / 'selten'))
    s.refresh()
    assert s.footnote_starts() == {} and s.auto_footnotes() == 0 and not os.path.exists(s.klogpath)


def test_hochgestellte_ziffern():
    import korrlib
    assert korrlib.sup_markup('eingewiesen.³⁸ Über') == 'eingewiesen.<sup>38</sup> Über'
    assert korrlib.sup_markup('ohne') == 'ohne' and korrlib.sup_markup('a¹ b²⁰') == 'a<sup>1</sup> b<sup>20</sup>'


def fnbuch(folder):
    """Drei Seiten mit Fußnoten: ein »*« und angeklebte Ziffern, wo die Erkennung die hochgestellten Zahlen verlas, eine
    schon hochgestellte Nummer, eine Stellenangabe »S.12«, ein altes »*)«; die Nummern der Fußnoten unten sind lesbar."""
    os.makedirs(folder)
    seiten = {'001': ['# 5', 'Die Kolonisten zogen.* Der Weg war weit.2 Sie kamen an.', '---', '1 Ebenda.', '2 Vgl. Stumpp.'],
              '002': ['# 6', 'Im Jahr 1812 zogen sie, S.12 steht es. Die Reise dauerte lange.*', '---', '3 Ebenda S. 12.'],
              '003': ['# 7', 'Sie kamen an.<sup>4</sup> Dann weiter.* Das Dorf hieß *) Neudorf.', '---', '4 Ebenda.', '5 Ebenda.'],
              '004': ['# 8', 'Ohne Fußnoten.* Das bleibt.']}
    for pg, lines in seiten.items():
        with open(os.path.join(folder, pg + '.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines) + '\n')


def test_fussnotenzeichen_vorschlagen(tmp_path):
    import server
    fnbuch(str(tmp_path / 'buch'))
    b = server.Book(str(tmp_path / 'buch'))
    b.refresh()
    refs = {pg: [(f['line'], f['word'], f['expect']) for f in v] for pg, v in b.fnrefs.items()}
    assert refs == {'001': [(1, '*', 1), (1, '2', 2)], '002': [(1, '*', 3)], '003': [(1, '*', 5)]}
    f = [x for x in b.page_data('001')['flags'] if x['kind'] == 'fnref']
    assert [(x['start'], x['len']) for x in f] == [(21, 1), (40, 1)]
    # Hochgestellt gespeichert: aus dem Bearbeitungsfeld kommen hochgestellte Ziffern, in die Datei kommt <sup>
    old = b.pages['001'][1]
    d = b.edit('001', [dict(line=1, old=old, new=old.replace('zogen.*', 'zogen.¹').replace('weit.2', 'weit.²'))])
    assert d['lines'][1] == 'Die Kolonisten zogen.<sup>1</sup> Der Weg war weit.<sup>2</sup> Sie kamen an.'
    assert not [x for x in d['flags'] if x['kind'] == 'fnref'] and [f['expect'] for f in b.fnrefs['002']] == [3]
    # auch beim Teilen der Zeile
    old = b.pages['002'][1]
    d, err = b.split_line('002', 1, old, old.replace('lange.*', 'lange.³'), old.index('Die Reise'))
    assert err is None and d['lines'][2] == 'Die Reise dauerte lange.<sup>3</sup>'
    # im Zitat einer Notiz stehen keine Fußnotenzeichen
    b.settings['notizen'] = str(tmp_path / 'notizen')
    r, err = b.make_note('001', b.pages['001'][1])
    assert err is None and r['text'] == 'Die Kolonisten zogen. Der Weg war weit. Sie kamen an.'
