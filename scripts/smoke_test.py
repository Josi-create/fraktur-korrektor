"""Prueft die gepackte App: startet sie, fragt den Server, liest ein PDF mit dem mitgelieferten Tesseract ein.

Das ist der Test, den pytest nicht leisten kann - er laeuft gegen das fertige Bundle und faellt auf, wenn eine
Ressource fehlt (Woerterbuch, Hilfe, Oberflaeche) oder Tesseract im Bundle nicht startet. Kein echter Buchordner:
eigener freier Port, FRAKTUR_HOME in einem Wegwerf-Ordner.

    python scripts/smoke_test.py "dist/Fraktur-Korrektor.app"
    python scripts/smoke_test.py "dist\\Fraktur-Korrektor\\Fraktur-Korrektor.exe"
"""
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


def binary(path: Path) -> Path:
    """Bei einer .app die Datei in Contents/MacOS."""
    if path.suffix == ".app":
        inner = sorted((path / "Contents" / "MacOS").iterdir())
        if not inner:
            sys.exit(f"Keine ausfuehrbare Datei in {path}/Contents/MacOS")
        return inner[0]
    return path


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def get(port: int, path: str, timeout: int = 30):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=timeout) as r:
        return r.status, r.read()


def post(port: int, path: str, body: dict, timeout: int = 30):
    data = json.dumps(body).encode("utf-8")
    with urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data), timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def make_pdf(path: Path) -> bool:
    """Ein zweiseitiges PDF ohne brauchbare Textebene gibt es nur mit PyMuPDF; sonst entfaellt der OCR-Durchlauf."""
    try:
        import fitz
    except ImportError:
        return False
    lines = ["Die Kolonisten zogen nach Russland, und der", "Weg war weit. Sie dachten an die Zukunft",
             "und an die Heimat, die sie verlassen hatten."]
    doc = fitz.open()
    for n in range(2):
        page = doc.new_page(width=420, height=595)
        page.insert_text((150, 50), "— %d —" % (n + 7), fontsize=11, fontname="tiro")
        for k, line in enumerate(lines):
            page.insert_text((50, 100 + 22 * k), line, fontsize=13, fontname="tiro")
    doc.save(str(path))
    doc.close()
    return True


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    exe = binary(Path(sys.argv[1]).resolve())
    if not exe.is_file():
        sys.exit(f"Nicht gefunden: {exe}")

    port = free_port()
    tmp = Path(tempfile.mkdtemp(prefix="fraktur-rauchtest-"))
    env = dict(os.environ, FRAKTUR_HOME=str(tmp / "home"), PYTHONIOENCODING="utf-8")
    print(f"Starte {exe} auf Port {port} (FRAKTUR_HOME={tmp / 'home'})")
    proc = subprocess.Popen([str(exe), "--port", str(port), "--no-browser", "--no-ui"],
                            env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def fail(text):
        proc.kill()
        out = proc.stdout.read().decode("utf-8", "replace") if proc.stdout else ""
        print(f"FEHLGESCHLAGEN: {text}\n--- Ausgabe der App ---\n{out}", file=sys.stderr)
        return 1

    try:
        deadline = time.time() + 120
        while True:
            if proc.poll() is not None:
                return fail(f"Die App hat sich sofort beendet (Code {proc.returncode}).")
            try:
                ping = json.loads(get(port, "/api/ping", timeout=5)[1].decode("utf-8"))
                break
            except OSError:
                if time.time() > deadline:
                    return fail("Der Server antwortet nicht.")
                time.sleep(0.2)
        if ping.get("app") != "fraktur-korrektor":
            return fail(f"Unerwartete Antwort auf /api/ping: {ping}")
        print(f"  Server antwortet, Version {ping.get('version') or '?'}")

        # Ressourcen aus dem Bundle: Oberflaeche, Uebersetzung, Hilfe (docs/), Bibliothek (dict/ laedt erst spaeter)
        for path, muss in (("/", b"i18n.js"), ("/i18n.js", b"function"), ("/hilfe/de/index", b"Fraktur"),
                           ("/hilfe/en/usage", b"<table")):   # die Tabelle beweist, dass die Markdown-Erweiterung mit im Bundle ist
            code, body = get(port, path)
            if code != 200 or muss not in body:
                return fail(f"{path} liefert {code} ohne den erwarteten Inhalt {muss!r}")
        print("  Oberflaeche, Uebersetzung und Hilfeseiten kommen aus dem Bundle")

        tools = json.loads(get(port, "/api/tools")[1].decode("utf-8"))
        print(f"  Werkzeuge: {tools}")
        if not tools.get("tesseract"):
            return fail("Tesseract wurde nicht gefunden - ist vendor/tesseract mitgebaut?")
        app_root = Path(sys.argv[1]).resolve()
        app_root = app_root if app_root.is_dir() else app_root.parent
        if app_root not in Path(tools["tesseract"]).resolve().parents:
            return fail(f"Das gefundene Tesseract liegt nicht in der App, sondern unter {tools['tesseract']} - "
                        "mitgeliefert wurde es also nicht.")
        if tools.get("model") != "frak2021":
            return fail(f"Das Fraktur-Modell fehlt (gefunden: {tools.get('model')}).")
        if tools.get("antiqua") != "deu":
            return fail(f"Das Modell deu fehlt (gefunden: {tools.get('antiqua')}).")
        if not tools.get("pdf"):
            return fail("PyMuPDF fehlt im Bundle - PDFs lassen sich nicht oeffnen.")

        pdf = tmp / "probe.pdf"
        if not make_pdf(pdf):
            print("  PyMuPDF fehlt im Build-Python: OCR-Durchlauf uebersprungen")
        else:
            job = post(port, "/api/import_ocr", dict(source=str(pdf), title="Rauchtest", script="antiqua",
                                                     target=str(tmp / "buecher")))["job"]
            for _ in range(1800):
                state = json.loads(get(port, f"/api/job/{job}")[1].decode("utf-8"))
                if state["state"] != "running":
                    break
                time.sleep(0.2)
            else:
                return fail("Das Einlesen wird nicht fertig.")
            if state["state"] != "done":
                return fail(f"Einlesen fehlgeschlagen: {state}")
            result = state["result"]
            text = (Path(result["folder"]) / "001.txt").read_text(encoding="utf-8")
            if "Kolonisten" not in text:
                return fail(f"Der erkannte Text passt nicht:\n{text}")
            print(f"  PDF eingelesen: {result['pages']} Seiten, Ampel {result['quality']['level']}, "
                  f"erste Zeile {text.splitlines()[0]!r}")

        print("RAUCHTEST BESTANDEN")
        return 0
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main())
