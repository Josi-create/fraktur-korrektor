"""Absätze (#67): <p> am Anfang der Zeile, mit der ein Absatz beginnt – beim ersten Öffnen am Einzug erkannt, mit A von
Hand gesetzt oder entfernt, mit U zurückgenommen."""
import os, json
from conftest import png, start

# Zeilenhöhe 40, linker Rand 100; ein Absatz ist 50 eingerückt (1,25 Zeilenhöhen)
SEITEN = {
    '001': [('# 5', 100), ('<h2>Erstes Kapitel.</h2>', 400),
            ('Die Kolonisten zogen nach Rußland und', 100), ('der Weg war weit. Die Zu¬', 100),
            ('kunft lag vor ihnen, daß sie', 150),            # eingerückt, aber nach ¬: kein Absatz
            ('der Heimat gedachten.', 100),
            ('Im Frühjahr brachen sie auf, und', 150),         # Absatz
            ('sie kamen bis an die Donau. Dort', 100),
            ('— 5 —', 450),                                    # zentriert: weit mehr als 3 Zeilenhöhen
            ('warteten sie auf die Schiffe', 100),
            ('und auf gutes Wetter.', 100)],
    '002': [('# 6', 100),
            ('Der Vater und der Sohn gingen', 150),            # Absatz am Seitenanfang: 001 endet mit Punkt
            ('voraus, die Mutter folgte mit', 100),
            ('den Kindern', 100),
            ('auf dem Wagen, der langsam fuhr', 150),         # eingerückt, aber davor kein Satzende: kein Absatz
            ('und bei jedem Stein ächzte.', 100),
            ('So kamen sie nach Ulm.', 100)],
}


def make(folder):
    os.makedirs(os.path.join(folder, 'img'))
    geo = {}
    for pg, rows in SEITEN.items():
        with open(os.path.join(folder, pg + '.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(t for t, x in rows) + '\n')
        gl = [dict(text=t, x0=x, x1=900, y0=100 + 60 * n, y1=140 + 60 * n, kind='head' if n == 0 else 'body') for n, (t, x) in enumerate(rows)]
        geo[pg] = dict(w=1000, h=1500, lines=gl)
        with open(os.path.join(folder, 'img', pg + '.png'), 'wb') as f:
            f.write(png(500, 750))
    json.dump(geo, open(os.path.join(folder, 'lines.json'), 'w', encoding='utf-8'))


def test_absatzanfaenge_erkennen(tmp_path):
    import server
    make(str(tmp_path / 'buch'))
    b = server.Book(str(tmp_path / 'buch'))
    b.refresh()
    assert b.paragraph_starts() == {'001': [6], '002': [1]}
    # beim ersten Öffnen gesetzt, als Serie protokolliert – einmal je Buch
    assert b.auto_paragraphs() == 2 and b.auto_paragraphs() == 0
    assert b.pages['001'][6] == '<p>Im Frühjahr brachen sie auf, und' and b.pages['002'][1].startswith('<p>Der Vater')
    d = b.page_data('001')
    assert len(d['geo']) == len(d['lines']) and d['flags'] == []  # die Auszeichnung wird nicht geprüft
    assert server.Book(str(tmp_path / 'buch')).auto_paragraphs() == 0  # steht schon ein <p> im Buch: nichts mehr
    # U nimmt alles zurück; danach erkennt das Programm sie auch beim nächsten Öffnen nicht wieder
    sid = b.last_series()[0]
    assert sid.startswith('absaetze-') and b.series_undo() == dict(id=sid, done=2, skipped=0)
    assert not any('<p>' in l for lines in b.pages.values() for l in lines)
    assert server.Book(str(tmp_path / 'buch')).auto_paragraphs() == 0


def test_ohne_einzug_keine_absaetze(tmp_path):
    """Das Testbuch ohne Einzüge und ein Buch, in dem fast jede Zeile eingerückt ist: nichts setzen."""
    import server
    from conftest import make_book
    make_book(str(tmp_path / 'glatt'))
    b = server.Book(str(tmp_path / 'glatt'))
    assert b.auto_paragraphs() == 0 and not os.path.exists(b.klogpath)
    make(str(tmp_path / 'zickzack'))
    g = json.load(open(tmp_path / 'zickzack' / 'lines.json', encoding='utf-8'))
    for pg in g:
        for n, l in enumerate(g[pg]['lines'][1:]):
            l['x0'] = 100 + 50 * (n % 2)
    json.dump(g, open(tmp_path / 'zickzack' / 'lines.json', 'w', encoding='utf-8'))
    for pg in ('001', '002'):  # jede Zeile endet mit einem Satzzeichen
        p = tmp_path / 'zickzack' / (pg + '.txt')
        p.write_text(''.join(l.replace('¬', '').rstrip('.') + '.\n' if n else l + '\n' for n, l in enumerate(p.read_text(encoding='utf-8').splitlines())), encoding='utf-8')
    z = server.Book(str(tmp_path / 'zickzack'))
    z.refresh()
    assert len([i for v in z.paragraph_starts().values() for i in v]) > 0.25 * sum(len(v) for v in z.pages.values())
    assert z.auto_paragraphs() == 0


def test_absatz_von_hand_und_beim_oeffnen(tmp_path):
    make(str(tmp_path / 'buch'))
    p, c = start(tmp_path, str(tmp_path / 'buch'))
    try:
        code, o = c.get('/api/overview')
        assert code == 200 and o['absaetze'] == 2 and c.get('/api/overview')[1]['absaetze'] == 0
        assert c.get('/api/series_last')[1]['id'].startswith('absaetze-')
        # A: setzen und wieder entfernen
        t = c.text('001')
        code, d = c.post('/api/markup/001', dict(kind='para', line=2, old=t[2]))
        assert code == 200 and d['lines'][2] == '<p>' + t[2] and c.log()[-1][1] == 'edit'
        code, d = c.post('/api/markup/001', dict(kind='para', line=2, old=d['lines'][2]))
        assert code == 200 and d['lines'][2] == t[2]
        assert c.post('/api/markup/001', dict(kind='para', line=0, old=t[0]))[0] == 400   # Kopfzeile
        assert c.post('/api/markup/001', dict(kind='para', line=1, old=t[1]))[0] == 400   # Überschrift
        assert c.post('/api/markup/001', dict(kind='para', line=2, old='anders'))[0] == 409
        # Verbinden: ein Absatz beginnt nicht mitten in der Zeile
        code, d = c.post('/api/lines/001', dict(kind='join', line=5, old=t[5:7]))
        assert code == 200 and d['lines'][5] == 'der Heimat gedachten. Im Frühjahr brachen sie auf, und'
    finally:
        p.kill()
        p.wait()
