# Roadmap: Vom Skript zum freien GitHub-Projekt

Ziel: Der Fraktur-Korrektor wird als Open-Source-Projekt veröffentlicht – benutzbar auch für Menschen
ohne Technik-Erfahrung (Historiker, Bibliothekare, Studierende), mit sauberer Dokumentation auf Deutsch
und Englisch, und offen für Mitarbeit.

Der Arbeitsstand steht in den [Milestones](../../milestones) und [Issues](../../issues); diese Datei gibt den Überblick.

## Grundsätze

- **`main` ist immer benutzbar.** Das Programm wird täglich produktiv eingesetzt; jede Änderung muss mit
  vorhandenen Buchordnern weiter funktionieren (Dateiformat abwärtskompatibel).
- **Tests laufen nie gegen echte Buchdaten**, sondern gegen das Beispielbuch bzw. eine Kopie, auf eigenem Port.
- **Wir ersetzen keine OCR.** Nische: Lesen und Korrigieren in einem Durchgang, tastaturgesteuert, mit Serienkorrektur.
- Das Repository bleibt privat, bis die Installer stehen – der erste Eindruck zählt.

## Entscheidungen

| Thema | Entscheidung |
|---|---|
| Lizenz Code | GPL-3.0-or-later (verträglich mit freien Hunspell-Wörterbüchern, PyMuPDF/AGPL, ScanTailor) |
| Lizenz Doku | CC BY-SA 4.0 |
| Sprachen | Deutsch und Englisch, für Doku und Oberfläche |
| Doku-Quelle | Markdown unter `docs/de`, `docs/en` – auf GitHub lesbar und im Programm unter „Hilfe“ |
| Spenden | „Buy me a coffee“: `.github/FUNDING.yml`, Link in README und im Hilfe-Menü |
| Mac | signierte und notarisierte App (Apple-Entwicklerkonto vorhanden), Test auf Intel-MacBook |

## Meilensteine

### M1 – Fundament
Lizenz, freies Wörterbuch statt fest verdrahtetem Pfad, Paketierung (`pyproject.toml`), Beispielbuch
(gemeinfrei), Tests (pytest), CI auf Windows/macOS/Linux, Changelog, Prüfung der Git-Historie.

### M2 – Bibliothek und Hilfe im Programm
Start ohne Kommandozeilen-Argumente, Startseite mit Buchauswahl, Import eines Transkribus-Exports per
Knopfdruck, Hilfe-Seite im Browser (rendert `docs/`), Oberfläche zweisprachig, Spenden-Link.

### M3 – PDF-Import
PDF → Seitenbilder (PyMuPDF), Texterkennung mit Tesseract (Fraktur-Modelle) → `NNN.txt` + `lines.json`,
Fortschrittsanzeige, Qualitätsampel (Tesseract-Konfidenz + Wörterbuchquote + Zeilenend-Hapax) mit
Empfehlung „besser mit Transkribus“ bzw. „vorher mit ScanTailor aufbereiten“, ScanTailor-Button
(Bilder exportieren, ScanTailor starten, Ergebnis wieder einlesen).

### M4 – Installation für alle
Windows: `.exe` + Installer (PyInstaller, Inno Setup). Mac: signierte, notarisierte `.app` im `.dmg`.
Build automatisch per GitHub Actions bei jedem Versions-Tag. Assistent beim ersten Start prüft
Wörterbuch, Tesseract, ScanTailor.

### M5 – Dokumentation
README (EN/DE) mit Bildschirmfotos, Installationsanleitungen Windows/Mac für Einsteiger, Erste Schritte,
Bedienung, Arbeitsablauf Transkribus → Fraktur-Korrektor, Arbeitsablauf PDF/Tesseract, ScanTailor,
Vergleich mit anderen Programmen (ABBYY FineReader, Transkribus, Tesseract, OCR4all/LAREX,
eScriptorium, gImageReader, PoCoTo …), FAQ und Fehlerbehebung.

### M6 – Veröffentlichung
CONTRIBUTING, Code of Conduct, Issue-/PR-Vorlagen (DE/EN), SECURITY, CITATION.cff, Zenodo-DOI,
Labels, Discussions, Topics; Repository öffentlich, Release v0.9 (Beta); Betatest mit 2–3 Personen
aus der Zielgruppe; v1.0.

### M7 – Bekanntmachen
Vorstellungstext (DE/EN), Kurzvideo; gestaffelt in: InetBib, openbiblio.social, o-bib/b.i.t.online,
H-Soz-Kult, L.I.S.A., Archivalia, hypotheses.org, NFDI4Memory, DHd-Liste/-Blog, Humanist,
Transkribus- und Tesseract-Foren, CompGen/Ahnenforschung.net, Wikisource-Skriptorium, Reddit, Show HN.

## Später

- Zeilen teilen/verbinden mit Erhalt der Bildzuordnung
- Epub-Export (Kapitel, Fußnoten)
- Zugriffsschutz für `--lan`
- `pipx install fraktur-korrektor` (PyPI)
