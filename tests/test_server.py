"""Die HTTP-Schnittstelle gegen ein Wegwerf-Buch (siehe conftest.py)."""


def words(data, kind=None):
    return [f['word'] for f in data['flags'] if kind in (None, f['kind'])]


def test_uebersicht_und_markierungen(app):
    code, ov = app.get('/api/overview')
    assert code == 200 and [p['page'] for p in ov['pages']] == ['001', '002']
    assert app.get('/api/progress')[1] == dict(done=1, total=1)  # nichts in Arbeit: der Ladebalken bleibt verborgen
    code, d = app.get('/api/page/001')
    # ber: unbekannt; baß: Falle; Vgl: Zusatzliste; Zu¬kunft: über die Trennung hinweg bekannt
    assert words(d) == ['ber', 'baß', 'ber']
    assert app.get('/api/page/999')[0] == 404


def test_bildzuordnung(app):
    d = app.get('/api/page/001')[1]
    assert len(d['geo']) == len(d['lines'])
    assert d['geo'][5] is None                      # Fußnotentrenner hat keine Bildzeile
    assert d['geo'][1] == dict(x0=50, x1=450, y0=80, y1=100)   # Maßstab 0.5
    assert d['size'] == [500, 750]                    # Bildmaße, damit der Reader die Nachbarseiten platzieren kann
    assert d['img'] == app.book + '/img/001.png' and app.raw(d['img'])[1][:4] == b'\x89PNG'


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


def test_rechtschreibung_je_buch(app):
    import os, json
    old = app.text('002')[1]
    app.post('/api/edit/002', dict(edits=[dict(line=1, old=old, new='Der Vater sagte, dass die Thür offen sey. BWKG und BWKG.')]))
    assert app.get('/api/settings')[1] == dict(year=None, dics=['1901'], notizen=None, kennung=None, autor=None)  # Bücher von früher: wie bisher
    assert words(app.get('/api/page/002')[1]) == ['dass', 'Thür', 'sey']              # die Sigle BWKG (zweimal, Großbuchstaben) gilt
    code, r = app.post('/api/settings', dict(dics=['neu', '1901']))
    assert code == 200 and r['dics'] == ['1901', 'neu'] and words(app.get('/api/page/002')[1]) == ['Thür', 'sey']
    r = app.post('/api/settings', dict(dics=['vor1901']))[1]                          # ein Wörterbuch muss gelten
    assert r['dics'] == ['1901', 'vor1901'] and words(app.get('/api/page/002')[1]) == ['dass']
    assert r['total'] == sum(p['n'] for p in app.get('/api/overview')[1]['pages'])
    assert json.load(open(os.path.join(app.folder, 'buch.json'), encoding='utf-8'))['dics'] == ['1901', 'vor1901']  # bleibt gespeichert


