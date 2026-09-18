# Änderungen

Format nach [Keep a Changelog](https://keepachangelog.com/de/), Versionen nach [SemVer](https://semver.org/lang/de/).

## [Unveröffentlicht]

### Neu
- Durchsuchbare PDFs: vorhandenen Text übernehmen statt neu erkennen (570 Seiten in wenigen Sekunden); Zeilen werden
  anhand der Grundlinie geordnet, Randzeichen vom mitgescannten Seitenrand entfernt.
- Seitenbilder werden unverändert aus dem PDF entnommen, wenn die Seite aus einem einzigen Bild besteht (schneller,
  kein Qualitätsverlust); der Fortschrittsbalken zählt fertige Seiten statt der Reihenfolge.
- PDF oder Bilderordner einlesen: Texterkennung mit Tesseract (läuft parallel, Fortschrittsbalken, abbrechbar), Schriftwahl
  Fraktur/Antiqua; das Fraktur-Modell `frak2021` (UB Mannheim) wird bei Bedarf geladen.
- Qualitätsampel nach dem Einlesen (Konfidenz, Wörterbuchquote, schwache Zeilenenden) mit Empfehlung Transkribus bzw.
  ScanTailor; Ampelpunkt in der Bibliothek; Werte je Seite in `qualitaet.json`.
- ScanTailor-Anbindung: PDF-Seiten als Bilder exportieren, ScanTailor starten, Ergebnisordner einlesen; »Programm zeigen …«.
- Hilfeseiten: PDF oder Bilder einlesen, Mit Transkribus arbeiten, Werkzeuge installieren (DE/EN).
- Bibliothek: Start ohne Argumente zeigt alle bekannten Bücher; Buchordner per Dialog öffnen. Mehrere Bücher und
  Browser-Tabs nebeneinander – jedes Buch hat seine eigene Adresse (`/buch/<id>`).
- Transkribus-Export (ZIP oder Ordner) per Knopfdruck importieren, Seitenbilder aus dem Export oder einem Bilderordner; JPG-Bilder.
- Hilfe im Programm (`F1`): `docs/de`, `docs/en` werden im Browser angezeigt.
- Oberfläche auf Deutsch und Englisch.
- Hinweis beim ersten, langsamen Laden eines Buchs; Spenden-Link »Kaffee spendieren« im Fuß der Bibliothek.
- Freies Wörterbuch für die Rechtschreibung von 1901 wird mitgeliefert (`dict/`); das Programm läuft ohne `--dic`.
- Wörterbuchwahl zusätzlich über `~/.fraktur-korrektor/config.json` (`"dic"`).
- `dict/zusatz.txt` (Abkürzungen gelten als richtig) und `dict/fallen.txt` („baß“ wird immer markiert).
- Zwischenspeicher für Wörterbuchprüfungen – schnellerer Start ab dem zweiten Mal.
- Tests (pytest) und CI für Windows, macOS, Linux; `pyproject.toml`; Lizenz GPL-3.0-or-later; ROADMAP.

### Geändert
- Der fest eingetragene Pfad zu einem Wörterbuch aus Adobe Photoshop ist entfernt.

## [0.5.0] – 2026-09-18

Stand vor Beginn der Veröffentlichungsarbeiten: Lesemodus, Korrekturmodus, Serienkorrektur (F9) mit Rücknahme,
Whitelist, Fußnotentrenner, Lesezeichen, Korrekturprotokoll, `--lan`, Werkzeuge für Transkribus-PAGE-XML.
