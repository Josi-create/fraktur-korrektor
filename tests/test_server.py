"""Die HTTP-Schnittstelle gegen ein Wegwerf-Buch (siehe conftest.py)."""


def words(data, kind=None):
    return [f['word'] for f in data['flags'] if kind in (None, f['kind'])]


def test_uebersicht_und_markierungen(app):
    code, ov = app.get('/api/overview')
    assert code == 200 and [p['page'] for p in ov['pages']] == ['001', '002']
    code, d = app.get('/api/page/001')
    # ber: unbekannt; baß: Falle; Vgl: Zusatzliste; Zu¬kunft: über die Trennung hinweg bekannt
    assert words(d) == ['ber', 'baß', 'ber']
    assert app.get('/api/page/999')[0] == 404


def test_bildzuordnung(app):
    d = app.get('/api/page/001')[1]
    assert len(d['geo']) == len(d['lines'])
    assert d['geo'][5] is None                      # Fußnotentrenner hat keine Bildzeile
    assert d['geo'][1] == dict(x0=50, x1=450, y0=80, y1=100)   # Maßstab 0.5
    assert app.raw('/img/001.png')[1][:4] == b'\x89PNG'


def test_korrektur_schreibt_datei_und_protokoll(app):
    old = app.text('002')[1]
    code, d = app.post('/api/edit/002', dict(edits=[dict(line=1, old=old, new='Der Vater und der Sohn.')]))
    assert code == 200 and words(d) == []
    assert app.text('002')[1] == 'Der Vater und der Sohn.'
    assert app.log()[-1][1:] == ['edit', '002', '2', old, 'Der Vater und der Sohn.']


def test_korrektur_konflikt_bei_extern_geaenderter_zeile(app):
    code, _ = app.post('/api/edit/002', dict(edits=[dict(line=1, old='etwas anderes', new='x')]))
    assert code == 409
    assert app.text('002')[1] == 'Der Vater und ber Sohn.'


def test_serienkorrektur_und_ruecknahme(app):
    before = {pg: app.text(pg) for pg in ('001', '002')}
    assert app.get('/api/occurrences?word=ber&count=1')[1] == dict(n=3)
    items = app.get('/api/occurrences?word=ber')[1]['items']
    code, r = app.post('/api/series', dict(word='ber', new='der', items=items))
    assert code == 200 and (r['done'], r['skipped']) == (3, 0)
    assert app.text('001')[2] == 'der Weg war weit. Die Zu¬' and app.text('002')[1] == 'Der Vater und der Sohn.'
    r = app.post('/api/series_undo', {})[1]
    assert r['done'] == 3
    assert {pg: app.text(pg) for pg in ('001', '002')} == before
    assert app.post('/api/series_undo', {})[1]['id'] is None


def test_serienkorrektur_ueber_zeilentrennung(app):
    items = app.get('/api/occurrences?word=Zukunft')[1]['items']
    assert len(items) == 1 and items[0]['join']
    app.post('/api/series', dict(word='Zukunft', new='Ankunft', items=items))
    assert app.text('001')[2:4] == ['ber Weg war weit. Die An¬', 'kunft lag vor ihnen, baß sie']


def test_serie_ueberspringt_geaenderte_zeilen(app):
    items = app.get('/api/occurrences?word=ber')[1]['items']
    old = app.text('002')[1]
    app.post('/api/edit/002', dict(edits=[dict(line=1, old=old, new='Der Vater und ber Sohn!')]))
    r = app.post('/api/series', dict(word='ber', new='der', items=items))[1]
    assert (r['done'], r['skipped']) == (2, 1)


def test_fussnotentrenner_verschieben_und_entfernen(app):
    t = app.text('001')
    code, r = app.post('/api/fnsep/001', dict(line=4, old=t[4]))
    assert code == 200 and r['action'] == 'gesetzt'
    assert app.text('001')[4:] == ['---', 'ber Heimat gedachten.', '1) Vgl. die Quellen.']
    assert None not in [g for g, l in zip(r['data']['geo'], r['data']['lines']) if l != '---']
    r = app.post('/api/fnsep/001', dict(line=5, old='ber Heimat gedachten.'))[1]
    assert r['action'] == 'entfernt' and '---' not in app.text('001')


def test_whitelist(app):
    app.post('/api/whitelist', dict(word='ber'))
    assert words(app.get('/api/page/001')[1]) == ['baß']
    assert app.get('/api/whitelist')[1]['words'] == ['ber']
    app.post('/api/whitelist_remove', dict(word='ber'))
    assert words(app.get('/api/page/001')[1]) == ['ber', 'baß', 'ber']


def test_lesezeichen(app):
    assert app.get('/api/bookmark')[1] == {}
    app.post('/api/bookmark', dict(page='002', line=1))
    assert app.get('/api/bookmark')[1] == dict(page='002', line=1)


def test_nextflag(app):
    assert app.get('/api/nextflag?after=001')[1] == dict(page='002')
    assert app.get('/api/nextflag?after=002')[1] == dict(page=None)


def test_zweiter_start_auf_gleichem_port_scheitert_verstaendlich(app):
    import subprocess, sys, os
    from conftest import ROOT
    port = app.base.rsplit(':', 1)[1]
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'server.py'), app.folder, '--port', port, '--no-browser'],
                       capture_output=True, timeout=60, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
    assert r.returncode != 0 and 'ist belegt' in r.stderr.decode('utf-8')
