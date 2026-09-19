"""Lädt die Tesseract-Modelle, die mit der App ausgeliefert werden, nach vendor/tesseract/tessdata.

frak2021 (UB Mannheim) liest Fraktur, deu ist für Bücher in Antiqua da. Beide werden mitgeliefert, damit nach
der Installation nichts mehr heruntergeladen oder eingerichtet werden muss – die Zielgruppe soll doppelklicken
und loslegen. Dieselben Dateien auf Windows und Mac, darum der Download statt der Sprachpakete von Homebrew
(die zudem über ein Gigabyte groß sind).

Aufruf: python scripts/models.py [zielordner]
"""
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "vendor" / "tesseract" / "tessdata"

# Name im Bundle -> (Adresse, Mindestgroesse). Die Groesse faengt abgebrochene Downloads und Fehlerseiten ab.
MODELS = {
    "frak2021.traineddata": (
        "https://ub-backup.bib.uni-mannheim.de/~stweil/tesstrain/frak2021/tessdata_fast/frak2021_0.905.traineddata",
        5_000_000,
    ),
    "deu.traineddata": (
        "https://github.com/tesseract-ocr/tessdata_fast/raw/4.1.0/deu.traineddata",
        1_400_000,
    ),
}


def fetch(target: Path = TARGET) -> Path:
    target = Path(target)
    target.mkdir(parents=True, exist_ok=True)
    for name, (url, minimum) in MODELS.items():
        out = target / name
        if out.is_file() and out.stat().st_size >= minimum:
            print(f"  {name}: schon vorhanden")
            continue
        print(f"  {name}: lade von {url} …")
        tmp = out.with_name(name + ".tmp")
        try:
            with urllib.request.urlopen(url, timeout=300) as response, open(tmp, "wb") as f:
                shutil.copyfileobj(response, f)
        except OSError as e:
            sys.exit(f"Download fehlgeschlagen ({name}): {e}")
        size = tmp.stat().st_size
        if size < minimum:
            tmp.unlink()
            sys.exit(f"{name} ist unvollstaendig ({size} Bytes, erwartet mindestens {minimum}) – Quelle: {url}")
        tmp.replace(out)
        print(f"    {size / 1e6:.1f} MB")
    return target


if __name__ == "__main__":
    fetch(Path(sys.argv[1]) if len(sys.argv) > 1 else TARGET)