def test_notizen_fuer_obsidian(app, tmp_path):
    import os, json
    assert app.post('/api/notiz', dict(page='001', text='Die Kolonisten'))[1]['error'] == 'kein_notizordner'
    assert app.post('/api/settings', dict(notizen=str(tmp_path / 'gibtsnicht' / 'Buch')))[1]['notizen'].endswith('Buch')
    assert app.post('/api/notiz', dict(page='001', text='x'))[1]['error'] == 'notizordner_fehlt'  # Elternordner fehlt: vertippt
    folder = tmp_path / 'Vault' / 'Leibbrandt 1928'
    folder.parent.mkdir()
    app.post('/api/settings', dict(notizen=str(folder)))
    assert json.load(open(os.path.join(app.folder, 'buch.json'), encoding='utf-8'))['notizen'] == str(folder)
    code, r = app.post('/api/notiz', dict(page='001', text='ber Weg war weit. Die Zu¬\nkunft lag  vor ihnen, baß sie\nber Heimat gedachten.', lines=[3, 5]))
    assert code == 200 and r['name'] == '01 Seite 5' and r['page'] == '5' and not r['opened']  # gedruckte Seitenzahl aus der Kopfzeile
    note = open(folder / '01 Seite 5.md', encoding='utf-8').read()
    assert note == '**Anmerkung**\n\n\n\n---\n\n> ber Weg war weit. Die Zukunft lag vor ihnen, baß sie ber Heimat gedachten.\n\nSeite 5, Zeile 3–5, [[0 Quellenangabe|buch]]\n'
    code, r = app.post('/api/notiz', dict(page='001', text='Die Kolonisten', lines=[2, 2], lang='en'))  # eine Zeile, englisch
    assert code == 200 and open(folder / '02 Page 5.md', encoding='utf-8').read().endswith('\n\nPage 5, Line 2, [[0 Source|buch]]\n')
    code, r = app.post('/api/notiz', dict(page='001', text='Die Kolonisten'))  # ohne Zeilenangabe (ältere Aufrufer)
    assert code == 200 and open(folder / '03 Seite 5.md', encoding='utf-8').read().endswith('\n\nSeite 5, [[0 Quellenangabe|buch]]\n')
    src = open(folder / '0 Quellenangabe.md', encoding='utf-8').read()
    assert src.startswith('# buch\n') and 'Zotero' in src
    open(folder / '0 Quellenangabe.md', 'w', encoding='utf-8').write('# Eigene Angaben\n')  # wird nie überschrieben
    r = app.post('/api/notiz', dict(page='002', text='<em>Der Vater</em> und ber Sohn.', lang='en'))[1]
    assert r['name'] == '04 Page 6' and open(folder / '04 Page 6.md', encoding='utf-8').read().startswith('**Note**\n\n\n\n---\n\n> Der Vater und ber Sohn.\n\nPage 6')
    assert open(folder / '0 Quellenangabe.md', encoding='utf-8').read() == '# Eigene Angaben\n'
    assert sorted(os.listdir(folder)) == ['0 Quellenangabe.md', '0 Source.md', '01 Seite 5.md', '02 Page 5.md', '03 Seite 5.md', '04 Page 6.md']
    assert app.post('/api/notiz', dict(page='001', text='  \n '))[1]['error'] == 'kein_text'
    assert app.post('/api/settings', dict(dics=['neu']))[1]['notizen'] == str(folder)  # Wörterbuchwahl lässt den Ordner stehen
    assert app.post('/api/settings', dict(notizen=''))[1]['notizen'] is None


def test_notiz_titel_mit_klammern_und_ordner_als_datei(app, tmp_path):
    # Umbenennen lässt [ ] | im Titel zu – der Verweis im Zettel bleibt trotzdem ein gültiger Obsidian-Link (#71)
    app.lpost('/api/rename', dict(id=app.book[6:], title='Reise [Band 2]'))
    (tmp_path / 'Vault').mkdir()
    app.post('/api/settings', dict(notizen=str(tmp_path / 'Vault' / 'Reise')))
    assert app.post('/api/notiz', dict(page='001', text='Die Kolonisten', lines=[2, 2]))[0] == 200
    assert open(tmp_path / 'Vault' / 'Reise' / '01 Seite 5.md', encoding='utf-8').read().endswith(', [[0 Quellenangabe|Reise (Band 2)]]\n')
    # Ist der Notizordner in Wahrheit eine Datei: Meldung statt abgerissener Verbindung
    (tmp_path / 'Vault' / 'Datei').write_text('x')
    app.post('/api/settings', dict(notizen=str(tmp_path / 'Vault' / 'Datei')))
    assert app.post('/api/notiz', dict(page='001', text='x')) == (400, dict(error='notiz_schreiben'))


