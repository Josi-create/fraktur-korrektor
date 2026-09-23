"""Zwei Arbeitsstände desselben Buchs zusammenführen (#66): am PC gesichert, am Laptop weitergearbeitet, und
am PC inzwischen auch – die Änderungen aus dem PDF werden nachgespielt, Konflikte dem Nutzer gezeigt."""
import os, json
import pytest
from conftest import make_book
from test_ocr import wait

fitz = pytest.importorskip('fitz')


def job(lib, path, body):
    j = wait(lib, lib.lpost(path, body)[1]['job'])
    assert j['state'] == 'done', j
    return j['result']


def edit(lib, bid, pg, n, old, new):
    code, r = lib.lpost('/buch/%s/api/edit/%s' % (bid, pg), dict(edits=[dict(line=n, old=old, new=new)]))
    assert code == 200, (code, r)
    return r


def lines(lib, bid, pg):
    return lib.lget('/buch/%s/api/page/%s' % (bid, pg))[1]['lines']


def hin_und_zurueck(lib, tmp_path):
    """PC: eine Korrektur, sichern. Laptop: einlesen, korrigieren, Wort merken, Lesezeichen, sichern. Liefert (pc, lap, pdf2)."""
    make_book(str(tmp_path / 'Probebuch'))
    pc = lib.lpost('/api/open', dict(folder=str(tmp_path / 'Probebuch')))[1]['id']
    edit(lib, pc, '001', 2, 'ber Weg war weit. Die Zu¬', 'der Weg war weit. Die Zu¬')
    pdf = job(lib, '/api/export_pdf', dict(id=pc, target=str(tmp_path)))['file']
    lap = job(lib, '/api/import_pdfbuch', dict(source=pdf, target=str(tmp_path / 'laptop')))['id']
    edit(lib, lap, '002', 1, 'Der Vater und ber Sohn.', 'Der Vater und der Sohn.')
    lib.lpost('/buch/%s/api/whitelist' % lap, dict(word='Kolonisten'))
    lib.lpost('/buch/%s/api/bookmark' % lap, dict(page='002', line=1))
    (tmp_path / 'stick').mkdir()
    pdf2 = job(lib, '/api/export_pdf', dict(id=lap, target=str(tmp_path / 'stick')))['file']
    lib.lpost('/api/forget', dict(id=lap))  # das Laptop-Buch liegt nur wegen des Tests in derselben Bibliothek
    return pc, lap, pdf2


def test_compare():
    import merge
    a = '1\tedit\t001\t2\ta\tb\n2\tedit\t001\t3\tc\td\n'
    assert merge.compare(a, a) == dict(safe=True, here=0, there=0, only_here=[], only_there=[])
    assert merge.compare('', a)['safe'] and merge.compare('', a)['there'] == 2
    # nach dem Zusammenführen stehen die fremden Einträge hinter den eigenen – als Menge fehlt trotzdem nichts
    c = merge.compare(a + '3\tedit\t002\t1\tx\ty\n', '2\tedit\t001\t3\tc\td\n1\tedit\t001\t2\ta\tb\n')
    assert (c['safe'], c['here'], c['there']) == (False, 1, 0)
    c = merge.compare('1\tedit\t001\t2\ta\tb\n', '1\tedit\t001\t2\ta\tb\n1\tedit\t001\t2\ta\tb\n')  # derselbe Eintrag zweimal zählt zweimal
    assert (c['safe'], c['there']) == (True, 1)
    assert merge.parse('1\tedit\t001\t2\ta\tb') == ('1', 'edit', '001', 1, 'a', 'b') and merge.parse('kaputt') is None


