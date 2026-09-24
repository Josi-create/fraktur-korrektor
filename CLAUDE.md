# Fraktur-Korrektor – Hinweise für Claude Code

Bitte auf Deutsch antworten und den Betreiber siezen.

## Worum es geht

Lokales Lese- und Korrekturprogramm für OCR-Text gescannter Bücher, vor allem Fraktur: links das Seitenbild, rechts der
Text, unbekannte Wörter rot, alles mit der Tastatur. Ein Python-Server (`server.py`) und der Browser als Fenster. Nichts
geht ins Internet.

**Zielgruppe** sind Historiker, Bibliothekare, Familienforscher ohne Technikkenntnisse – Leitbild: ein älterer
Geschichtsprofessor. Daran wird jede Entscheidung gemessen: kein Kommandozeilenzwang, keine Fachwörter in der Oberfläche
(der Nutzer muss nicht wissen, was ein „Transkribus-Export“ ist – das Programm erkennt es), verständliche Fehlermeldungen
mit einem nächsten Schritt, eine klare Empfehlung statt einer Auswahl ohne Rat.

Das Projekt wird Open Source (GPL-3.0-or-later), Mitarbeit erwünscht. Plan und Stand: [ROADMAP.md](ROADMAP.md),
[CHANGELOG.md](CHANGELOG.md), GitHub-Milestones M1–M7. Das Repository ist seit dem 24. September 2026 öffentlich; die CI (Tests, Installer, Website) läuft bei jedem Push.

## Aufbau

| Datei | Aufgabe |
|---|---|
| `server.py` | HTTP-Server (nur Standardbibliothek), Klasse `Book`, Bibliothek, Hintergrundaufträge, Hilfe-Rendering |
| `korrlib.py` | Wörterbücher (`Checker`, Hunspell über spylls, Zwischenspeicher), Rechtschreibung je Epoche, Tokenisierung, Auszeichnung (`make_table`, `heading`, `mask`) |
| `finder.py` | erkennt, was eine Datei/ein Ordner enthält (Buch, PDF, EPUB, Bilder, Transkribus-Export) und empfiehlt |
| `ocr.py` | PDF/Bilder → Tesseract oder vorhandene Textebene; Qualitätsampel; ScanTailor finden/starten |
| `epub.py` | EPUB lesen; Textbuch; EPUB-Wortlaut auf die Zeilen eines PDF legen (`transplant`) |
| `pagexml.py` | Transkribus-PAGE-XML → Buchordner; `classify` (Kopfzeile, Fußnoten) für alle Importwege |
| `pdfbuch.py` | Buch als PDF sichern (Bilder, unsichtbare Textebene, Arbeitsstand als Anhang) und daraus wieder einlesen |
| `reader.html`, `bibliothek.html`, `i18n.js` | Oberfläche; alle Texte zweisprachig in `i18n.js` (`t('schluessel')`) |
| `docs/de`, `docs/en` | Hilfe: dieselben Dateinamen in beiden Sprachen, im Programm unter `/hilfe/<sprache>/<seite>` |
| `dict/` | mitgelieferte Wörterbücher (GPL) samt Lizenztexten, `zusatz.txt`, `fallen.txt` |
| `tools/` | ältere Kommandozeilenwerkzeuge (autokorr, build_text …) |

Ein **Buchordner** enthält `NNN.txt` (eine Datei je Seite: optional `# Kopfzeile`, Haupttext, `---`, Fußnoten),
`lines.json` (Zeilengeometrie), `img/NNN.jpg|png`, dazu `whitelist.txt`, `lesezeichen.json`, `korrekturen.log`, `buch.json`
(Erscheinungsjahr, geltende Rechtschreibung), `qualitaet.json`. Einstellungen des Nutzers: `~/.fraktur-korrektor`
(überschreibbar mit `FRAKTUR_HOME`), neue Bücher: `~/Fraktur-Korrektor`.

## Was nicht brechen darf

- **Zeilenzahl = Bildzuordnung.** Die Textzeilen einer Seite werden der Reihe nach den Zeilen in `lines.json` zugeordnet
  (`Book.geo_seq`). Wer die Zahl der Zeilen ändert, muss `lines.json` mitführen – so machen es `split_line`/`join_lines`.
  Deshalb ist Auszeichnung zeilenweise: eine Tabellenzelle ist eine Zeile.