def test_notiz_fuer_obsidian_auf_dem_tablet(app, tmp_path):
    """Vom Tablet (#63): Der Server schreibt den Zettel nicht, sondern liefert Inhalt und Ort im Vault – Obsidian dort legt ihn
    an. Die Nummer zählt trotzdem weiter, auch solange der Zettel hier noch fehlt (Obsidian am Rechner nicht offen)."""
    import os, json
    vault = tmp_path / 'Mein Vault'
    (vault / '.obsidian').mkdir(parents=True)
    folder = vault / 'Recherche' / 'Leibbrandt 1928'
    folder.parent.mkdir()
    assert app.get('/api/vault')[1] == dict(vault=None)  # noch kein Notizordner
    app.post('/api/settings', dict(notizen=str(folder)))
    assert app.get('/api/vault')[1] == dict(vault='Mein Vault')
    code, r = app.post('/api/notiz', dict(page='001', text='Die Kolonisten', lines=[2, 2], geraet=True))
    assert code == 200 and r['vault'] == 'Mein Vault' and r['file'] == 'Recherche/Leibbrandt 1928/01 Seite 5' and r['name'] == '01 Seite 5'
    assert r['content'] == '**Anmerkung**\n\n\n\n---\n\n> Die Kolonisten\n\nSeite 5, Zeile 2, [[0 Quellenangabe|buch]]\n'
    assert sorted(os.listdir(folder)) == ['0 Quellenangabe.md']  # hier entsteht nur die Quellenangabe
    assert app.post('/api/notiz', dict(page='001', text='x', geraet=True))[1]['name'] == '02 Seite 5'
    assert app.post('/api/notiz', dict(page='002', text='Der Vater'))[1]['name'] == '03 Seite 6'  # am Rechner geht es weiter
    (folder / '10 Eigene.md').write_text('x')  # selbst angelegte Zettel mit höherer Nummer zählen wie bisher
    assert app.post('/api/notiz', dict(page='001', text='x', geraet=True))[1]['name'] == '11 Seite 5'
    assert json.load(open(os.path.join(app.folder, 'buch.json'), encoding='utf-8'))['notiz_nr'] == 11
    app.post('/api/settings', dict(notizen=str(vault)))  # der Vault selbst als Notizordner
    assert app.post('/api/notiz', dict(page='001', text='x', geraet=True))[1]['file'] == '01 Seite 5'  # anderer Ordner: neue Zählung
    # Notizordner in keinem Vault: Meldung – der Reader legt den Zettel dann am Rechner an
    (tmp_path / 'Lose').mkdir()
    app.post('/api/settings', dict(notizen=str(tmp_path / 'Lose' / 'Buch')))
    assert app.post('/api/notiz', dict(page='001', text='x', geraet=True)) == (400, dict(error='kein_vault'))
    assert app.get('/api/vault')[1] == dict(vault=None)
    assert not (tmp_path / 'Lose' / 'Buch').exists()
    assert app.post('/api/notiz', dict(page='001', text='x'))[1]['name'] == '01 Seite 5'


def test_suche_im_ganzen_buch(app):
    """Suchen (S im Reader): ohne Rücksicht auf Groß-/Kleinschreibung, auch über die Zeilentrennung ¬ hinweg."""
    r = app.get('/api/search?q=ber')[1]
    assert r['n'] == 3 and [(o['page'], o['line'], o['start'], o['len']) for o in r['items']] == [('001', 2, 0, 3), ('001', 4, 0, 3), ('002', 1, 14, 3)]
    assert [o['start'] for o in app.get('/api/search?q=RUSSLAND')[1]['items']] == [] and [o['start'] for o in app.get('/api/search?q=ru%C3%9Fland')[1]['items']] == [26]
    j = app.get('/api/search?q=Zukunft')[1]['items']  # steht nirgends in einer Zeile, nur als Zu¬ / kunft
    assert len(j) == 1 and j[0]['join'] and (j[0]['line'], j[0]['start'], j[0]['len'], j[0]['start2'], j[0]['len2']) == (2, 22, 2, 0, 5)
    assert app.get('/api/search?q=')[1]['n'] == 0 and app.get('/api/search?q=gibtesnicht')[1]['n'] == 0


