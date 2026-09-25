"""Die gepackte App: Kennung für den Starter, zweiter Start, Auswahldialoge, mitgeliefertes Tesseract.

Der Durchlauf mit der fertigen .app bzw. .exe steht in scripts/smoke_test.py – hier geht es um die Logik,
die dafür in server.py, ocr.py und starter.py dazugekommen ist."""
import os
import subprocess
import sys
import types

import pytest

import ocr
import server
import starter


def test_ping_nennt_programm_und_version(lib):
    assert lib.lget('/api/ping')[1] == dict(app='fraktur-korrektor', version=server.version())


def test_zweiter_start_oeffnet_nur_den_browser(lib, monkeypatch):
    """Ein zweiter Doppelklick darf keinen zweiten Server starten – er zeigt nur wieder das Fenster."""
    port = int(lib.base.rsplit(':', 1)[1])
    geoeffnet = []
    monkeypatch.setattr(starter, 'show', geoeffnet.append)
    monkeypatch.setattr(starter.server, 'setup', lambda A: pytest.fail('es wurde ein zweiter Server gestartet'))
    assert starter.main(['--port', str(port)]) == 0
    assert geoeffnet == ['http://localhost:%d' % port]
    geoeffnet.clear()
    assert starter.main(['--port', str(port), '--no-browser']) == 0
    assert geoeffnet == []


def test_fremder_dienst_auf_dem_port_ist_kein_fraktur_korrektor(lib):
    """Auf dem Port antwortet zwar etwas, aber nicht dieses Programm: dann darf der Starter ihn nicht übernehmen."""
    assert starter.answering(int(lib.base.rsplit(':', 1)[1]))
    with __import__('socket').socket() as so:
        so.bind(('127.0.0.1', 0))
        assert not starter.answering(so.getsockname()[1])  # niemand horcht


def test_starter_meldet_belegten_port(monkeypatch):
    def belegt(A):
        raise OSError(48, 'Address already in use')
    monkeypatch.setattr(starter.server, 'setup', belegt)
    monkeypatch.setattr(starter, 'answering', lambda port: False)
    gemeldet = []
    monkeypatch.setattr(starter, 'alert', gemeldet.append)
    assert starter.main(['--port', '8765']) == 1
    assert '8765' in gemeldet[0]


def test_prozessnummer_des_finders_stoert_nicht(monkeypatch):
    """Der Finder hängt beim Start manchmal -psn_0_… an; argparse würde daran scheitern."""
    monkeypatch.setattr(starter, 'answering', lambda port: True)
    monkeypatch.setattr(starter, 'show', lambda url: None)
    assert starter.main(['-psn_0_123456', '--port', '8765']) == 0


def test_fenster_zeigen_statt_neuem_tab(monkeypatch):
    """»Im Browser öffnen« soll das schon geöffnete Fenster zeigen; erst wenn es keins gibt, einen neuen Tab."""
    monkeypatch.setattr(starter.sys, 'platform', 'darwin')
    monkeypatch.setattr(starter, 'running_apps', lambda: {'Google Chrome', 'Mail'})
    gefragt, neu = [], []
    monkeypatch.setattr(starter.webbrowser, 'open', neu.append)

    def run(cmd, **kw):
        gefragt.append(cmd[-1])
        return types.SimpleNamespace(returncode=0, stdout=b'ok\n', stderr=b'')
    monkeypatch.setattr(starter.subprocess, 'run', run)
    starter.show('http://localhost:8765')
    assert len(gefragt) == 1 and 'Google Chrome' in gefragt[0] and 'localhost:8765' in gefragt[0]
    assert 'Safari' not in ''.join(gefragt)  # Safari läuft nicht: nicht starten, nur fragen kostet Zeit
    assert neu == []

    # kein passender Tab (oder keine Erlaubnis): dann wie bisher einen neuen öffnen
    monkeypatch.setattr(starter.subprocess, 'run',
                        lambda cmd, **kw: types.SimpleNamespace(returncode=1, stdout=b'', stderr=b'nicht erlaubt (-1743)'))
    starter.show('http://localhost:8765')
    assert neu == ['http://localhost:8765']


# ---- Auswahldialoge

def lauf(ergebnis='', fehler=b'', code=0):
    return types.SimpleNamespace(returncode=code, stdout=ergebnis.encode('utf-8'), stderr=fehler)


def test_mac_dialog_ordner_und_datei(monkeypatch):
    gesehen = []

    def run(cmd, **kw):
        gesehen.append(cmd[-1])
        return lauf('/Users/x/Mein Buch\n')
    monkeypatch.setattr(server.subprocess, 'run', run)
    assert server.mac_dialog('folder') == '/Users/x/Mein Buch'
    assert 'choose folder with prompt' in gesehen[-1] and 'of type' not in gesehen[-1]
    assert server.mac_dialog('any') == '/Users/x/Mein Buch'
    assert 'choose file with prompt' in gesehen[-1] and '"com.adobe.pdf"' in gesehen[-1]


