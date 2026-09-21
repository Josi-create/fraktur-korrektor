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
| Lesen | `Bild↓` `Bild↑`, `Pos1` `Ende` | Seite vor/zurück, Seitenanfang/-ende |
| Lesen | `G` | gehe zu Seite: oben erscheint eine Eingabezeile für die Seitenzahl |
| Lesen | `S` (oder `/`, `Strg`+`F`, am Mac auch `Cmd`+`F`) | im ganzen Buch suchen; `N` nächste, `Umschalt`+`N` vorige Fundstelle (siehe unten) |
| Lesen | `+` `−` `0` | Zoom des Seitenbildes |
| Lesen | `R` | Seite neu laden (nach Änderungen in einem anderen Editor) |
| Korrektur | `Enter` | übernehmen und weiterlesen (steht in derselben Zeile noch ein rotes Wort, kommt dieses zuerst) |
| Korrektur / Zeile bearbeiten | `F7` | Trennzeichen `¬` an der Schreibmarke einfügen |
| Korrektur / Zeile bearbeiten | `Umschalt`+`Enter` | Zeile an der Schreibmarke teilen (siehe unten) |
| Korrektur | `F8` | Wort ist richtig → Whitelist |
| Korrektur | `Tab` | nächstes rotes Wort, ohne zu ändern |
| Korrektur | `Esc` | zurück zum Lesen, ohne zu ändern |
| Lesen / Korrektur | `F9` | Serienkorrektur (siehe unten) |
| Lesen | `U` | letzte Serienkorrektur zurücknehmen |
| Lesen | `F` | Fußnoten beginnen mit der Lesezeile (siehe unten) |
| Lesen | `T` | Tabelle: aus getrennten Zeilen eine Tabelle machen bzw. wieder auflösen (siehe unten) |
| Lesen | `H` | Überschrift: Ebene 1 → 2 → 3 → keine (siehe unten) |
| Lesen | `V` | Lesezeile mit der nächsten Zeile verbinden |
| Lesen | `W` | Whitelist anzeigen |
| Lesen | `D` | Wörterbuch: welche Rechtschreibung gilt in diesem Buch (siehe unten) |
| Lesen | `Umschalt`+`↓` / `↑` | Zeilen für eine Notiz markieren (innerhalb der Seite); jede andere Taste hebt die Markierung auf |
| Lesen / Korrektur | `F4` oder Rechtsklick auf die Markierung | Notiz für Obsidian aus der markierten Passage, sonst aus der Lesezeile (siehe unten) |
| Lesen | `N` | Notizordner für dieses Buch festlegen |
| überall | `F1` | diese Hilfe |

## Suchen (S) und Gehe zu Seite (G)

`S` – oder die gewohnte Tastenkombination `Strg`+`F` (am Mac auch `Cmd`+`F`) – öffnet oben in der Kopfleiste eine Eingabezeile. Was Sie dort eintippen, sucht das Programm im ganzen Buch –
ohne Rücksicht auf Groß- und Kleinschreibung, ſ gilt als s, und ein Wort wird auch gefunden, wenn es am Zeilenende
getrennt ist. `Enter` springt zur ersten Fundstelle ab der Leseposition; sie ist im Text blau markiert und im
Seitenbild eingerahmt. Oben bleibt ein kleines Feld stehen mit dem Suchwort, der Zählung („3 / 17“) und zwei
Knöpfen: `N` geht zur nächsten Fundstelle, `Umschalt`+`N` zur vorigen, das × schließt die Suche. `Esc` verwirft
die Eingabe.

`G` fragt auf dieselbe Weise nach einer Seitenzahl. Gemeint ist die Seite der Datei (die Zahl in der Auswahl
oben), nicht die gedruckte Seitenzahl des Buchs.

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

## Zeilen teilen und verbinden

Manchmal übersieht die Texterkennung einen Zeilenwechsel – zwei Zeilen (oder zwei Tabellenzellen) stehen in einer – oder
sie macht einen zu viel.

- **Teilen:** Zeile bearbeiten (`F2` oder `Enter`), die Schreibmarke an die Stelle setzen und `Umschalt`+`Enter` drücken.
  Was Sie im Feld schon geändert haben, wird dabei mit übernommen.
- **Verbinden:** Im Lesemodus `V` – die Lesezeile wird mit der nächsten verbunden. Endet sie mit dem Trennzeichen `¬`,
  wird das getrennte Wort dabei zusammengezogen (`Zu¬` + `kunft` → `Zukunft`).

Das Programm teilt bzw. vereinigt dabei auch den **Bildausschnitt** der Zeile (beim Teilen anteilig an der Trennstelle).
So behält jede Textzeile ihre Stelle im Seitenbild – anders als beim Ändern der Zeilenzahl in einem fremden Editor.
Innerhalb einer Tabelle wird die Tabelle danach neu durchgezählt: Verrutschte Spalten stehen wieder richtig.

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

