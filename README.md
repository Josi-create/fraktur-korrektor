# Fraktur-Korrektor

Lesen und Korrekturlesen in einem: ein kleiner lokaler „E-Book-Reader“ für OCR-Text gescannter
(Fraktur-)Bücher. Links das Seitenbild, rechts der erkannte Text. Ein Lesecursor (aktuelle Zeile,
immer im oberen Viertel) hält Bild und Text synchron. Fragliche Wörter (nicht im Wörterbuch, unsichere
automatische Ersetzungen) sind rot markiert. Alles ist mit der Tastatur bedienbar.

Ziel ist ein sauberer Text als Grundlage für ein Epub.

## Bedienung

| Modus | Taste | Wirkung |
|---|---|---|
| Lesen | `↓` `↑` (oder `j` `k`) | nächste / vorige Zeile (läuft über Seitengrenzen) |
| Lesen | `Leertaste` | zum nächsten roten Wort → Korrekturmodus |
| Lesen | `F8` | erstes rotes Wort der Lesezeile ist richtig → `whitelist.txt` (nochmal `F8` = nächstes; ohne rotes Wort in der Lesezeile: das nächste weiter unten auf der Seite, die Lesezeile springt dorthin) |
| Lesen | `Enter` | steht in der Lesezeile ein rotes Wort: direkt dorthin (Korrekturmodus, Wort markiert); sonst wie `F2` |
| Lesen | `F2` | aktuelle Zeile frei bearbeiten (Satzzeichen, Fußnotenzeichen, alles, was die Automatik nicht bemerkt) |
| Lesen | `Bild↓` `Bild↑`, `Pos1` `Ende`, `G` | Seite vor/zurück, Seitenanfang/-ende, gehe zu Seite |
| Lesen | `+` `−` `0` | Zoom des Seitenbildes |
| Lesen | `R` | Seite neu laden (nach Änderungen in einem anderen Editor) |
| Korrektur | `Enter` | übernehmen und weiterlesen (steht in derselben Zeile noch ein rotes Wort, kommt dieses zuerst) |
| Korrektur | `F8` | Wort ist richtig → `whitelist.txt` |
| Korrektur | `Tab` | nächstes rotes Wort, ohne zu ändern |
| Korrektur | `Esc` | zurück zum Lesen, ohne zu ändern |
| Lesen/Korrektur | `F9` | Serienkorrektur: alle Fundstellen eines Wortes mit Scan-Ausschnitt; `Leertaste` Haken, `A` alle, `Enter` ersetzen, `Esc` abbrechen |
| Lesen | `U` | letzte Serienkorrektur zurücknehmen |
| Lesen | `W` | Whitelist anzeigen (neueste zuerst, Filter); `Entf`/`Leertaste`/Klick nimmt ein Wort heraus bzw. wieder auf |

Bei Wörtern mit Zeilentrennung (`Zu¬` / `kunft`) erscheinen beide Zeilen als Eingabefelder.
Die Leseposition wird in `lesezeichen.json` gespeichert. Jede Korrektur wird sofort in die
Textdatei geschrieben; die Dateien dürfen parallel in einem Editor bearbeitet werden
(die Zeilenzahl einer Seite dabei nicht ändern, sonst fehlt die Bildzuordnung).

## Serienkorrektur (F9)

Derselbe OCR-Fehler kommt in einem Buch oft dutzendfach vor (`ber` statt „der“, `bie` statt „die“).
Die Serienkorrektur zeigt alle Fundstellen eines Wortes auf einmal und ersetzt sie nach einem kurzen Blick auf die Scan-Ausschnitte.

**F9 nach einer Korrektur**
- Wer z. B. `ber` → `der` korrigiert, sieht unter dem Eingabefeld einen Hinweis in der Art „‚ber‘ kommt noch 74× im Buch vor – F9 zeigt alle Stellen“.
- Im Korrekturmodus nimmt F9 ohne vorherige Korrektur das aktuelle rote Wort; die Ersetzung wird eingetippt.
- Im Lesemodus werden beide Wörter frei eingegeben.

**Die Liste**
- Jede Fundstelle zeigt Seite und Zeile, den Scan-Ausschnitt mit rotem Rahmen und den Text.
- Alle Stellen sind vorab angehakt. Auch über das Zeilenende getrennte Wörter (`¬`) werden gefunden.

**Tasten in der Liste**
- `↓` `↑` wandern durch die Liste.
- `Leertaste` setzt oder entfernt den Haken, `A` schaltet alle an oder aus.
- `Tab` ändert die Ersetzung.
- `Enter` ersetzt alle angehakten Stellen, `Esc` bricht ab.

**Zurücknehmen:** `U` im Lesemodus nimmt die letzte Serie zurück. Zeilen, die seither von Hand geändert wurden, bleiben dabei unangetastet.

**Protokoll:** Jede Korrektur steht in `korrekturen.log` im Buchordner, egal ob einzeln, als Serie oder als Rücknahme
(Zeit, Art, Seite, Zeile, alte Zeile, neue Zeile). Die Datei gehört zusammen mit `lesezeichen.json` und `whitelist.txt` in jede Sicherung des Buchordners.

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
    korrekturen.log  Protokoll aller Korrekturen (Zeit, Art, Seite, Zeile, alt, neu)

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
