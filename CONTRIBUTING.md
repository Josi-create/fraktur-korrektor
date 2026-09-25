# Mitarbeit am Fraktur-Korrektor

*English version: [CONTRIBUTING.en.md](CONTRIBUTING.en.md)*

Danke, dass Sie mithelfen wollen. Der Fraktur-Korrektor ist ein kleines Programm mit einem klaren Ziel: OCR-Text
gescannter Bücher lesen und dabei korrigieren – links das Seitenbild, rechts der Text, alles mit der Tastatur. Es
läuft lokal, nichts geht ins Internet. Die Menschen, für die es gebaut wird, sind Historikerinnen, Bibliothekare,
Familienforscher – Leute, die ein Buch lesen wollen und keine Kommandozeile. Daran messen wir jede Änderung: keine
Fachwörter in der Oberfläche, verständliche Fehlermeldungen mit einem nächsten Schritt, eine klare Empfehlung statt
einer Auswahl ohne Rat.

## Helfen ohne zu programmieren

Vieles, was das Programm besser macht, braucht keinen Code:

- **Probelesen mit echten Büchern.** Öffnen Sie ein eigenes Buch (PDF, Transkribus-Export, EPUB, Bilderordner) und
  berichten Sie, wo es hakt: eine Meldung, die Sie nicht verstanden haben, ein Knopf, den Sie gesucht haben, ein
  Wort, das fälschlich rot war. Solche Berichte sind die wertvollsten – schreiben Sie ein [Issue](../../issues/new/choose).
- **Wörterbücher.** `dict/zusatz.txt` enthält Wörter und Abkürzungen, die als richtig gelten sollen (wissenschaftlicher
  Apparat, Bibelstellen, Siglen); `dict/fallen.txt` Wörter, die zwar im Wörterbuch stehen, aber fast immer ein
  Lesefehler sind („baß“ für „daß“). Beide sind einfache Textdateien, ein Wort je Zeile. Vorschläge bitte mit einem
  Beispiel, wo das Wort vorkam.
- **Hilfetexte.** Die Hilfe liegt als Markdown in `docs/de` und `docs/en` und wird im Programm unter `F1` gezeigt. Wenn
  eine Erklärung unklar ist oder eine Frage fehlt, die Sie sich gestellt haben: verbessern oder ergänzen Sie sie. Jede
  Seite gibt es in beiden Sprachen unter demselben Dateinamen; wer nur eine Sprache schreiben kann, schreibt die eine
  und vermerkt es im Pull Request.
- **Übersetzung.** Alle Texte der Oberfläche stehen in `i18n.js`, deutsch und englisch nebeneinander. Bessere
  Formulierungen sind willkommen, besonders im Englischen.

## Fehler melden und Vorschläge machen

Bitte über die [Issue-Vorlagen](../../issues/new/choose): Fehlerbericht oder Vorschlag. Beim Fehler helfen
Betriebssystem, Programmversion (steht unten in der Bibliothek), der Weg, auf dem das Buch ins Programm kam, und der
genaue Wortlaut der Meldung. **Laden Sie keine Seitenbilder oder Texte aus Ihren Büchern hoch**, es sei denn, sie sind
gemeinfrei – das Urheberrecht gilt auch für Scans. Ein Ausschnitt in eigenen Worten reicht meist.

Was das Programm nicht kann und nicht können soll, steht in der [ROADMAP](ROADMAP.md): Es ersetzt keine
Texterkennung, sondern hilft beim Lesen und Korrigieren dessen, was Tesseract oder Transkribus geliefert haben.

## Einrichtung für Entwickler

Voraussetzungen: Python 3.10 oder neuer, Git. Tesseract ist nur nötig, um PDF und Bilder selbst einzulesen; die
Tests laufen ohne (in der CI läuft der Durchlauf mit echtem Tesseract nur unter Linux).

    git clone https://github.com/Josi-create/fraktur-korrektor.git
    cd fraktur-korrektor
    pip install -e .[dev]
    pytest
    python server.py

Auf dem Mac nimmt `./mac_lesen.sh` das Anlegen der `.venv` und den Start ab; `./mac_lesen.sh test` lässt die Tests
laufen. Wie die Installer entstehen, steht in [RELEASE.md](RELEASE.md).