- **Auszeichnung ist XHTML wie im EPUB** (`<table><tr><td>`, `<h2>`, `<em>` …), nichts Eigenes. Die Wortprüfung übergeht sie
  (`korrlib.mask`), Zeichenpositionen gelten immer für die echte Zeile. Im Reader wird sie dargestellt, nicht gezeigt.
- **Jede Änderung prüft, ob die Zeile noch so aussieht wie im Browser** (`old` mitschicken, sonst 409): Textdateien dürfen
  parallel in einem Editor bearbeitet werden. Jede Änderung landet in `korrekturen.log`.
- **Nie überschreiben:** Importe legen bei Namensgleichheit „(2)“ an; verworfen wird nur, was das Programm selbst eingelesen
  hat und worin noch keine Arbeit steckt (`discard`).
- **Bibliothek verändern nur lokal:** Öffnen, Einlesen, Dateidialog sind für Anfragen aus dem LAN gesperrt (`H.local`).
- Jedes Buch hat seine eigene Adresse `/buch/<id>/…` – mehrere Bücher und Tabs nebeneinander.

## Arbeitsweise

- **`main` ist immer benutzbar.** Der Betreiber arbeitet täglich mit der neuesten Version an echten Büchern und ist der
  erste Betatester. `python server.py <buchordner> --lan` muss weiter funktionieren wie bisher; Formate abwärtskompatibel.
- **Tests und Probeläufe nie gegen echte Buchordner.** Eigene Instanz, eigener Port (nicht 8765), `FRAKTUR_HOME` auf einen
  Temp-Ordner; `tests/conftest.py` zeigt das Muster (Wegwerf-Buch, freier Port). Laufende Server des Betreibers nicht
  beenden, außer er bittet darum.
- **Buchdaten, Scans und Texte gehören nicht ins Repository** (Urheberrecht) – auch nicht als Testdaten.
- `pip install -e .[dev]` und `pytest` – muss grün bleiben, neue Logik bekommt Tests. Die CI läuft auf Windows, macOS und
  Linux; unter Linux mit echtem Tesseract.
- **Was pytest nicht sieht, im Browser ansehen:** JavaScript-Fehler fallen erst dort auf. Selbsttest-Einstiege:
  `/buch/<id>?notrans&keys=Space,F2,caret=6,Shift+Enter,…` spielt Tasten ab, `/bibliothek#auto=<pfad>` liest die Empfehlung
  gleich ein, `#open=<pfad>` öffnet den Dialog. Für Bildschirmfotos eignet sich Chrome headless; bei laufenden Aufträgen
  passt dessen künstliche Uhr nicht zu echten Netzabfragen (deshalb pollt `#auto` ohne Pause).
- **Was sich nicht automatisch prüfen lässt** (Dateidialog, ScanTailor-Start, Doppelklick, Gatekeeper), ausdrücklich
  benennen und den Betreiber bitten, es auszuprobieren.
- **Externe Fakten nachprüfen** (Download-Adressen, Homebrew-Namen, Preise, Apple-Abläufe) statt aus dem Gedächtnis
  schreiben – in der Doku waren solche Angaben schon falsch. Mit Stand-Datum versehen, wo sie veralten.
- **Code wie der vorhandene:** knapp, deutsche Kommentare, die das Warum erklären. `server.py`, `reader.html` und
  `README.md` haben CRLF-Zeilenenden – beibehalten, sonst wird der Diff unlesbar. In `reader.html`/`bibliothek.html` keine
  lokale Variable `t` anlegen: Sie würde die Übersetzungsfunktion `t()` verdecken (ein Test prüft das).
- Jeder neue Oberflächentext kommt deutsch **und** englisch nach `i18n.js`, jede Hilfeseite in beide Sprachordner (Tests
  prüfen die Vollständigkeit).
- Commits direkt auf `main` sind hier üblich, mit aussagekräftiger deutscher Nachricht und `Closes #…`.

## Verwandtes Projekt

`Josi-create/PDF_Sortier_Meister` (öffentlich) hat eine erprobte Release-Pipeline: PyInstaller, Inno Setup, macOS-DMGs für
arm64 und x86_64, Signatur/Notarisierung, mitgeliefertes Tesseract. Für M4 ist das die Vorlage – siehe Issue #18.
