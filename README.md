# Fraktur-Korrektor

Lesen und Korrekturlesen in einem: ein kleiner lokaler „E-Book-Reader“ für OCR-Text gescannter
(Fraktur-)Bücher. Links das Seitenbild, rechts der erkannte Text. Ein Lesecursor (aktuelle Zeile,
immer im oberen Viertel) hält Bild und Text synchron. Fragliche Wörter (nicht im Wörterbuch, unsichere
automatische Ersetzungen) sind rot markiert. Alles ist mit der Tastatur bedienbar.

Ziel ist ein sauberer Text als Grundlage für ein Epub.

## Bedienung

Alles geht mit der Tastatur; die wichtigsten Tasten stehen im Programm immer oben rechts, `F1` öffnet die Hilfe.

- [Hilfe: Überblick](docs/de/index.md) · [Ein Buch hinzufügen](docs/de/add-book.md) · [PDF oder Bilder einlesen](docs/de/pdf-import.md) ·
  [Mit Transkribus arbeiten](docs/de/transkribus.md) · [Bedienung und alle Tasten](docs/de/usage.md) · [Werkzeuge installieren](docs/de/install-tools.md)
- English: [Help](docs/en/index.md) · [Adding a book](docs/en/add-book.md) · [Reading in a PDF or images](docs/en/pdf-import.md) ·
  [Working with Transkribus](docs/en/transkribus.md) · [Usage](docs/en/usage.md) · [Installing the tools](docs/en/install-tools.md)

Jede Korrektur wird sofort in die Textdatei geschrieben und in `korrekturen.log` protokolliert; die Leseposition steht in
`lesezeichen.json`. Die Dateien dürfen parallel in einem Editor bearbeitet werden (die Zeilenzahl einer Seite dabei nicht
ändern, sonst fehlt die Bildzuordnung).

## Start

    pip install spylls markdown pymupdf
    py server.py                  Bibliothek: Bücher öffnen, Transkribus-Export importieren, PDF/Bilder mit Tesseract einlesen
    py server.py <buchordner>     direkt ein Buch öffnen

Optionen: `--port 8765`, `--dic <hunspell-pfad-ohne-endung>`, `--title "…"`, `--no-browser`, `--lan`.
Die Oberfläche gibt es auf Deutsch und Englisch (Umschalter oben rechts).

Mit `--lan` ist die App auch von anderen Rechnern im lokalen Netz erreichbar (die Adresse wird beim Start angezeigt;
Windows fragt beim ersten Mal nach der Firewall-Freigabe für „Private Netzwerke“). Es gibt keinen Passwortschutz – nur im eigenen Heimnetz verwenden.

Wörterbuch: mitgeliefert wird ein freies Hunspell-Wörterbuch für die deutsche Rechtschreibung von 1901
(siehe [dict/](dict/README.md)). Ein anderes lässt sich per `--dic`, Umgebungsvariable `FRAKTUR_DIC` oder
`"dic"` in `~/.fraktur-korrektor/config.json` wählen. Der erste Start mit einem neuen Buch dauert etwas länger,
danach sind die Prüfergebnisse zwischengespeichert.

## Buchordner

    NNN.txt        eine Datei je Seite: optional "# Kopfzeile", Haupttext, "---", Fußnoten
    lines.json     Zeilengeometrie je Seite (aus PAGE-XML, siehe tools/build_text.py)
    img/NNN.png    Seitenbilder (PNG oder JPG)
    autokorr.log   optional: Protokoll der automatischen Ersetzungen (unsichere werden orange markiert)
    whitelist.txt  bestätigte Wörter
    lesezeichen.json
    korrekturen.log  Protokoll aller Korrekturen (Zeit, Art, Seite, Zeile, alt, neu)
    qualitaet.json   nur nach dem Einlesen mit Tesseract: Konfidenz und Wörterbuchquote je Seite, Ampel

Buchdaten gehören **nicht** in dieses Repository.

## Werkzeuge (tools/)

Die Importwege stecken in `pagexml.py` (Transkribus) und `ocr.py` (PDF/Bilder → Tesseract; auch als
`py ocr.py <pdf-oder-bilderordner> <buchordner>` aufrufbar).

- `page2txt.py` – Text aus Transkribus-PAGE-XML
- `build_text.py` – PAGE-XML → `NNN.txt` + `lines.json`, trennt Fußnoten (Grundlinienabstand, „N)“-Anfang); dasselbe macht der Import in der Bibliothek (`pagexml.py`)
- `autokorr.py` – typische Fraktur-Verwechslungen (l/t/k/f, b/d, B/W/V, s/f, u/n …) gegen Wörterbuch und Korpusfrequenz korrigieren
- `ocr_quality.py` – Qualitätsmaß je Seite (Hapax-Quote der Zeilenendwörter)

## Geplant

Siehe [ROADMAP.md](ROADMAP.md): Installer für Windows
und Mac, zweisprachige Dokumentation; später Zeilen teilen/verbinden und Epub-Export.

## Entwicklung

    pip install -e .[dev]
    pytest

Die Tests starten eigene Serverinstanzen auf freien Ports mit einem Wegwerf-Buch im Temp-Ordner.

## Unterstützen

Das Programm entsteht in der Freizeit. Wer mag, spendiert einen Kaffee: <https://buymeacoffee.com/josicreate> ☕
Genauso willkommen sind Fehlerberichte, Wünsche und Mitarbeit.

## Lizenz

[GPL-3.0-or-later](LICENSE). Das mitgelieferte Wörterbuch hat eigene Lizenzangaben, siehe [dict/](dict/README.md).
Für PDF-Dateien wird PyMuPDF benutzt (AGPL-3.0, mit der GPL-3.0 verträglich).
Mitarbeit ist willkommen.
