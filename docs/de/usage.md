# Bedienung

Links das Seitenbild, rechts der Text. Die gelb hinterlegte **Lesezeile** steht immer auf derselben Höhe;
Bild und Text wandern gemeinsam. Rot markiert sind Wörter, die das Wörterbuch nicht kennt; orange sind
Stellen, die eine automatische Vorkorrektur unsicher ersetzt hat.

Das Programm kennt drei Zustände, oben in der Leiste angezeigt: **Lesen** (grün), **Korrektur** (rot) –
ein rotes Wort wird geändert – und **Zeile bearbeiten** (orange).

## Tasten

| Modus | Taste | Wirkung |
|---|---|---|
| Lesen | `↓` `↑` (oder `j` `k`), Mausrad | nächste / vorige Zeile; der Text läuft fließend über Seitengrenzen. Ein Klick auf eine Zeile macht sie zur Lesezeile |
| Lesen | `Leertaste` | zum nächsten roten Wort → Korrektur |
| Lesen | Doppelklick auf ein Wort | Korrektur dieser Zeile, das angeklickte Wort ist markiert |
| Lesen | `F8` | erstes rotes Wort der Lesezeile ist richtig → Whitelist. Nochmal `F8` = nächstes. Ohne rotes Wort in der Lesezeile: das nächste weiter unten auf der Seite |
| Lesen | `Enter` | steht in der Lesezeile ein rotes Wort: direkt dorthin; sonst wie `F2` |
| Lesen | `F2` | die Lesezeile frei bearbeiten (Satzzeichen, Fußnotenzeichen, alles, was die Automatik nicht bemerkt) |
| Lesen | `Bild↓` `Bild↑`, `Pos1` `Ende`, `G` | Seite vor/zurück, Seitenanfang/-ende, gehe zu Seite |
| Lesen | `+` `−` `0` | Zoom des Seitenbildes |
| Lesen | `R` | Seite neu laden (nach Änderungen in einem anderen Editor) |
| Korrektur | `Enter` | übernehmen und weiterlesen (steht in derselben Zeile noch ein rotes Wort, kommt dieses zuerst) |
| Korrektur / Zeile bearbeiten | `F7` | Trennzeichen `¬` an der Schreibmarke einfügen |
| Korrektur | `F8` | Wort ist richtig → Whitelist |
| Korrektur | `Tab` | nächstes rotes Wort, ohne zu ändern |
| Korrektur | `Esc` | zurück zum Lesen, ohne zu ändern |
| Lesen / Korrektur | `F9` | Serienkorrektur (siehe unten) |
| Lesen | `U` | letzte Serienkorrektur zurücknehmen |
| Lesen | `F` | Fußnoten beginnen mit der Lesezeile (siehe unten) |
| Lesen | `W` | Whitelist anzeigen |
| überall | `F1` | diese Hilfe |

## Getrennte Wörter

Am Zeilenende getrennte Wörter schreibt das Programm mit dem Trennzeichen `¬`: `Zu¬` / `kunft`. Beide
Teile werden zusammen geprüft. Bei der Korrektur erscheinen beide Zeilen als Eingabefelder. `F7` fügt das
Zeichen ein.

## Serienkorrektur (F9)

Derselbe Lesefehler kommt in einem Buch oft dutzendfach vor (`ber` statt „der“, `bie` statt „die“). Die
Serienkorrektur zeigt alle Fundstellen eines Wortes auf einmal und ersetzt sie nach einem kurzen Blick auf
die Bildausschnitte.

- Wer zum Beispiel `ber` → `der` korrigiert, sieht danach den Hinweis „‚ber‘ kommt noch 74× im Buch vor –
  F9 zeigt alle Stellen“.
- In der Korrektur nimmt `F9` das aktuelle rote Wort; die Ersetzung tippen Sie ein.
- Beim Lesen geben Sie beide Wörter frei ein.

Jede Fundstelle zeigt Seite und Zeile, den Bildausschnitt mit rotem Rahmen und den Text. Alle Stellen sind
vorab angehakt; auch über das Zeilenende getrennte Wörter werden gefunden.

| Taste | Wirkung |
|---|---|
| `↓` `↑` | durch die Liste wandern |
| `Leertaste` | Haken setzen / entfernen |
| `A` | alle an / alle aus |
| `Tab` | die Ersetzung ändern |
| `Enter` | alle angehakten Stellen ersetzen |
| `Esc` | abbrechen |

`U` im Lesemodus nimmt die letzte Serie zurück. Zeilen, die Sie seither von Hand geändert haben, bleiben
dabei unangetastet.

## Fußnoten (F)

Fußnoten stehen in der Textdatei unter einer Zeile `---` und laufen immer bis zum Seitenende. `F` setzt
oder verschiebt diesen Trenner vor die Lesezeile. Steht die Lesezeile auf der ersten Fußnotenzeile, nimmt
`F` den Trenner wieder weg.

## Whitelist (W)

Die Whitelist enthält die Wörter, die Sie mit `F8` bestätigt haben (Namen, Orte, alte Schreibungen). `W`
zeigt sie, die neuesten zuerst, mit Filter. `Entf`, `Leertaste` oder ein Klick nimmt ein Wort heraus bzw.
wieder auf – es wird dann im Buch wieder rot.

## Über das Heimnetz mitlesen

Wird das Programm mit der Option `--lan` gestartet, ist es auch von anderen Geräten im selben Netz
erreichbar (die Adresse steht beim Start im Fenster). Es gibt keinen Passwortschutz – nur im eigenen
Heimnetz verwenden. Bücher hinzufügen kann man nur an dem Rechner, auf dem das Programm läuft.