def test_zusammenfuehren_ohne_konflikt(lib, tmp_path):
    pc, lap, pdf2 = hin_und_zurueck(lib, tmp_path)
    # am PC inzwischen eine andere Zeile berichtigt: Ersetzen geht nicht mehr, Zusammenführen wird empfohlen
    edit(lib, pc, '001', 4, 'ber Heimat gedachten.', 'der Heimat gedachten.')
    f = lib.lpost('/api/scan', dict(path=pdf2))[1]['found'][0]
    assert f['kind'] == 'pdfbuch' and f['known'] and f['book']['id'] == pc
    assert f['update'] == dict(safe=False, here=1, there=2)  # dort: Korrektur und gemerktes Wort; das Lesezeichen steht nicht im Protokoll
    j = wait(lib, lib.lpost('/api/import_pdfbuch', dict(source=pdf2, into=pc))[1]['job'])
    assert (j['state'], j['error']) == ('error', 'nicht_aktualisierbar')  # ohne ausdrückliches Zusammenführen bleibt es dabei
    r = job(lib, '/api/import_pdfbuch', dict(source=pdf2, into=pc, merge=True))
    assert r['updated'] and r['id'] == pc and r['backup'].startswith('vorher-') and r['merged']['conflicts'] == 0 and r['conflicts'] == 0
    assert r['merged']['applied'] == 1 and r['merged']['whitelist'] == 1 and r['bookmark'] == '002'
    assert lines(lib, pc, '002')[1] == 'Der Vater und der Sohn.' and lines(lib, pc, '001')[4] == 'der Heimat gedachten.'
    assert lib.lget('/buch/%s/api/whitelist' % pc)[1]['words'] == ['Kolonisten']
    assert lib.lget('/buch/%s/api/bookmark' % pc)[1] == dict(page='002', line=1)
    assert [x['title'] for x in lib.lget('/api/library')[1]['books']] == ['Probebuch']  # kein zweites Buch
    assert not os.path.exists(tmp_path / 'Probebuch' / 'konflikte.json')
    # das Protokoll enthält jetzt die Einträge vom Laptop wortgleich: das PDF hat nichts mehr, was hier fehlt
    theirs = open(tmp_path / 'laptop' / 'korrekturen.log', encoding='utf-8').read().splitlines()
    mine = open(tmp_path / 'Probebuch' / 'korrekturen.log', encoding='utf-8').read().splitlines()
    assert all(l in mine for l in theirs) and len(mine) == len(theirs) + 1
    assert lib.lpost('/api/scan', dict(path=pdf2))[1]['found'][0]['update'] == dict(safe=False, here=1, there=0)
    # zurück auf dem Laptop genügt wieder das einfache Ersetzen – dort fehlt nur die eine PC-Korrektur
    pdf3 = job(lib, '/api/export_pdf', dict(id=pc, target=str(tmp_path / 'stick')))['file']
    lap = lib.lpost('/api/open', dict(folder=str(tmp_path / 'laptop')))[1]['id']
    lib.lpost('/api/forget', dict(id=pc))
    assert lib.lpost('/api/scan', dict(path=pdf3))[1]['found'][0]['update'] == dict(safe=True, here=0, there=1)
    assert job(lib, '/api/import_pdfbuch', dict(source=pdf3, into=lap))['merged'] is None
    assert lines(lib, lap, '001')[4] == 'der Heimat gedachten.'


def test_dieselbe_zeile_verschieden(lib, tmp_path):
    """Konflikt: hier und dort dieselbe Zeile anders berichtigt. Die hiesige bleibt stehen, die Leseansicht zeigt beide."""
    pc, lap, pdf2 = hin_und_zurueck(lib, tmp_path)
    edit(lib, pc, '002', 1, 'Der Vater und ber Sohn.', 'Der Vater und der Sohn!')
    edit(lib, pc, '001', 4, 'ber Heimat gedachten.', 'ber Heimat gedachten.')  # ohne Wirkung, aber im Protokoll
    r = job(lib, '/api/import_pdfbuch', dict(source=pdf2, into=pc, merge=True))
    assert (r['merged']['applied'], r['merged']['conflicts'], r['conflicts']) == (0, 1, 1)
    assert lines(lib, pc, '002')[1] == 'Der Vater und der Sohn!'
    k = json.load(open(tmp_path / 'Probebuch' / 'konflikte.json', encoding='utf-8'))
    assert len(k) == 1 and (k[0]['page'], k[0]['line'], k[0]['art'], k[0]['hier'], k[0]['dort'], k[0]['alt']) == \
        ('002', 1, 'edit', 'Der Vater und der Sohn!', 'Der Vater und der Sohn.', 'Der Vater und ber Sohn.')
    p = lib.lget('/buch/%s/api/page/002' % pc)[1]
    assert len(p['conflicts']) == 1 and p['conflicts'][0]['dort'] == 'Der Vater und der Sohn.'
    assert lib.lget('/buch/%s/api/page/001' % pc)[1]['conflicts'] == []
    assert len(lib.lget('/buch/%s/api/overview' % pc)[1]['conflicts']) == 1
    # noch einmal dasselbe PDF: der Konflikt bleibt einer, nichts wird doppelt angewendet
    r = job(lib, '/api/import_pdfbuch', dict(source=pdf2, into=pc, merge=True))
    assert len(json.load(open(tmp_path / 'Probebuch' / 'konflikte.json', encoding='utf-8'))) == 1
    # der Nutzer nimmt die Fassung vom anderen Rechner – wie im Browser nur, wenn die Zeile noch so aussieht
    code, _ = lib.lpost('/buch/%s/api/conflict' % pc, dict(page='002', line=1, action='take', old='veraltet', dort='Der Vater und der Sohn.'))
    assert code == 409
    code, p = lib.lpost('/buch/%s/api/conflict' % pc, dict(page='002', line=1, action='take', old='Der Vater und der Sohn!', dort='Der Vater und der Sohn.'))
    assert code == 200 and p['lines'][1] == 'Der Vater und der Sohn.' and p['conflicts'] == []
    assert not os.path.exists(tmp_path / 'Probebuch' / 'konflikte.json')
    assert lib.lget('/buch/%s/api/overview' % pc)[1]['conflicts'] == []