def test_mac_dialog_abbruch_und_rueckfall(monkeypatch):
    """Abbruch (-128) heißt: nichts gewählt. Ein anderer Fehler heißt: die Typliste war zu eng."""
    monkeypatch.setattr(server.subprocess, 'run', lambda cmd, **kw: lauf(fehler=b'execution error: ... (-128)', code=1))
    assert server.mac_dialog('pdf') == ''

    versuche = []

    def run(cmd, **kw):
        versuche.append(cmd[-1])
        return lauf(fehler=b'execution error: unbekannter Typ (-1700)', code=1) if len(versuche) == 1 else lauf('/Users/x/b.pdf\n')
    monkeypatch.setattr(server.subprocess, 'run', run)
    assert server.mac_dialog('pdf') == '/Users/x/b.pdf'
    assert 'of type' in versuche[0] and 'of type' not in versuche[1]


def buendel(tmp_path, name='ScanTailor (Advanced).app', exe='ScanTailor'):
    """Ein Mac-Programmbündel wie das von ScanTailor: neben der Programmdatei liegt ein Ordner »config«."""
    import plistlib
    app = tmp_path / name
    (app / 'Contents' / 'MacOS' / 'config').mkdir(parents=True)
    (app / 'Contents' / 'MacOS' / exe).write_text('x')
    with open(app / 'Contents' / 'Info.plist', 'wb') as f:
        plistlib.dump(dict(CFBundleExecutable=exe), f)
    return app


def test_mac_dialog_loest_programmbuendel_auf(monkeypatch, tmp_path):
    """Für ScanTailor wird die Datei im Bündel gebraucht, nicht der Ordner ScanTailor.app."""
    app = buendel(tmp_path)
    monkeypatch.setattr(server.subprocess, 'run', lambda cmd, **kw: lauf(str(app) + '/\n'))
    assert server.mac_dialog('exe') == str(app / 'Contents' / 'MacOS' / 'ScanTailor')


def test_programmbuendel_die_richtige_datei(monkeypatch, tmp_path):
    """Gesucht wird, was die Info.plist nennt – alphabetisch käme der Ordner »config« zuletzt und wäre kein Programm."""
    app = buendel(tmp_path)
    monkeypatch.setattr(ocr.korrlib, 'config', dict)
    assert ocr._find('scantailor', [], [str(tmp_path / '*.app')]) == str(app / 'Contents' / 'MacOS' / 'ScanTailor')
    ohne = tmp_path / 'Ohne Plist.app'
    (ohne / 'Contents' / 'MacOS').mkdir(parents=True)
    (ohne / 'Contents' / 'MacOS' / 'programm').write_text('x')
    assert ocr.app_binary(str(ohne)) == str(ohne / 'Contents' / 'MacOS' / 'programm')
    assert ocr.app_binary('/usr/local/bin/scantailor') == '/usr/local/bin/scantailor'


def test_choose_nimmt_auf_dem_mac_osascript(monkeypatch):
    """Auf dem Mac ohne Unterprozess der eigenen App: eine Mac-App bringt kein Tk mit."""
    monkeypatch.setattr(server.sys, 'platform', 'darwin')
    monkeypatch.setattr(server, 'mac_dialog', lambda kind: '/Users/x/' + kind)
    assert server.choose('folder') == '/Users/x/folder'


def test_choose_liest_das_ergebnis_aus_der_datei(monkeypatch, tmp_path):
    """Windows: die gepackte App hat keine Standardausgabe, der Unterprozess schreibt darum in eine Datei."""
    monkeypatch.setattr(server.sys, 'platform', 'win32')
    monkeypatch.setattr(server.tempfile, 'gettempdir', lambda: str(tmp_path))

    benutzt = []

    def run(cmd, **kw):
        benutzt.append(cmd[-1])
        with open(cmd[-1], 'w', encoding='utf-8') as f:
            f.write('C:/Buecher/Mein Buch\n')
        return lauf()
    monkeypatch.setattr(server.subprocess, 'run', run)
    assert server.choose('folder') == 'C:/Buecher/Mein Buch'
    assert not os.path.exists(benutzt[0])  # aufgeräumt