### Start aus dem Quelltext

    python server.py                  Bibliothek; »Öffnen …« erkennt selbst: Buchordner, PDF, EPUB (+ gleichnamiges PDF), Bilder, Transkribus-Export
    python server.py <buchordner>     direkt ein Buch öffnen

Optionen: `--port 8765`, `--dic <hunspell-pfad-ohne-endung>`, `--title "…"`, `--no-browser`, `--lan`,
`--last` (ohne Buchordner: im Browser gleich das zuletzt gelesene Buch statt der Bibliothek).

Mit `--lan` ist das Programm auch von anderen Rechnern im lokalen Netz erreichbar (die Adresse wird beim Start angezeigt;
Windows fragt beim ersten Mal nach der Firewall-Freigabe für „Private Netzwerke“). Es gibt keinen Passwortschutz – nur
im eigenen Heimnetz verwenden.

Wörterbücher: Mitgeliefert werden freie Hunspell-Wörterbücher für die deutsche Rechtschreibung von 1901 und für die neue
(siehe [dict/](dict/README.md)); welche Rechtschreibung gilt, wird je Buch gewählt (Taste `D`, Vorschlag nach
Erscheinungsjahr). Ein anderes Wörterbuch für die Rechtschreibung von 1901 lässt sich per `--dic`, Umgebungsvariable
`FRAKTUR_DIC` oder `"dic"` in `~/.fraktur-korrektor/config.json` wählen. Der erste Start mit einem neuen Buch dauert
etwas länger, danach sind die Prüfergebnisse zwischengespeichert.

### Eigene Testumgebung – nie gegen echte Bücher

Das Programm schreibt in Buchordner (Textdateien, Protokoll, Lesezeichen) und in `~/.fraktur-korrektor`
(Einstellungen, Zwischenspeicher). Zum Ausprobieren deshalb immer:

- eine **eigene Instanz auf einem anderen Port** (`--port 8899`), nicht die, in der Sie gerade lesen;
- `FRAKTUR_HOME` auf einen **Wegwerfordner**, damit Einstellungen und Bibliothek des Alltags unberührt bleiben;
- eine **Kopie** eines Buchordners oder das Wegwerf-Buch aus `tests/conftest.py`, nie das Buch, an dem Sie arbeiten.

`tests/conftest.py` zeigt das Muster: Es baut ein kleines Buch im Temp-Ordner, sucht sich einen freien Port und startet
dafür einen eigenen Server.

Was pytest nicht sieht, fällt erst im Browser auf – JavaScript-Fehler zum Beispiel. Zum Nachstellen gibt es
Selbsttest-Einstiege: `/buch/<id>?notrans&keys=Space,F2,caret=6,Shift+Enter` spielt Tasten ab,
`/bibliothek#auto=<pfad>` liest eine Datei mit der empfohlenen Einstellung gleich ein, `#open=<pfad>` öffnet den
Dialog. Was sich gar nicht automatisch prüfen lässt (Dateidialog, ScanTailor-Start, Doppelklick auf die App), im
Pull Request ausdrücklich nennen, damit es jemand von Hand ausprobiert.

## Aufbau

| Datei | Aufgabe |
|---|---|
| `server.py` | HTTP-Server (nur Standardbibliothek), Klasse `Book`, Bibliothek, Hintergrundaufträge, Hilfe-Rendering |
| `korrlib.py` | Wörterbücher (`Checker`, Hunspell über spylls, Zwischenspeicher), Rechtschreibung je Epoche, Tokenisierung, Auszeichnung (`make_table`, `heading`, `mask`) |
| `finder.py` | erkennt, was eine Datei/ein Ordner enthält (Buch, PDF, EPUB, Bilder, Transkribus-Export) und empfiehlt |
| `ocr.py` | PDF/Bilder → Tesseract oder vorhandene Textebene; Qualitätsampel; ScanTailor finden/starten |
| `scans.py` | Scans vorbereiten: Doppelseiten teilen, schiefe Seiten geraderichten |
| `epub.py` | EPUB lesen; Textbuch; EPUB-Wortlaut auf die Zeilen eines PDF legen (`transplant`) |
| `pagexml.py` | Transkribus-PAGE-XML, hOCR, ALTO → Buchordner; `classify` (Kopfzeile, Fußnoten), Spaltenerkennung |
| `pdfbuch.py` | Buch als PDF sichern (Bilder, unsichtbare Textebene, Arbeitsstand als Anhang) und daraus wieder einlesen |
| `merge.py` | zwei Arbeitsstände desselben Buchs zusammenführen |
| `starter.py` | Start als fertiges Programm (Symbol im Dock bzw. Infobereich) |
| `reader.html`, `bibliothek.html`, `i18n.js` | Oberfläche; alle Texte zweisprachig in `i18n.js` (`t('schluessel')`) |
| `docs/de`, `docs/en` | Hilfe: dieselben Dateinamen in beiden Sprachen, im Programm unter `/hilfe/<sprache>/<seite>` |
| `dict/` | mitgelieferte Wörterbücher (GPL) samt Lizenztexten, `zusatz.txt`, `fallen.txt` |
| `tests/` | pytest; jeder Test bekommt ein Wegwerf-Buch und einen eigenen Server |
| `tools/` | ältere Kommandozeilenwerkzeuge (autokorr, build_text …) |