def test_konflikt_erledigt_und_verschobene_zeile(lib, tmp_path):
    """»Erledigt« lässt die hiesige Fassung stehen; eine inzwischen verschobene Zeile findet die Leseansicht am Wortlaut."""
    pc, lap, pdf2 = hin_und_zurueck(lib, tmp_path)
    edit(lib, pc, '002', 1, 'Der Vater und ber Sohn.', 'Der Vater und der Sohn!')
    job(lib, '/api/import_pdfbuch', dict(source=pdf2, into=pc, merge=True))
    # Fußnotentrenner vor die Zeile: sie rückt um eins nach unten
    lib.lpost('/buch/%s/api/fnsep/002' % pc, dict(line=1, old='Der Vater und der Sohn!'))
    p = lib.lget('/buch/%s/api/page/002' % pc)[1]
    assert p['lines'][2] == 'Der Vater und der Sohn!' and p['conflicts'][0]['line'] == 2
    code, p = lib.lpost('/buch/%s/api/conflict' % pc, dict(page='002', line=2, action='done', dort='Der Vater und der Sohn.'))
    assert code == 200 and p['conflicts'] == [] and p['lines'][2] == 'Der Vater und der Sohn!'


def test_teilen_verbinden_fussnoten(lib, tmp_path):
    """Geteilte und verbundene Zeilen, versetzte Fußnotenstriche vom anderen Rechner: nachgespielt samt Zeilenlage."""
    pc, lap, pdf2 = hin_und_zurueck(lib, tmp_path)
    lib.lpost('/api/open', dict(folder=str(tmp_path / 'laptop')))
    # Laptop: Zeile 3 teilen, Zeile 1+2 verbinden, Fußnoten beginnen erst mit der letzten Zeile
    old = 'kunft lag vor ihnen, baß sie'
    assert lib.lpost('/buch/%s/api/lines/001' % lap, dict(kind='split', line=3, old=old, text=old, pos=13))[0] == 200
    l = lines(lib, lap, '001')
    assert l[3:5] == ['kunft lag vor', 'ihnen, baß sie']
    assert lib.lpost('/buch/%s/api/lines/001' % lap, dict(line=1, old=l[1:3]))[0] == 200
    l = lines(lib, lap, '001')
    assert l[1] == 'Die Kolonisten zogen nach Rußland und der Weg war weit. Die Zu¬' and l[2] == 'kunft lag vor'
    assert lib.lpost('/buch/%s/api/fnsep/001' % lap, dict(line=len(l) - 1, old=l[-1]))[0] == 200  # war schon dort: entfernt
    assert '---' not in lines(lib, lap, '001')
    pdf3 = job(lib, '/api/export_pdf', dict(id=lap, target=str(tmp_path / 'stick')))['file']
    lib.lpost('/api/forget', dict(id=lap))
    # PC: inzwischen die letzte Zeile berichtigt (andere Zeile: kein Konflikt)
    edit(lib, pc, '001', 6, '1) Vgl. die Quellen.', '1) Vgl. die Quellen!')
    r = job(lib, '/api/import_pdfbuch', dict(source=pdf3, into=pc, merge=True))
    assert (r['merged']['applied'], r['merged']['conflicts']) == (4, 0), r['merged']  # Korrektur 002, teilen, verbinden, fnsep
    p = lib.lget('/buch/%s/api/page/001' % pc)[1]
    assert p['lines'] == ['# 5', 'Die Kolonisten zogen nach Rußland und der Weg war weit. Die Zu¬', 'kunft lag vor', 'ihnen, baß sie',
                          'ber Heimat gedachten.', '1) Vgl. die Quellen!']
    assert p['geo'] and len(p['geo']) == len(p['lines']) and all(p['geo'][k] for k in range(len(p['lines'])))  # Zeilenzahl = Bildzuordnung
    assert p['geo'][2]['x1'] == p['geo'][3]['x0'] and p['geo'][1]['x0'] == 50 and p['geo'][1]['y1'] == 130  # im Maßstab des Bildes (0,5)
    # das Protokoll hält die Einträge vom Laptop wortgleich fest – bis auf den Fußnotenstrich: Die Zeile danach lautet hier anders
    theirs = open(tmp_path / 'laptop' / 'korrekturen.log', encoding='utf-8').read().splitlines()
    mine = open(tmp_path / 'Probebuch' / 'korrekturen.log', encoding='utf-8').read().splitlines()
    assert [l for l in theirs if l not in mine] == [l for l in theirs if '	fnsep	' in l] and any('	fnsep	' in l for l in mine)