def test_dialog_schreibt_in_die_datei(tmp_path):
    """Nur der Weg über die Datei, ohne Tk: dialog() selbst braucht einen Bildschirm."""
    out = tmp_path / 'wahl.txt'
    fake = types.ModuleType('tkinter')
    fake.Tk = lambda: types.SimpleNamespace(withdraw=lambda: None, attributes=lambda *a: None)
    fake.filedialog = types.SimpleNamespace(askdirectory=lambda **kw: str(tmp_path / 'Buch'),
                                            askopenfilename=lambda **kw: '')
    sys.modules['tkinter'] = fake
    sys.modules['tkinter.filedialog'] = fake.filedialog
    try:
        server.dialog('folder', str(out))
    finally:
        del sys.modules['tkinter'], sys.modules['tkinter.filedialog']
    assert out.read_text(encoding='utf-8') == str(tmp_path / 'Buch')


def test_scantailor_macht_den_ordner_greifbar(monkeypatch, tmp_path):
    """Der Hinweis im Browser ist verdeckt, sobald ScanTailor davor liegt – darum Zwischenablage und Dateifenster."""
    getan = []
    monkeypatch.setattr(server.ocr, 'find_scantailor', lambda: str(tmp_path / 'scantailor-programm'))
    monkeypatch.setattr(server, 'new_folder', lambda title, source: ('Probe', str(tmp_path / 'Probe')))
    monkeypatch.setattr(server.ocr, 'export_pages', lambda src, ordner, fortschritt, abbruch: os.makedirs(ordner, exist_ok=True))
    monkeypatch.setattr(server.ocr, 'to_clipboard', lambda text: bool(getan.append(('zwischenablage', text))) or True)
    monkeypatch.setattr(server.ocr, 'reveal', lambda f: getan.append(('zeigen', f)))
    monkeypatch.setattr(server.ocr, 'launch', lambda exe: getan.append(('starten', exe)))
    pdf = tmp_path / 'buch.pdf'
    pdf.write_bytes(b'%PDF-1.4')

    r = server.scantailor(str(pdf), 'Probe', lambda *a: None, lambda: False)
    assert r['folder'] == str(tmp_path / 'Probe' / 'scantailor') and r['out'].endswith('out') and r['clipboard']
    assert [was for was, _ in getan] == ['zwischenablage', 'zeigen', 'starten']  # ScanTailor zuletzt: es soll vorn liegen
    assert getan[0][1] == r['folder'] and getan[1][1] == r['folder']


def test_zwischenablage_und_ordner_zeigen(monkeypatch):
    aufrufe = []
    monkeypatch.setattr(ocr.sys, 'platform', 'darwin')
    monkeypatch.setattr(ocr.subprocess, 'run', lambda cmd, **kw: aufrufe.append(cmd) or types.SimpleNamespace(returncode=0))
    monkeypatch.setattr(ocr.subprocess, 'Popen', lambda cmd, **kw: aufrufe.append(cmd))
    assert ocr.to_clipboard('/pfad/zum/ordner') is True
    assert ocr.reveal('/pfad/zum/ordner') is True
    assert aufrufe == [['pbcopy'], ['open', '/pfad/zum/ordner']]


def test_reveal_nur_fuer_vorhandene_ordner(lib, tmp_path):
    """Der Knopf »Ordner zeigen« darf nichts öffnen, was es nicht gibt."""
    assert lib.lpost('/api/reveal', dict(path=str(tmp_path / 'gibtsnicht'))) == (400, dict(error='quelle_fehlt'))


# ---- mitgeliefertes Tesseract

def test_gebuendeltes_tesseract_geht_vor(monkeypatch, tmp_path):
    """In der gepackten App zählt das mitgelieferte Tesseract, nicht irgendeines aus dem PATH."""
    (tmp_path / 'tesseract').mkdir()
    name = 'tesseract.exe' if os.name == 'nt' else 'tesseract'
    (tmp_path / 'tesseract' / name).write_text('x')
    monkeypatch.setattr(ocr.korrlib, 'config', dict)
    monkeypatch.setattr(ocr.shutil, 'which', lambda n: '/usr/local/bin/tesseract')
    assert ocr.find_tesseract() == '/usr/local/bin/tesseract'
    monkeypatch.setattr(ocr, 'BUNDLE', str(tmp_path))
    assert ocr.find_tesseract() == str(tmp_path / 'tesseract' / name)
    # von Hand gewählt (»Programm zeigen …«) gilt trotzdem weiter
    eigen = tmp_path / 'eigenes'
    eigen.write_text('x')
    monkeypatch.setattr(ocr.korrlib, 'config', lambda: dict(tesseract=str(eigen)))
    assert ocr.find_tesseract() == str(eigen)


def test_modelle_aus_dem_bundle(monkeypatch, tmp_path):
    (tmp_path / 'tesseract' / 'tessdata').mkdir(parents=True)
    monkeypatch.setattr(ocr, 'BUNDLE', str(tmp_path))
    monkeypatch.setattr(ocr, 'TESSDATA', str(tmp_path / 'gibtsnicht'))
    monkeypatch.setattr(ocr, '_langs', lambda tess, d=None: ['frak2021', 'deu'] if d else ['eng'])
    assert ocr.pick_model('t') == ('frak2021', str(tmp_path / 'tesseract' / 'tessdata'))
    assert ocr.pick_model('t', 'antiqua') == ('deu', str(tmp_path / 'tesseract' / 'tessdata'))


