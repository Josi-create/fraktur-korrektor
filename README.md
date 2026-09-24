# Fraktur-Korrektor

Lesen und Korrekturlesen in einem: ein kleiner lokaler „E-Book-Reader“ für OCR-Text gescannter
(Fraktur-)Bücher. Links das Seitenbild, rechts der erkannte Text. Ein Lesecursor (aktuelle Zeile,
immer im oberen Viertel) hält Bild und Text synchron. Fragliche Wörter (nicht im Wörterbuch, unsichere
automatische Ersetzungen) sind rot markiert. Alles ist mit der Tastatur bedienbar.

Ziel ist ein sauberer Text als Grundlage für ein Epub.

## Bedienung

Alles geht mit der Tastatur; die wichtigsten Tasten stehen im Programm immer oben rechts, `F1` öffnet die Hilfe.

- [Hilfe: Überblick](docs/de/index.md) · [Ein Buch öffnen](docs/de/add-book.md) · [PDF oder Bilder einlesen](docs/de/pdf-import.md) ·
  [Mit Transkribus arbeiten](docs/de/transkribus.md) · [Bedienung und alle Tasten](docs/de/usage.md) ·
  [Programm installieren](docs/de/install.md) · [Werkzeuge installieren](docs/de/install-tools.md)
- English: [Help](docs/en/index.md) · [Opening a book](docs/en/add-book.md) · [Reading in a PDF or images](docs/en/pdf-import.md) ·
  [Working with Transkribus](docs/en/transkribus.md) · [Usage](docs/en/usage.md) ·
  [Installing the program](docs/en/install.md) · [Installing the tools](docs/en/install-tools.md)

Jede Korrektur wird sofort in die Textdatei geschrieben und in `korrekturen.log` protokolliert; die Leseposition steht in
`lesezeichen.json`. Die Dateien dürfen parallel in einem Editor bearbeitet werden (die Zeilenzahl einer Seite dabei nicht
ändern, sonst fehlt die Bildzuordnung).

## Installieren

Fertige Programme, in denen alles steckt – auch die Texterkennung, es muss nichts nachinstalliert werden:

| | |
|---|---|
| Windows | [Fraktur-Korrektor_Setup.exe](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor_Setup.exe) |
| Mac, Apple Silicon | [Fraktur-Korrektor-macos-arm64.dmg](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-arm64.dmg) |
| Mac, Intel | [Fraktur-Korrektor-macos-x86_64.dmg](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-x86_64.dmg) |

