# Änderungen

Format nach [Keep a Changelog](https://keepachangelog.com/de/), Versionen nach [SemVer](https://semver.org/lang/de/).

## [Unveröffentlicht]

### Neu
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