def test_ressourcen_liegen_beim_programm():
    """dict/, docs/ und die Oberfläche werden über HERE gefunden – gepackt ist das der Bundle-Ordner."""
    for name in ('reader.html', 'bibliothek.html', 'i18n.js', 'pyproject.toml'):
        assert os.path.exists(os.path.join(server.HERE, name))
    assert os.path.isdir(os.path.join(server.HERE, 'docs', 'de'))
    assert os.path.isdir(os.path.join(ocr.korrlib.HERE, 'dict'))


def test_alle_module_im_paket():
    """pyproject.toml zählt die Module einzeln auf: Fehlt eines, bricht eine gewöhnliche Installation (pip, später pipx)
    beim Start ab – die editierbare der Tests merkt es nicht (so wäre es epubbuch.py fast ergangen)."""
    import re
    from conftest import ROOT
    toml = open(os.path.join(ROOT, 'pyproject.toml'), encoding='utf-8').read()
    listed = set(re.findall(r'"(\w+)"', re.search(r'^py-modules = \[(.*)\]', toml, re.M).group(1)))
    assert listed == {f[:-3] for f in os.listdir(ROOT) if f.endswith('.py')}


# ---- Linux: Tesseract aus dem Paketmanager, Umgebung der Kindprozesse, Fenster des Starters

def test_linux_findet_tesseract_aus_dem_paket(monkeypatch):
    """Vom Schreibtisch gestartet hat das AppImage nicht immer den vollen PATH – /usr/bin wird darum auch so probiert."""
    monkeypatch.setattr(ocr.korrlib, 'config', dict)
    monkeypatch.setattr(ocr, 'BUNDLE', None)
    monkeypatch.setattr(ocr.shutil, 'which', lambda n: None)
    monkeypatch.setattr(ocr.glob, 'glob', lambda pat: [pat] if pat == '/usr/bin/tesseract' else [])
    assert ocr.find_tesseract() == '/usr/bin/tesseract'
    monkeypatch.setattr(ocr.glob, 'glob', lambda pat: [])
    assert ocr.find_tesseract() is None


def test_linux_gibt_kindprozessen_den_bibliothekspfad_des_systems(monkeypatch):
    """PyInstaller biegt LD_LIBRARY_PATH auf das Bundle; Tesseract und der Browser sollen ihre eigenen Bibliotheken laden."""
    monkeypatch.setattr(starter.sys, 'platform', 'linux')
    monkeypatch.setattr(starter.sys, 'frozen', True, raising=False)
    monkeypatch.setenv('LD_LIBRARY_PATH', '/tmp/bundle/_internal:/opt/lib')
    monkeypatch.setenv('LD_LIBRARY_PATH_ORIG', '/opt/lib')
    starter.unbundle_env()
    assert os.environ['LD_LIBRARY_PATH'] == '/opt/lib' and 'LD_LIBRARY_PATH_ORIG' not in os.environ
    monkeypatch.setenv('LD_LIBRARY_PATH', '/tmp/bundle/_internal')
    monkeypatch.delenv('LD_LIBRARY_PATH_ORIG', raising=False)
    starter.unbundle_env()
    assert 'LD_LIBRARY_PATH' not in os.environ
    # nicht gepackt (python starter.py) bleibt alles, wie es ist
    monkeypatch.setattr(starter.sys, 'frozen', False, raising=False)
    monkeypatch.setenv('LD_LIBRARY_PATH', '/tmp/bundle/_internal')
    starter.unbundle_env()
    assert os.environ['LD_LIBRARY_PATH'] == '/tmp/bundle/_internal'


def test_linux_starter_nimmt_tkinter_oder_die_konsole(monkeypatch):
    monkeypatch.setattr(starter.sys, 'platform', 'linux')
    monkeypatch.setitem(sys.modules, 'tkinter', types.ModuleType('tkinter'))
    assert starter.pick_ui(False) is starter.linux_ui
    monkeypatch.setitem(sys.modules, 'tkinter', None)  # nicht installiert
    assert starter.pick_ui(False) is starter.console_ui
    assert starter.pick_ui(True) is starter.console_ui


def test_linux_alert_ohne_display_stuerzt_nicht(monkeypatch, capsys):
    monkeypatch.setattr(starter.sys, 'platform', 'linux')
    monkeypatch.setattr(starter.os, 'name', 'posix')
    monkeypatch.setitem(sys.modules, 'tkinter', None)
    starter.alert('Der Port 8765 ist belegt')
    assert 'belegt' in capsys.readouterr().out
