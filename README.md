# Fraktur-Korrektor

[![Herunterladen – neueste Version](https://img.shields.io/github/v/release/Josi-create/fraktur-korrektor?label=Herunterladen&style=for-the-badge&color=2e7d32)](https://github.com/Josi-create/fraktur-korrektor/releases/latest)

**Neueste Version herunterladen:**
[Windows](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor_Setup.exe) ·
[Mac mit Apple-Chip](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-arm64.dmg) ·
[Mac mit Intel-Chip](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-x86_64.dmg) ·
[Linux](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-linux-x86_64.AppImage) –
[so wird es installiert](docs/de/install.md)

*English version: [README.en.md](README.en.md)*

**Alte Bücher lesen, berichtigen und daraus zitieren – auf Ihrem eigenen Rechner.**

Sie haben ein Buch in Frakturschrift als Scan, als PDF oder als Fotos aus dem Archiv und wollen damit arbeiten: es
lesen, darin suchen, daraus zitieren. Der Fraktur-Korrektor macht aus den Seitenbildern Text und zeigt beides
nebeneinander – links die Seite, wie sie gedruckt ist, rechts der erkannte Text. Wörter, die das Programm nicht kennt,
sind rot. Sie lesen das Buch einfach durch und verbessern dabei, was die Texterkennung (OCR) falsch gelesen hat. Am
Ende steht ein sauberer, durchsuchbarer Text.

<!-- Bildschirmfoto: Seitenbild links, Text rechts, ein rotes Wort mit Vorschlägen (#20) -->

Wer beim Lesen exzerpiert, macht aus einer markierten Stelle mit einer Taste einen Zettel für
[Obsidian](https://obsidian.md): das Zitat mit gedruckter Seitenzahl und Verweis auf die Quelle. So wächst beim Lesen
ein Zettelkasten nach dem Vorbild Niklas Luhmanns – das Programm liefert die Exzerpte, das Verknüpfen und
Weiterdenken geschieht in Obsidian.

Ihre Bücher und Notizen verlassen den Rechner nicht. Das Programm ist frei (GPL), kostet nichts und läuft unter
Windows, macOS und Linux.

## Was es kann

- **Einlesen, was Sie haben.** PDF, Scans oder Fotos, EPUB, ein Export aus Transkribus – Sie zeigen dem Programm die
  Datei, es erkennt selbst, was es ist ([Ein Buch öffnen](docs/de/add-book.md)). Die Texterkennung samt Modell für
  Fraktur ist eingebaut; eine Ampel zeigt danach, wie gut sie gelungen ist und was helfen würde
  ([PDF oder Bilder einlesen](docs/de/pdf-import.md)).
- **Lesen und berichtigen in einem Durchgang.** Seitenbild und Text laufen mit, rote Wörter bekommen Vorschläge. Das
  Wörterbuch richtet sich nach dem Erscheinungsjahr: »Thür« ist in einem Buch von 1880 richtig. Alles geht mit der
  Tastatur, jede Korrektur ist sofort gespeichert ([Bedienung](docs/de/usage.md)).
- **Exzerpieren.** Zettel für Obsidian mit Zitat, Seite und Zeile – auch aus den Markierungen, die Sie auf dem Kindle
  gemacht haben ([Markierungen vom Kindle](docs/de/kindle.md)).
- **Mitnehmen.** Das Buch als PDF sichern: Seitenbilder, durchsuchbarer Text, Inhaltsverzeichnis und Ihr ganzer
  Arbeitsstand – lesbar in jedem PDF-Programm und auf einem anderen Rechner wieder ein Buch
  ([Ein Buch als PDF sichern](docs/de/pdf-sichern.md)).

## Für wen?

- **Historikerinnen und Historiker**, die mit gedruckten Quellen in Fraktur arbeiten.
- **Familienforscher** mit Ortschroniken, Heimatbüchern und alten Zeitungen – zweispaltiger Satz wird Spalte für
  Spalte gelesen.
- **Alle, die exzerpieren** und ihre Zettel in Obsidian sammeln.

So sieht ein Zettel aus:

    **Anmerkung**

    (Ihr Gedanke dazu)

    ---

    > Die Kolonisten zogen nach Rußland und der Weg war weit.

    Seite 57, Zeile 3–4, [[0 Quellenangabe|Leibbrandt 1928]]

## Installieren

Fertige Programme mit allem, was man zum Einlesen, Vorbereiten der Scans und Korrigieren braucht – auch der
Texterkennung samt Frakturmodell; es muss nichts nachinstalliert werden (Linux: Tesseract aus dem Paketmanager).
Nur für besonders schwierige Vorlagen – zum Bund hin gewölbte Seiten, Flecken, ungleichmäßiges Licht – lässt sich
zusätzlich das freie Programm ScanTailor einbinden ([Werkzeuge installieren](docs/de/install-tools.md)):

| | |
|---|---|
| Windows | [Fraktur-Korrektor_Setup.exe](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor_Setup.exe) |
| Mac, Apple Silicon | [Fraktur-Korrektor-macos-arm64.dmg](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-arm64.dmg) |
| Mac, Intel | [Fraktur-Korrektor-macos-x86_64.dmg](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-x86_64.dmg) |
| Linux (x86_64) | [Fraktur-Korrektor-linux-x86_64.AppImage](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-linux-x86_64.AppImage) |

Schritt für Schritt, auch zum Beenden und Aktualisieren: [Programm installieren](docs/de/install.md) ·
[Installing the program](docs/en/install.md). Alle Fassungen samt portablem ZIP stehen auf der
[Seite der Veröffentlichungen](https://github.com/Josi-create/fraktur-korrektor/releases/latest). Wer das Programm aus
dem Quelltext starten möchte: [CONTRIBUTING.md](CONTRIBUTING.md#einrichtung-für-entwickler).

## Hilfe

Alles geht mit der Tastatur; die wichtigsten Tasten stehen im Programm immer unten unter Bild und Text, `F1` öffnet die Hilfe.

- [Hilfe: Überblick](docs/de/index.md) · [Ein Buch öffnen](docs/de/add-book.md) · [PDF oder Bilder einlesen](docs/de/pdf-import.md) ·
  [Bücher selbst fotografieren](docs/de/fotografieren.md) · [Mit Transkribus arbeiten](docs/de/transkribus.md) ·
  [Bedienung und alle Tasten](docs/de/usage.md) · [Programm installieren](docs/de/install.md) ·
  [Werkzeuge installieren](docs/de/install-tools.md) · [Häufige Fragen](docs/de/faq.md)
- English: [Help](docs/en/index.md) · [Opening a book](docs/en/add-book.md) · [Reading in a PDF or images](docs/en/pdf-import.md) ·
  [Photographing books yourself](docs/en/fotografieren.md) · [Working with Transkribus](docs/en/transkribus.md) ·
  [Usage](docs/en/usage.md) · [Installing the program](docs/en/install.md) ·
  [Installing the tools](docs/en/install-tools.md) · [FAQ](docs/en/faq.md)
- Dieselben Seiten als Website: <https://josi-create.github.io/fraktur-korrektor/>

## Mitmachen

Fehlerberichte und Vorschläge bitte über die [Issue-Vorlagen](../../issues/new/choose) – ohne Seitenbilder oder Texte aus
dem Buch (Urheberrecht). Wie man mitarbeitet, auch ohne zu programmieren (Wörterbücher, Hilfetexte, Übersetzung,
Probelesen), wie man das Programm aus dem Quelltext startet und was im Code nicht brechen darf, steht in
[CONTRIBUTING.md](CONTRIBUTING.md) ([English](CONTRIBUTING.en.md)); was geplant ist, in der [ROADMAP](ROADMAP.md).
Für alle gilt der [Verhaltenskodex](CODE_OF_CONDUCT.md); Sicherheitslücken bitte nach [SECURITY.md](SECURITY.md)
melden, nicht als öffentliches Issue. Zitieren: [CITATION.cff](CITATION.cff).

## Unterstützen

Das Programm entsteht in der Freizeit. Wer mag, spendiert einen Kaffee: <https://buymeacoffee.com/josicreate> ☕
Genauso willkommen sind Fehlerberichte, Wünsche und Mitarbeit (siehe oben).

## Lizenz

[GPL-3.0-or-later](LICENSE). Das mitgelieferte Wörterbuch hat eigene Lizenzangaben, siehe [dict/](dict/README.md).
Für PDF-Dateien wird PyMuPDF benutzt (AGPL-3.0, mit der GPL-3.0 verträglich). Die Hilfetexte stehen unter CC BY-SA 4.0.