Ein **Buchordner** enthält `NNN.txt` (eine Datei je Seite: optional `# Kopfzeile`, Haupttext, `---`, Fußnoten),
`lines.json` (Zeilengeometrie), `img/NNN.jpg|png`, dazu `whitelist.txt`, `lesezeichen.json`, `korrekturen.log`,
`buch.json` (Kennung, Erscheinungsjahr, geltende Rechtschreibung) und `qualitaet.json`. Einstellungen liegen in
`~/.fraktur-korrektor` (überschreibbar mit `FRAKTUR_HOME`), neue Bücher in `~/Fraktur-Korrektor`. Optional liegt dort
`autokorr.log`, das Protokoll automatischer Ersetzungen (unsichere zeigt der Reader orange). Die Textdateien dürfen
parallel in einem Editor bearbeitet werden – die Zeilenzahl einer Seite dabei nicht ändern, sonst fehlt die
Bildzuordnung.

### Kommandozeilenwerkzeuge

Die Importwege lassen sich auch ohne Oberfläche aufrufen: `python ocr.py <pdf-oder-bilderordner> <buchordner>`
(Tesseract bzw. vorhandene Textebene), `python scans.py <pdf-oder-bilderordner> [<zielordner>]` (Doppelseiten teilen,
geraderichten). In `tools/` liegen ältere Werkzeuge aus der Zeit vor der Bibliothek und der Bau der Website:

- `page2txt.py` – Text aus Transkribus-PAGE-XML
- `build_text.py` – PAGE-XML → `NNN.txt` + `lines.json`, trennt Fußnoten (Grundlinienabstand, „N)“-Anfang); dasselbe
  macht der Import in der Bibliothek (`pagexml.py`)
- `autokorr.py` – typische Fraktur-Verwechslungen (l/t/k/f, b/d, B/W/V, s/f, u/n …) gegen Wörterbuch und
  Korpusfrequenz korrigieren
- `ocr_quality.py` – Qualitätsmaß je Seite (Hapax-Quote der Zeilenendwörter)
- `build_site.py` – die Hilfe als Website (`site/`), wie sie der Workflow für GitHub Pages baut

## Was nicht brechen darf

Diese Regeln sind kein Stil, sondern tragende Wände. Ein Pull Request, der eine davon verletzt, wird nicht angenommen,
auch wenn er sonst gut ist.

1. **Zeilenzahl = Bildzuordnung.** Die Textzeilen einer Seite werden der Reihe nach den Zeilen in `lines.json`
   zugeordnet (`Book.geo_seq`). Wer die Zahl der Zeilen ändert, muss `lines.json` mitführen – so machen es
   `split_line` und `join_lines`. Deshalb ist auch Auszeichnung zeilenweise: eine Tabellenzelle ist eine Zeile.
2. **Auszeichnung ist XHTML wie im EPUB** (`<table><tr><td>`, `<h2>`, `<em>` …), kein eigenes Format. Die Wortprüfung
   übergeht sie (`korrlib.mask`), Zeichenpositionen gelten immer für die echte Zeile. Im Reader wird sie dargestellt,
   nicht gezeigt.