def test_teilen_nicht_moeglich_wird_konflikt(lib, tmp_path):
    """Die Zeile, die dort geteilt wurde, wurde hier geändert: kein halbes Teilen, sondern ein Konflikt an dieser Zeile."""
    pc, lap, pdf2 = hin_und_zurueck(lib, tmp_path)
    lib.lpost('/api/open', dict(folder=str(tmp_path / 'laptop')))
    old = 'kunft lag vor ihnen, baß sie'
    lib.lpost('/buch/%s/api/lines/001' % lap, dict(kind='split', line=3, old=old, text=old, pos=13))
    pdf3 = job(lib, '/api/export_pdf', dict(id=lap, target=str(tmp_path / 'stick')))['file']
    lib.lpost('/api/forget', dict(id=lap))
    edit(lib, pc, '001', 3, old, 'kunft lag vor ihnen, daß sie')
    r = job(lib, '/api/import_pdfbuch', dict(source=pdf3, into=pc, merge=True))
    assert (r['merged']['applied'], r['merged']['conflicts']) == (1, 1)
    p = lib.lget('/buch/%s/api/page/001' % pc)[1]
    assert p['lines'][3] == 'kunft lag vor ihnen, daß sie' and len(p['lines']) == 7
    assert p['conflicts'][0]['art'] == 'teilen' and p['conflicts'][0]['line'] == 3 and p['conflicts'][0]['dort'] == 'kunft lag vor ⏎ ihnen, baß sie'


def test_altes_pdf_ohne_kennung_und_fremdes_buch(lib, tmp_path):
    """Ein PDF ohne Kennung (frühere Fassung) und ein PDF eines unbekannten Buchs: wie bisher ein neues Buch."""
    import server, pdfbuch
    make_book(str(tmp_path / 'Alt'))
    b = server.Book(str(tmp_path / 'Alt'))
    assert b.settings['kennung'] is None
    pdfbuch.save(b, str(tmp_path / 'Alt.pdf'))
    assert pdfbuch.info(str(tmp_path / 'Alt.pdf'))['kennung'] is None
    lib.lpost('/api/open', dict(folder=str(tmp_path / 'Alt')))
    f = lib.lpost('/api/scan', dict(path=str(tmp_path / 'Alt.pdf')))[1]['found'][0]
    assert f['kind'] == 'pdfbuch' and not f['known'] and 'update' not in f
    r = job(lib, '/api/import_pdfbuch', dict(source=str(tmp_path / 'Alt.pdf'), target=str(tmp_path / 'neu')))
    assert r['updated'] is False and r['merged'] is None and r['folder'] == str(tmp_path / 'neu')
    # in ein fremdes Buch geht es nicht – auch nicht mit Zusammenführen
    pc = lib.lpost('/api/open', dict(folder=str(tmp_path / 'Alt')))[1]['id']
    j = wait(lib, lib.lpost('/api/import_pdfbuch', dict(source=str(tmp_path / 'Alt.pdf'), into=pc, merge=True))[1]['job'])
    assert (j['state'], j['error']) == ('error', 'nicht_aktualisierbar')


def test_sicherung_und_bilder(lib, tmp_path):
    """Vor dem Zusammenführen wird der Stand gesichert; ein fehlendes Seitenbild kommt aus dem PDF, vorhandene bleiben."""
    pc, lap, pdf2 = hin_und_zurueck(lib, tmp_path)
    edit(lib, pc, '001', 4, 'ber Heimat gedachten.', 'der Heimat gedachten.')
    os.remove(tmp_path / 'Probebuch' / 'img' / '002.png')
    (tmp_path / 'Probebuch' / 'img' / '001.png').write_bytes(b'eigenes')  # bliebe sonst nicht »unverändert«
    r = job(lib, '/api/import_pdfbuch', dict(source=pdf2, into=pc, merge=True))
    assert r['images'] == 1 and os.path.exists(tmp_path / 'Probebuch' / 'img' / '002.png')
    assert (tmp_path / 'Probebuch' / 'img' / '001.png').read_bytes() == b'eigenes'
    b = [x for x in lib.lget('/api/library')[1]['books'] if x['id'] == pc][0]['backups']
    assert len(b) == 1 and b[0]['name'] == r['backup']
    assert lib.lpost('/api/restore', dict(id=pc, name=b[0]['name']))[0] == 200
    assert lines(lib, pc, '002')[1] == 'Der Vater und ber Sohn.' and lib.lget('/buch/%s/api/whitelist' % pc)[1]['words'] == []