def test_seitenzahl_passt_nicht_zu_nachbarn(tmp_path):
    """Die OCR liest in Fraktur 1 als 4: Kopfzeilen 13, 14, 45, 46, 17, 18. Die falschen Zahlen werden rot, mit der nach den
    Nachbarn richtigen Zahl; die Notiz nimmt gleich die richtige. Wo die Nachbarn sich nicht einig sind, bleibt es still."""
    import os, server
    folder = tmp_path / 'buch'
    folder.mkdir()
    for i, n in enumerate(['13', '14', '45', '46', '17', '18', '', '20', '21']):  # 007 ohne Kopfzeile (Tafel), 008 stimmt wieder
        (folder / ('%03d.txt' % (i + 1))).write_text(('# %s\n' % n if n else '') + 'Die Kolonisten zogen.\n', encoding='utf-8')
    b = server.Book(str(folder))
    b.refresh()
    assert [f for f in b.flags('001') if f['kind'] == 'page'] == []  # 13: 14 sagt ja, 45 und 46 nein – keine Dreiviertel, kein Rot
    assert [f for f in b.flags('003') if f['kind'] == 'page'] == [dict(line=0, start=2, len=2, word='45', kind='page', expect=15)]
    assert [f for f in b.flags('004') if f['kind'] == 'page'] == [dict(line=0, start=2, len=2, word='46', kind='page', expect=16)]
    assert [f for f in b.flags('005') if f['kind'] == 'page'] == []
    assert b.printed_page('004') == '16' and b.printed_page('005') == '17'
    assert b.printed_page('007') == '19' and b.flags('007') == []  # Kapitelanfang ohne Kopfzeile: die Notiz weiß trotzdem die Seite
    assert b.expected_page('008') == 20 and b.printed_page('009') == '21'
    # fehlender Scan: 1 2 3 4 | 6 7 8 9 – die Nachbarn stehen halb gegen halb, nichts wird rot
    g = tmp_path / 'luecke'
    g.mkdir()
    for i, n in enumerate([1, 2, 3, 4, 6, 7, 8, 9]):
        (g / ('%03d.txt' % (i + 1))).write_text('# %d\nText.\n' % n, encoding='utf-8')
    g = server.Book(str(g))
    g.refresh()
    assert all(f['kind'] != 'page' for pg in g.pages for f in g.flags(pg))
    (folder / '004.txt').write_text('# 16\nDie Kolonisten zogen.\n', encoding='utf-8')
    os.utime(folder / '004.txt', (0, 1e9))
    b.refresh()
    assert b.flags('004') == [] and b.printed_page('004') == '16'
    # Nachbarseiten berichtigt, ohne dass 003 sich ändert: das Urteil über 003 darf nicht aus dem Zwischenspeicher kommen
    for i, n in enumerate(['43', '44', None, '46', '47', '48', '', '50', '51']):  # 003 bleibt unberührt
        if n is None:
            continue
        (folder / ('%03d.txt' % (i + 1))).write_text(('# %s\n' % n if n else '') + 'Die Kolonisten zogen.\n', encoding='utf-8')
        os.utime(folder / ('%03d.txt' % (i + 1)), (0, 2e9))
    b.refresh()
    assert b.flags('003') == [] and b.printed_page('003') == '45'


def test_seitenzahl_unten_auf_der_seite(tmp_path):
    """Neuere Bücher tragen die Seitenzahl unten, oft mit Rauschen vom Seitenrand (»i 12«, »BTB«). Sie gilt wie die aus der
    Kopfzeile: für Notizen, gegen Lesefehler (»44« statt 14), und ein über die Seitengrenze getrenntes Wort bleibt ganz."""
    import korrlib, server
    assert korrlib.foot_number(['# ', 'Text der Seite.', 'i 20', 'BTB']) == (20, 2, 2, 2)
    assert korrlib.foot_number(['# ', 'Text der Seite.', '— 137 —'])[0] == 137 and korrlib.foot_number(['Text', '8 | 4'])[0] == 4
    assert korrlib.foot_number(['# ', 'Text der Seite.', '4 *']) is None           # Bogensignatur
    assert korrlib.foot_number(['# ', 'im Jahre 1985.']) is None                   # Text, keine Seitenzahl
    assert korrlib.foot_number(['# ', '17', 'Text', 'noch Text', 'und noch mehr Text']) is None  # nur die letzten drei Zeilen
    folder = tmp_path / 'buch'
    folder.mkdir()
    pages = [['Die Kolonisten zogen.', '11'], ['Die Kolonisten zogen.', 'i 12', 'BTB'], ['durch die Ge¬', '— 13 —'],
             ['walt der Musik.', '44ä'], ['Erstes Kapitel.'], ['Die Kolonisten zogen.', '16'], ['Die Kolonisten zogen.', '17'],
             ['Die Kolonisten zogen.', '18']]
    for i, p in enumerate(pages):
        (folder / ('%03d.txt' % (i + 1))).write_text('\n'.join(['# '] + p) + '\n', encoding='utf-8')
    b = server.Book(str(folder))
    b.refresh()
    assert sorted(b.feet) == ['001', '002', '003', '004', '006', '007', '008']
    assert [b.printed_page(pg) for pg in b.pages] == ['11', '12', '13', '14', '15', '16', '17', '18']  # 005: Kapitelanfang ohne Zahl
    assert [f for f in b.flags('004') if f['kind'] == 'page'] == [dict(line=2, start=0, len=2, word='44', kind='page', expect=14)]
    assert b.flags('003') == [] and [f['kind'] for f in b.flags('004')] == ['page']  # Ge¬walt über »— 13 —« hinweg als ein Wort
    assert b.page_data('002')['foot'] == 2 and b.page_data('005')['foot'] is None
    # Jahreszahlen und Fußnotennummern am Seitenende machen noch kein Buch mit Seitenzahlen unten
    other = tmp_path / 'jahre'
    other.mkdir()
    for i, n in enumerate(['1985.', '1963.', '15.', 'Text.', '53.']):
        (other / ('%03d.txt' % (i + 1))).write_text('# \nDie Kolonisten zogen.\n%s\n' % n, encoding='utf-8')
    o = server.Book(str(other))
    o.refresh()
    assert o.feet == {} and o.printed_page('001') == '1' and all(f['kind'] != 'page' for pg in o.pages for f in o.flags(pg))


