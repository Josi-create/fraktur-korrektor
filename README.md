# Fraktur-Korrektor

Lesen und Korrekturlesen in einem: ein kleiner lokaler „E-Book-Reader“ für OCR-Text gescannter
(Fraktur-)Bücher. Links das Seitenbild, rechts der erkannte Text. Ein Lesecursor (aktuelle Zeile,
immer in der Mitte) hält Bild und Text synchron. Fragliche Wörter (nicht im Wörterbuch, unsichere
automatische Ersetzungen) sind rot markiert. Alles ist mit der Tastatur bedienbar.

Ziel ist ein sauberer Text als Grundlage für ein Epub.

## Bedienung

| Modus | Taste | Wirkung |
|---|---|---|
| Lesen | `↓` `↑` (oder `j` `k`) | nächste / vorige Zeile (läuft über Seitengrenzen) |
| Lesen | `Leertaste` | zum nächsten roten Wort → Korrekturmodus |
| Lesen | `Enter` oder `F2` | aktuelle Zeile frei bearbeiten (Satzzeichen, Fußnotenzeichen, alles, was die Automatik nicht bemerkt) |
| Lesen | `Bild↓` `Bild↑`, `Pos1` `Ende`, `G` | Seite vor/zurück, Seitenanfang/-ende, gehe zu Seite |
| Lesen | `+` `−` `0` | Zoom des Seitenbildes |
| Lesen | `R` | Seite neu laden (nach Änderungen in einem anderen Editor) |
| Korrektur | `Enter` | übernehmen und weiterlesen (steht in derselben Zeile noch ein rotes Wort, kommt dieses zuerst) |
| Korrektur | `F8` | Wort ist richtig → `whitelist.txt` |
| Korrektur | `Tab` | nächstes rotes Wort, ohne zu ändern |
| Korrektur | `Esc` | zurück zum Lesen, ohne zu ändern |

Bei Wörtern mit Zeilentrennung (`Zu¬` / `kunft`) erscheinen beide Zeilen als Eingabefelder.
Die Leseposition wird in `lesezeichen.json` gespeichert. Jede Korrektur wird sofort in die
Textdatei geschrieben; die Dateien dürfen parallel in einem Editor bearbeitet werden
(die Zeilenzahl einer Seite dabei nicht ändern, sonst fehlt die Bildzuordnung).

## Start

    pip install spylls
    py server.py <buchordner> [--port 8765] [--dic <hunspell-pfad-ohne-endung>] [--title "…"]

Wörterbuch: ein Hunspell-Wörterbuch (`.dic`/`.aff`), für alte Drucke am besten deutsche Rechtschreibung
von 1901. Pfad per `--dic` oder Umgebungsvariable `FRAKTUR_DIC`.

## Buchordner

    NNN.txt        eine Datei je Seite: optional "# Kopfzeile", Haupttext, "---", Fußnoten
    lines.json     Zeilengeometrie je Seite (aus PAGE-XML, siehe tools/build_text.py)
    img/NNN.png    Seitenbilder
    autokorr.log   optional: Protokoll der automatischen Ersetzungen (unsichere werden orange markiert)
    whitelist.txt  bestätigte Wörter
    lesezeichen.json

Buchdaten gehören **nicht** in dieses Repository.

## Werkzeuge (tools/)

- `page2txt.py` – Text aus Transkribus-PAGE-XML
- `build_text.py` – PAGE-XML → `NNN.txt` + `lines.json`, trennt Fußnoten (Grundlinienabstand, „N)“-Anfang)
- `autokorr.py` – typische Fraktur-Verwechslungen (l/t/k/f, b/d, B/W/V, s/f, u/n …) gegen Wörterbuch und Korpusfrequenz korrigieren
- `ocr_quality.py` – Qualitätsmaß je Seite (Hapax-Quote der Zeilenendwörter)

## Geplant

- Dateimanager / Bibliothek für mehrere Bücher
- Zeilen teilen/verbinden mit Erhalt der Bildzuordnung
- Epub-Export (Kapitel, Fußnoten)