Jede Zeile bleibt dabei eine Zeile – eine Zelle je Zeile –, damit die Zuordnung zum Seitenbild erhalten bleibt. Diese
Steuerzeichen bekommen Sie im Programm nicht zu sehen: Rechts erscheint die fertige **Tabelle als Tabelle**, mit Rahmen und
Spalten, und auch im Eingabefeld steht nur der Inhalt der Zelle. Der Lesecursor wandert Zelle für Zelle, links ist die
zugehörige Stelle im Seitenbild markiert. Die Wortprüfung übergeht die Auszeichnung. Den Inhalt der Zellen korrigieren Sie
wie jeden anderen Text (überflüssige Striche wie in `1812-` mit `F2` löschen).

**Verrutschte Spalten:** Stehen zwei Zellen in einer Zeile (`1812- 12 409`), weil die Texterkennung den Zeilenwechsel
übersehen hat, rutschen ab dort alle Spalten um eins weiter. Teilen Sie die Zeile an der Stelle (`F2`, Schreibmarke setzen,
`Umschalt`+`Enter`) – vor oder nach dem Anlegen der Tabelle; eine vorhandene Tabelle zählt das Programm danach neu durch.

Grenze: Die Zellen müssen in Lesereihenfolge stehen (Reihe für Reihe). Hat die Texterkennung eine Tabelle spaltenweise
gelesen, lässt sie sich so nicht auszeichnen.

## Überschriften (H)

`H` zeichnet die Lesezeile als Überschrift aus: beim ersten Mal Ebene 1 (`<h1>…</h1>`), bei jedem weiteren Druck die
nächste Ebene, nach Ebene 3 wieder gewöhnlicher Text. Überschriften erscheinen größer und fett, ohne sichtbare Steuerzeichen. Ein späterer EPUB-Export
kann daraus Kapitel und Inhaltsverzeichnis bilden.

Wer mag, kann mit `F2` auch weitere Auszeichnung von Hand eintragen; das Programm kennt `<em>`, `<strong>`, `<i>`, `<b>`,
`<sup>`, `<sub>`, `<p>`, `<blockquote>` und `<br/>`, behandelt sie nicht als Wörter und stellt Schrift-Auszeichnung
(kursiv, fett, hoch- und tiefgestellt) auch so dar.

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

## Notizen für Obsidian (F4)

Wer beim Lesen exzerpiert, kann jede Stelle als Zettel in [Obsidian](https://obsidian.md) ablegen – nach dem Vorbild von
Niklas Luhmanns Zettelkasten: ein Gedanke je Zettel, jeder mit Quellenangabe.

1. Einmal je Buch: `O` drücken (oder „Notizen“ in der Kopfleiste) und den Ordner im Obsidian-Vault angeben, in den die
   Zettel zu diesem Buch gehören, etwa `…/Vault/Katharinenfeld/Recherche/Leibbrandt 1928`. Der Knopf „Ordner wählen …“
   öffnet den Dateidialog; ein noch fehlender letzter Ordner wird angelegt. Die Wahl steht in `buch.json`.
2. Beim Lesen eine Passage mit der Maus markieren – auch über mehrere Zeilen – und `F4` drücken oder mit der rechten
   Maustaste auf die Markierung klicken. Ganz ohne Maus: zur ersten Zeile gehen, `Umschalt` halten und mit `↓` oder `↑`
   die gewünschten Zeilen markieren (blau hinterlegt), dann `F4`. Ohne Markierung wird die Lesezeile zum Zettel.

Das Programm legt im Ordner eine Datei an, fortlaufend nummeriert, zum Beispiel `07 Seite 57.md`:

    **Anmerkung**



    ---

    > Die Kolonisten zogen nach Rußland und der Weg war weit.

    Seite 57, [[0 Quellenangabe|Leibbrandt 1928]]

Oben Platz für die eigene Anmerkung, unter dem Strich das Zitat (am Zeilenende getrennte Wörter sind zusammengezogen) und die
Seite – die gedruckte Seitenzahl aus der Kopfzeile, sonst die PDF-Seite – und der Verweis auf die Quellenangabe des Buchs.
Diese Datei `0 Quellenangabe.md` legt das Programm beim ersten Zettel als Vorlage an; tragen Sie dort ein, woher das Buch
stammt (Universitätsbibliothek, Fernleihe …) und die Zitierweise, wie Zotero sie liefert. So hat jeder Zettel per Klick
seine vollständige Quelle. Das Zitat liegt außerdem in der Zwischenablage.

Ist Obsidian installiert, öffnet es den neuen Zettel sofort und kommt unter Windows in den Vordergrund (der Ordner muss in einem Vault liegen, den Obsidian kennt).
Ohne Obsidian bleibt die Datei einfach im Ordner – es ist gewöhnliches Markdown.

## Über das Heimnetz mitlesen

Wird das Programm mit der Option `--lan` gestartet, ist es auch von anderen Geräten im selben Netz
erreichbar (die Adresse steht beim Start im Fenster). Es gibt keinen Passwortschutz – nur im eigenen
Heimnetz verwenden. Bücher hinzufügen kann man nur an dem Rechner, auf dem das Programm läuft.