def test_korrekturvorschlaege(app):
    """#41: gelernt aus dem Protokoll, dann OCR-Verwechslungen (häufige im Buch zuerst), zuletzt Hunspell."""
    old = app.text('001')[2]
    app.post('/api/edit/001', dict(edits=[dict(line=2, old=old, new='der Weg war weit. Die Zu¬')]))
    r = app.get('/api/suggest?fast=1&word=ber')[1]
    assert r['items'][0] == 'der' and 'ber' not in r['items']
    assert app.get('/api/suggest?fast=1&word=ba%C3%9F')[1]['items'][0] == 'daß'  # b/d – „baß“ selbst steht in fallen.txt
    assert app.get('/api/suggest?fast=1&word=Bolk')[1]['items'] == ['Volk']
    app.post('/api/whitelist', dict(word='Katharinenfeld'))  # die Whitelist zählt als bekannt
    assert app.get('/api/suggest?fast=1&word=Katharinenfelb')[1]['items'] == ['Katharinenfeld']
    assert app.get('/api/suggest?fast=1&word=Zu%C2%ACkunft')[1]['items'] == []  # getrenntes Wort: als Ganzes, und das ist richtig
    assert 'Zukunft' in app.get('/api/suggest?word=Zutunft')[1]['items']  # mit Hunspell
    assert app.get('/api/suggest?word=')[1]['items'] == []
    # die nächsten roten Wörter meldet der Reader vorab (#68); die Rechnung dazu prüft test_korrlib
    assert app.post('/api/suggest_ahead', dict(words=['Rußlanb', 'Zu¬kunft', 'x', 7]))[0] == 200
    assert 'Rußland' in app.get('/api/suggest?word=Ru%C3%9Flanb')[1]['items']


def test_trennung_ueber_die_seitengrenze(lib, tmp_path):
    """Ge¬ | # 23 | walt: als ein Wort geprüft – Kopfzeile und Fußnoten dazwischen stören nicht."""
    folder = tmp_path / 'Buch'
    folder.mkdir()
    (folder / '035.txt').write_text('# 22\nfalls lediglich in Ceremonien, ohne durch die Ge¬\n---\n1) Fußnote.\n', encoding='utf-8')
    (folder / '036.txt').write_text('# 23\nwalt der Musik und des Glanzes gehoben zu\n', encoding='utf-8')
    (folder / '037.txt').write_text('# 24\nsein. Und dann kam das Ver¬\n', encoding='utf-8')
    (folder / '038.txt').write_text('# 25\nqwxyz der Kolonisten.\n', encoding='utf-8')
    b = '/buch/' + lib.lpost('/api/open', dict(folder=str(folder)))[1]['id']
    assert words(lib.lget(b + '/api/page/035')[1]) == ['Ceremonien'] and words(lib.lget(b + '/api/page/036')[1]) == []
    f = [x for x in lib.lget(b + '/api/page/037')[1]['flags'] if x['line'] == 1][0]
    assert (f['word'], f['start'], f['len'], f['cross']) == ('Ver¬qwxyz', 23, 3, 'next')
    f = lib.lget(b + '/api/page/038')[1]['flags'][0]
    assert (f['word'], f['line'], f['start'], f['len'], f['cross']) == ('Ver¬qwxyz', 1, 0, 5, 'prev')
    # die eine Hälfte berichtigt: die andere Seite merkt es (Zwischenspeicher hängt an beiden Seiten)
    lib.lpost(b + '/api/edit/038', dict(edits=[dict(line=1, old='qwxyz der Kolonisten.', new='mögen der Kolonisten.')]))
    assert words(lib.lget(b + '/api/page/037')[1]) == []


