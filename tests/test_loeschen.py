"""Rauschzeilen vom Scanrand löschen (#73): Strg/⌘+⌫ im Lesemodus, Strg/⌘+Z holt sie zurück – immer samt Bildzeile,
damit die Zeilen dahinter ihre Bildzuordnung behalten."""
import os, json


def geo_count(app, pg):
    return len(json.load(open(os.path.join(app.folder, 'lines.json'), encoding='utf-8'))[pg]['lines'])


def test_loeschen_und_zurueckholen(app):
    t = app.text('001')
    p0 = app.get('/api/page/001')[1]
    # eine Zeile: die Zeilen dahinter behalten ihre Bildzeile
    code, d = app.post('/api/lines/001', dict(kind='delete', line=2, old=[t[2]]))
    assert code == 200 and d['lines'] == t[:2] + t[3:] and geo_count(app, '001') == 5  # vorher 6
    assert d['geo'][1] == p0['geo'][1] and d['geo'][2] == p0['geo'][3] and d['geo'][5] == p0['geo'][6]
    kind = app.log()[-1][1]
    assert kind.startswith('loeschen:') and app.log()[-1][2:] == ['001', '3', t[2], '']
    # zwei markierte Zeilen auf einmal: ein Eintrag je Zeile, beide an derselben Stelle
    code, d = app.post('/api/lines/001', dict(kind='delete', line=2, old=[t[3], t[4]]))
    assert code == 200 and d['lines'] == [t[0], t[1], '---', t[6]] and d['geo'][3] == p0['geo'][6] and geo_count(app, '001') == 3
    assert [r[2:] for r in app.log()[-2:]] == [['001', '3', t[3], ''], ['001', '3', t[4], '']] and app.log()[-1][1] != kind
    # Strg+Z: erst die beiden zuletzt gelöschten Zeilen, dann die erste – jede an ihrer Stelle, mit ihrer Bildzeile
    assert app.post('/api/undelete', {})[1] == dict(page='001', line=2, n=2)
    d = app.get('/api/page/001')[1]
    assert d['lines'] == t[:2] + t[3:] and d['geo'][2] == p0['geo'][3] and d['geo'][3] == p0['geo'][4]
    assert app.post('/api/undelete', {})[1] == dict(page='001', line=2, n=1)
    d = app.get('/api/page/001')[1]
    assert d['lines'] == t and d['geo'] == p0['geo'] and geo_count(app, '001') == 6
    assert [r[1][:8] for r in app.log()[-3:]] == ['zurueck:'] * 3 and app.log()[-1][4:] == ['', t[2]]
    assert app.post('/api/undelete', {})[1] == dict(error='nichts')


def test_loeschen_geschuetzt(app):
    t = app.text('001')
    assert app.post('/api/lines/001', dict(kind='delete', line=0, old=[t[0]]))[0] == 400        # Kopfzeile
    assert app.post('/api/lines/001', dict(kind='delete', line=5, old=[t[5]]))[0] == 400        # Fußnotenstrich
    assert app.post('/api/lines/001', dict(kind='delete', line=4, old=[t[4], t[5]]))[0] == 400  # auch mitten in der Markierung
    assert app.post('/api/lines/001', dict(kind='delete', line=1, old=['anders']))[0] == 409    # extern geändert
    assert app.post('/api/lines/001', dict(kind='delete', line=6, old=[t[6], 'x']))[0] == 409   # über das Seitenende
    assert app.text('001') == t and app.log() == []
    # Tabellenzeilen: die Auszeichnung ginge kaputt
    code, d = app.post('/api/markup/001', dict(kind='table', start=1, end=2, old=t[1:3]))
    assert code == 200
    assert app.post('/api/lines/001', dict(kind='delete', line=2, old=[d['lines'][2]]))[0] == 400


def test_seitenzahl_unten_bleibt_rauschen_darunter_geht(tmp_path):
    import server
    folder = tmp_path / 'buch'
    folder.mkdir()
    for i in range(6):
        (folder / ('%03d.txt' % (i + 1))).write_text('# \nDie Kolonisten zogen.\n%d\nBTB\n' % (11 + i), encoding='utf-8')
    b = server.Book(str(folder))
    b.refresh()
    assert b.feet['002'][1] == 2
    assert b.delete_lines('002', 2, ['12']) == (None, 400)
    d, err = b.delete_lines('002', 3, ['BTB'])
    assert err is None and d['lines'] == ['# ', 'Die Kolonisten zogen.', '12'] and d['geo'] is None  # ohne lines.json geht es auch


def test_zurueckholen_wenn_die_seite_sich_verschoben_hat(tmp_path):
    """Seit dem Löschen kamen Zeilen davor hinzu: die Zeile kommt dorthin zurück, wo ihre Nachbarn jetzt stehen.
    Sind beide Nachbarn geändert, bleibt sie gelöscht, statt an einer falschen Stelle zu landen."""
    import server
    from conftest import make_book
    make_book(str(tmp_path / 'buch'))
    b = server.Book(str(tmp_path / 'buch'))
    b.refresh()
    t = list(b.pages['001'])
    assert b.delete_lines('001', 4, [t[4]])[1] is None
    old = t[1]
    assert b.split_line('001', 1, old, old, old.index(' nach'))[1] is None  # davor eine Zeile mehr
    assert b.undelete() == dict(page='001', line=5, n=1)
    d = b.page_data('001')
    assert d['lines'][5] == t[4] and len(d['geo']) == len(d['lines']) and d['geo'][5]['y0'] == d['geo'][4]['y0'] + 30
    # beide Nachbarn geändert: die Zeile davor berichtigt, der Fußnotenstrich danach entfernt
    assert b.delete_lines('001', 5, [t[4]])[1] is None
    assert b.edit('001', [dict(line=4, old=t[3], new='kunft lag vor ihnen, daß sie')])
    assert b.fnsep('001', 6, t[6])['action'] == 'entfernt'
    assert b.undelete() == dict(error='verschoben') and t[4] not in b.pages['001']
    assert b.deleted()[-1]['lines'] == [t[4]]  # gemerkt bleibt sie
