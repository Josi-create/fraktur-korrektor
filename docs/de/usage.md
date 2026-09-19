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
| Lesen | `T` | Tabelle: aus getrennten Zeilen eine Tabelle machen bzw. wieder auflösen (siehe unten) |
| Lesen | `H` | Überschrift: Ebene 1 → 2 → 3 → keine (siehe unten) |
| Lesen | `W` | Whitelist anzeigen |
| Lesen | `D` | Wörterbuch: welche Rechtschreibung gilt in diesem Buch (siehe unten) |
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

## Tabellen (T)

Eine Texterkennung zerreißt Tabellen meist in einzelne Zeilen – aus einer Aufstellung wird

    im Jahre 1811
    16 842 Eimer,
    1812-
    12 409

Stellen Sie die Lesezeile auf die erste Zeile und drücken Sie `T`. Mit `↓` ziehen Sie den Bereich bis zur letzten Zeile
der Tabelle, mit `2` … `9` wählen Sie die Zahl der Spalten; die Vorschau oben zeigt sofort, wie sich die Zeilen auf Reihen
und Spalten verteilen (der Reihe nach, von links nach rechts). `H` macht die erste Reihe zu Spaltenköpfen, `Enter`
übernimmt, `Esc` bricht ab. `T` auf einer vorhandenen Tabelle nimmt die Auszeichnung wieder weg – der Text bleibt.

Das Programm erfindet dafür kein eigenes Format, sondern schreibt dieselbe Auszeichnung in den Text, die auch ein EPUB
benutzt (XHTML):

    <table><tr><td>im Jahre 1811</td>
    <td>16 842 Eimer,</td></tr>
    <tr><td>1812-</td>
    <td>12 409</td></tr></table>

Jede Zeile bleibt dabei eine Zeile – eine Zelle je Zeile –, damit die Zuordnung zum Seitenbild erhalten bleibt. Die
Auszeichnung erscheint im Text klein und blass, die Tabelle mit blauem Rand; die Wortprüfung übergeht sie. Den Inhalt der
Zellen korrigieren Sie wie jeden anderen Text (überflüssige Striche wie in `1812-` mit `F2` löschen).

Grenzen: Die Zellen müssen in Lesereihenfolge stehen (Reihe für Reihe). Hat die Texterkennung eine Tabelle spaltenweise
gelesen oder zwei Zellen in eine Zeile gesetzt, hilft `F2`: Dort lässt sich die Auszeichnung von Hand ergänzen, zum Beispiel
`</td><td>` zwischen zwei Zellen derselben Zeile.

## Überschriften (H)

`H` zeichnet die Lesezeile als Überschrift aus: beim ersten Mal Ebene 1 (`<h1>…</h1>`), bei jedem weiteren Druck die
nächste Ebene, nach Ebene 3 wieder gewöhnlicher Text. Überschriften erscheinen größer und fett. Ein späterer EPUB-Export
kann daraus Kapitel und Inhaltsverzeichnis bilden.

Wer mag, kann mit `F2` auch weitere Auszeichnung von Hand eintragen; das Programm kennt `<em>`, `<strong>`, `<i>`, `<b>`,
`<sup>`, `<sub>`, `<p>`, `<blockquote>` und `<br/>` und behandelt sie nicht als Wörter.

## Whitelist (W)

Die Whitelist enthält die Wörter, die Sie mit `F8` bestätigt haben (Namen, Orte, alte Schreibungen). `W`
zeigt sie, die neuesten zuerst, mit Filter. `Entf`, `Leertaste` oder ein Klick nimmt ein Wort heraus bzw.
wieder auf – es wird dann im Buch wieder rot.

## Wörterbuch (D)

Rot wird, was das Wörterbuch nicht kennt – deshalb muss das Wörterbuch zum Buch passen. `D` (oder „Wörterbuch“ in der
Kopfleiste) zeigt drei Häkchen; die Wahl gilt nur für dieses Buch und wird gespeichert:

| Häkchen | Beispiele | Wofür |
|---|---|---|
| Schreibungen vor 1901 gelten lassen | Thür, Noth, seyn, giebt, civilisiren | Drucke des 19. Jahrhunderts – und neuere Arbeiten, die alte Quellen wörtlich zitieren |
| Rechtschreibung 1901 bis 1996 | daß, Schiffahrt, rauh | die meisten Frakturdrucke, alles bis zur Rechtschreibreform |
| Neue Rechtschreibung (ab 1996) | dass, Schifffahrt, rau | neuere Bücher, Skripte, Aufsätze |

Beim Einlesen schätzt das Programm das **Erscheinungsjahr** aus Titelei und Impressum und setzt die Häkchen passend:
vor 1902 die ersten beiden, bis 1997 das mittlere, ab 1998 die unteren beiden (die Umstellung zog sich hin, und neuere
Arbeiten zitieren ältere Texte). Das Fenster zeigt nach jeder Änderung, wie viele rote Wörter es vorher und nachher im Buch
gibt – so sehen Sie sofort, was passt. Echte Lesefehler (`ber`, `bie`, `Bolk`) bleiben in jeder Einstellung rot.

Unabhängig davon gelten immer: gängige Abkürzungen (Vgl, Bd, Ebd, Hg, Bibelstellen wie Offb, Joh), Siglen in
Großbuchstaben, die mehrfach vorkommen (BWKG, LKA), und längere Wörter, die im Buch mindestens dreimal stehen (meist
Namen). Einen Namen, der trotzdem rot ist, bestätigen Sie einmal mit `F8` – das gilt dann für alle Fundstellen.

## Über das Heimnetz mitlesen

Wird das Programm mit der Option `--lan` gestartet, ist es auch von anderen Geräten im selben Netz
erreichbar (die Adresse steht beim Start im Fenster). Es gibt keinen Passwortschutz – nur im eigenen
Heimnetz verwenden. Bücher hinzufügen kann man nur an dem Rechner, auf dem das Programm läuft.