def test_gleiche_aenderungszeit_beim_zweiten_schreiben(tmp_path, monkeypatch):
    """#72: Windows vergibt Änderungszeiten in Schritten von bis zu 15 ms. Teilen und Verbinden derselben Seite kurz
    hintereinander (so beim Zusammenführen) ergaben dieselbe Zeit, und das Programm arbeitete mit der geteilten Fassung
    weiter. Hier bekommt jede geschriebene Datei dieselbe Zeit – das Ergebnis muss trotzdem stimmen."""
    import os, server
    from conftest import make_book
    make_book(str(tmp_path / 'buch'))
    b = server.Book(str(tmp_path / 'buch'))
    b.refresh()
    schreiben = server.write_atomic

    def gleiche_zeit(path, text):
        schreiben(path, text)
        os.utime(path, (1e9, 1e9))
    monkeypatch.setattr(server, 'write_atomic', gleiche_zeit)
    t = list(b.pages['001'])
    assert b.split_line('001', 1, t[1], t[1], t[1].index(' nach'))[1] is None
    assert b.pages['001'][1:3] == ['Die Kolonisten zogen', 'nach Rußland und']
    d, err = b.join_lines('001', 1, b.pages['001'][1:3])
    assert err is None and d['lines'] == t and b.pages['001'] == t
    assert b.fnsep('001', 6, t[6])['data']['lines'] == t[:5] + t[6:]  # arbeitet auf der verbundenen Fassung


def test_zeilenlaenge_fuer_die_schriftgroesse(app):
    """Die Übersicht nennt, wie lang eine volle Zeile des Buchs ist – danach wählt der Reader die Schriftgröße, damit eine
    gedruckte Zeile rechts in eine Zeile passt. Kopfzeile und Fußnoten zählen nicht."""
    assert app.get('/api/overview')[1]['zeichen'] == len('Die Kolonisten zogen nach Rußland und')


def test_kolumnentitel_als_textzeile(tmp_path):
    """Der lebende Kolumnentitel, von der Erkennung als gewöhnliche Zeile oben gelesen (»Stalins Bauernopfer am Schwarzen
    Meer 9«, auch Titel und Zahl als zwei Zeilen, die Zahl links oder rechts): Er gilt wie die Kopfzeile – blass, nicht
    geprüft, nicht zu löschen, seine Zahl ist die Seitenzahl. Die Dateien ändern sich nicht."""
    import korrlib, server
    folder = tmp_path / 'buch'
    folder.mkdir()
    for i in range(6):
        n, t = 9 + i, 'Chronik von Qwxyzdorf'
        top = [t + ' %d' % n] if i % 3 == 0 else (['%d' % n, t] if i % 3 == 1 else [t, '%d' % n])
        body = ['Die Kolonisten zogen nach Rußland.', 'Der Weg war weit.', 'Sie kamen im Winter an.']
        (folder / ('%03d.txt' % (i + 1))).write_text('\n'.join(['# '] + top + body) + '\n', encoding='utf-8')
    before = {p.name: p.read_text(encoding='utf-8') for p in folder.iterdir()}
    b = server.Book(str(folder))
    b.refresh()
    assert b.heads['001'] == ((9, 1, 22, 1), [1]) and b.heads['002'] == ((10, 1, 0, 2), [1, 2]) and b.heads['003'][1] == [1, 2]
    assert [b.printed_page(pg) for pg in b.pages] == [str(9 + i) for i in range(6)]
    d = b.page_data('002')
    assert d['kopf'] == [1, 2] and d['flags'] == []                       # Qwxyzdorf wird nicht rot
    assert b.delete_lines('001', 1, [b.pages['001'][1]]) == (None, 400)
    assert {p.name: p.read_text(encoding='utf-8') for p in folder.iterdir() if p.suffix == '.txt'} == before
    # Kein Kolumnentitel: dieselbe erste Zeile auf zu wenigen Seiten (»Faust.« in einem Drama) oder nur auf zweien
    drama = {'%03d' % n: ['# %d' % n, 'Faust.' if n % 4 == 0 else 'Zeile %s von Seite %d.' % ('eins' * n, n), 'Text.'] for n in range(1, 13)}
    assert korrlib.head_lines(drama) == {}
    zwei = {'%03d' % n: ['# ', 'Chronik von Qwxyzdorf' if n < 3 else 'Anderes %d' % n, 'Text.'] for n in range(1, 4)}
    assert korrlib.head_lines(zwei) == {}