3. **Jede Änderung prüft, ob die Zeile noch so aussieht wie im Browser** (`old` mitschicken, sonst 409): Die
   Textdateien dürfen parallel in einem Editor bearbeitet werden. Jede Änderung landet in `korrekturen.log`.
4. **Nie überschreiben.** Importe legen bei Namensgleichheit „(2)“ an; verworfen wird nur, was das Programm selbst
   angelegt hat und worin noch keine Arbeit steckt (`discard`). Was ersetzt wird, wird vorher als `vorher-<Datum>.zip`
   gesichert.
5. **Bibliothek verändern nur lokal.** Öffnen, Einlesen, Dateidialog – alles, was Dateien außerhalb des Buchs liest
   oder schreibt – ist für Anfragen aus dem LAN gesperrt (`H.local`). Neue Endpunkte dieser Art gehören hinter
   dieselbe Sperre.
6. **`main` ist immer benutzbar** und die Dateiformate bleiben abwärtskompatibel: Vorhandene Buchordner müssen mit
   jeder neuen Version weiter funktionieren, `python server.py <buchordner> --lan` auch.
7. **Nichts geht ins Internet.** Das Programm lädt nichts nach und schickt nichts weg – auch keine Wörter zur
   Prüfung. Die einzige Ausnahme ist das Nachladen des Fraktur-Modells für Tesseract auf ausdrücklichen Wunsch.
8. **Jedes Buch hat seine eigene Adresse** `/buch/<id>/…`, damit mehrere Bücher und Tabs nebeneinander gehen.

## Stil

- **Code wie der vorhandene:** knapp, deutsche Bezeichner und Kommentare, die das *Warum* erklären – nicht das Was.
  Keine neuen Abhängigkeiten ohne guten Grund; der Server kommt mit der Standardbibliothek aus.
- `server.py`, `reader.html` und `README.md` haben **CRLF-Zeilenenden** – beibehalten, sonst wird der Diff unlesbar.
- In `reader.html` und `bibliothek.html` **keine lokale Variable `t`** anlegen: Sie würde die Übersetzungsfunktion
  `t()` verdecken (ein Test prüft das).
- **Jeder Oberflächentext kommt deutsch und englisch** nach `i18n.js`; jede Hilfeseite in beide Sprachordner unter
  demselben Namen. Tests prüfen die Vollständigkeit.
- **Fehlermeldungen nennen den nächsten Schritt** und keine Fachwörter. Der Nutzer muss nicht wissen, was ein
  „Transkribus-Export“ ist – das Programm erkennt es.
- **Externe Fakten nachprüfen** (Download-Adressen, Paketnamen, Abläufe bei Apple) statt aus dem Gedächtnis schreiben,
  und mit Stand-Datum versehen, wo sie veralten können.
- **Buchdaten, Scans und Texte gehören nicht ins Repository** – auch nicht als Testdaten (Urheberrecht). Die Tests
  bauen sich ihr Buch selbst.
- **Neue Logik bekommt Tests**; `pytest` muss auf Windows, macOS und Linux grün bleiben (die CI prüft alle drei).
- Jede sichtbare Änderung bekommt einen Eintrag in [CHANGELOG.md](CHANGELOG.md) unter *Unveröffentlicht*.

## Pull Requests

1. Vorher kurz ein Issue anlegen oder in einem bestehenden sagen, dass Sie es angehen – das erspart doppelte Arbeit,
   besonders bei Änderungen an der Oberfläche.
2. Fork und Branch, kleine, abgeschlossene Änderungen. Commit-Nachrichten auf Deutsch, in der Form „Was ändert sich
   und warum“, mit `Closes #…`, wenn ein Issue erledigt wird.
3. Die [Checkliste in der Pull-Request-Vorlage](.github/PULL_REQUEST_TEMPLATE.md) abhaken: Tests grün, beide
   Sprachen, Changelog, keine Buchdaten.
4. Mit dem Beitrag stimmen Sie zu, dass er unter [GPL-3.0-or-later](LICENSE) veröffentlicht wird (Hilfetexte unter
   CC BY-SA 4.0).

Für alle gilt der [Verhaltenskodex](CODE_OF_CONDUCT.md). Fragen sind willkommen – am besten in den [Discussions](https://github.com/Josi-create/fraktur-korrektor/discussions), im Zweifel einfach ein Issue.