Schritt für Schritt, auch zum Beenden und Aktualisieren: [Programm installieren](docs/de/install.md) ·
[Installing the program](docs/en/install.md). Alle Fassungen samt portablem ZIP stehen auf der
[Seite der Veröffentlichungen](https://github.com/Josi-create/fraktur-korrektor/releases/latest).

## Start aus dem Quelltext

    pip install spylls markdown pymupdf
    py server.py                  Bibliothek; »Öffnen …« erkennt selbst: Buchordner, PDF, EPUB (+ gleichnamiges PDF), Bilder, Transkribus-Export
    py server.py <buchordner>     direkt ein Buch öffnen

Optionen: `--port 8765`, `--dic <hunspell-pfad-ohne-endung>`, `--title "…"`, `--no-browser`, `--lan`.
Die Oberfläche gibt es auf Deutsch und Englisch (Umschalter oben rechts).

Mit `--lan` ist die App auch von anderen Rechnern im lokalen Netz erreichbar (die Adresse wird beim Start angezeigt;
Windows fragt beim ersten Mal nach der Firewall-Freigabe für „Private Netzwerke“). Es gibt keinen Passwortschutz – nur im eigenen Heimnetz verwenden.

Wörterbücher: mitgeliefert werden freie Hunspell-Wörterbücher für die deutsche Rechtschreibung von 1901 und für die neue
(siehe [dict/](dict/README.md)); welche Rechtschreibung gilt, wird je Buch gewählt (Taste `D`, Vorschlag nach Erscheinungsjahr).
Ein anderes Wörterbuch für die Rechtschreibung von 1901 lässt sich per `--dic`, Umgebungsvariable `FRAKTUR_DIC` oder
`"dic"` in `~/.fraktur-korrektor/config.json` wählen. Der erste Start mit einem neuen Buch dauert etwas länger,
danach sind die Prüfergebnisse zwischengespeichert.

## Buchordner

    NNN.txt        eine Datei je Seite: optional "# Kopfzeile", Haupttext, "---", Fußnoten; Auszeichnung als XHTML wie im
                   EPUB (<table><tr><td>, <h2>, <em> …) – jede Zeile bleibt eine Zeile
    lines.json     Zeilengeometrie je Seite (aus PAGE-XML, siehe tools/build_text.py)
    img/NNN.png    Seitenbilder (PNG oder JPG)
    autokorr.log   optional: Protokoll der automatischen Ersetzungen (unsichere werden orange markiert)
    whitelist.txt  bestätigte Wörter
    lesezeichen.json
    korrekturen.log  Protokoll aller Korrekturen (Zeit, Art, Seite, Zeile, alt, neu)
    buch.json        Erscheinungsjahr (geschätzt) und geltende Rechtschreibung
    qualitaet.json   nur nach dem Einlesen mit Tesseract: Konfidenz und Wörterbuchquote je Seite, Ampel

Buchdaten gehören **nicht** in dieses Repository.

## Werkzeuge (tools/)

Was geöffnet wird, erkennt `finder.py`. Die Importwege stecken in `pagexml.py` (Transkribus), `epub.py` (EPUB, auch auf die Zeilen
eines PDF gelegt) und `ocr.py` (PDF/Bilder → Tesseract bzw. vorhandene Textebene; auch als
`py ocr.py <pdf-oder-bilderordner> <buchordner>` aufrufbar). `pdfbuch.py` sichert ein Buch als PDF mit dem Arbeitsstand
im Anhang und liest es wieder ein. `scans.py` bereitet abfotografierte Seiten vor (Doppelseiten teilen, geraderichten; auch als
`py scans.py <pdf-oder-bilderordner> [<zielordner>]` aufrufbar).

- `page2txt.py` – Text aus Transkribus-PAGE-XML
- `build_text.py` – PAGE-XML → `NNN.txt` + `lines.json`, trennt Fußnoten (Grundlinienabstand, „N)“-Anfang); dasselbe macht der Import in der Bibliothek (`pagexml.py`)
- `autokorr.py` – typische Fraktur-Verwechslungen (l/t/k/f, b/d, B/W/V, s/f, u/n …) gegen Wörterbuch und Korpusfrequenz korrigieren
- `ocr_quality.py` – Qualitätsmaß je Seite (Hapax-Quote der Zeilenendwörter)

## Geplant

Siehe [ROADMAP.md](ROADMAP.md): Installer für Windows
und Mac, zweisprachige Dokumentation; später Epub-Export.

## Entwicklung

    pip install -e .[dev]
    pytest

Die Tests starten eigene Serverinstanzen auf freien Ports mit einem Wegwerf-Buch im Temp-Ordner.

Auf dem Mac nimmt `./mac_lesen.sh` einem das ab: Es legt beim ersten Mal `.venv` an und startet den Server
(`./mac_lesen.sh <buchordner> --lan`), baut mit `./mac_lesen.sh build` die App samt DMG lokal und lässt mit
`./mac_lesen.sh test` die Tests laufen.

## Mitmachen

Fehlerberichte und Vorschläge bitte über die [Issue-Vorlagen](../../issues/new/choose) – ohne Seitenbilder oder Texte aus
dem Buch (Urheberrecht). Wie man mitarbeitet, auch ohne zu programmieren (Wörterbücher, Hilfetexte, Übersetzung,
Probelesen), und was im Code nicht brechen darf, steht in [CONTRIBUTING.md](CONTRIBUTING.md)
([English](CONTRIBUTING.en.md)). Für alle gilt der [Verhaltenskodex](CODE_OF_CONDUCT.md); Sicherheitslücken bitte
nach [SECURITY.md](SECURITY.md) melden, nicht als öffentliches Issue. Zitieren: [CITATION.cff](CITATION.cff).

## Unterstützen

Das Programm entsteht in der Freizeit. Wer mag, spendiert einen Kaffee: <https://buymeacoffee.com/josicreate> ☕
Genauso willkommen sind Fehlerberichte, Wünsche und Mitarbeit (siehe oben).

## Lizenz

[GPL-3.0-or-later](LICENSE). Das mitgelieferte Wörterbuch hat eigene Lizenzangaben, siehe [dict/](dict/README.md).
Für PDF-Dateien wird PyMuPDF benutzt (AGPL-3.0, mit der GPL-3.0 verträglich). Die Hilfetexte stehen unter CC BY-SA 4.0.
