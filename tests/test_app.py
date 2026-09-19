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
    monkeypatch.setattr(starter.webbrowser, 'open', geoeffnet.append)
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
    monkeypatch.setattr(starter.webbrowser, 'open', lambda url: None)
    assert starter.main(['-psn_0_123456', '--port', '8765']) == 0


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


def test_mac_dialog_loest_programmbuendel_auf(monkeypatch, tmp_path):
    """Für ScanTailor wird die Datei im Bündel gebraucht, nicht der Ordner ScanTailor.app."""
    app = tmp_path / 'ScanTailor.app'
    (app / 'Contents' / 'MacOS').mkdir(parents=True)
    (app / 'Contents' / 'MacOS' / 'scantailor').write_text('x')
    monkeypatch.setattr(server.subprocess, 'run', lambda cmd, **kw: lauf(str(app) + '/\n'))
    assert server.mac_dialog('exe') == str(app / 'Contents' / 'MacOS' / 'scantailor')


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
