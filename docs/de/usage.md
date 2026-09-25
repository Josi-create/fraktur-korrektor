# Bedienung

Links das Seitenbild, rechts der Text. Die gelb hinterlegte **Lesezeile** steht immer auf derselben Höhe;
Bild und Text wandern gemeinsam. Rot markiert sind Wörter, die das Wörterbuch nicht kennt; orange sind
Stellen, die eine automatische Vorkorrektur unsicher ersetzt hat. Rot wird auch eine Seitenzahl, die nicht zu den
Nachbarseiten passt (die OCR liest in Fraktur gern „16“ als „46“) – der Hinweis nennt die Zahl, die dort stehen müsste,
und `Leertaste`, `Enter` berichtigen sie wie ein Wort. Die Seitenzahl darf oben in der Kopfzeile stehen oder unten auf
der Seite wie in neueren Büchern: Trägt ein Buch sie durchgehend unten, erkennt das Programm das von selbst und zeigt
sie dort blass wie die Kopfzeile. Ebenso den **Kolumnentitel** neuerer Bücher – oben auf jeder Seite der Buch- oder
Kapiteltitel mit der Seitenzahl (»Stalins Bauernopfer am Schwarzen Meer 9«), den die Texterkennung als gewöhnliche
Zeile gelesen hat: Er erscheint blass, wird nicht geprüft und gehört nicht zum Text; seine Zahl gilt als Seitenzahl.
Eintragen müssen Sie nichts, die Dateien bleiben, wie sie sind; fehlt die Zahl auf einer Seite (Kapitelanfang), ergibt
sie sich aus den Nachbarseiten.

Das Programm kennt drei Zustände, oben in der Leiste angezeigt: **Lesen** (grün), **Korrektur** (rot) –
ein rotes Wort wird geändert – und **Zeile bearbeiten** (orange).

## Tasten

| Modus | Taste | Wirkung |
|---|---|---|
| Lesen | `↓` `↑` (oder `j` `k`), Mausrad | nächste / vorige Zeile; der Text läuft fließend über Seitengrenzen. Ein Klick auf eine Zeile macht sie zur Lesezeile |
| Lesen | `Leertaste` | zum nächsten roten Wort → Korrektur |
| Lesen | Doppelklick auf ein Wort | Korrektur dieser Zeile, das angeklickte Wort ist markiert |
| Lesen | Doppelklick ins Seitenbild | die Zeile unter dem Mauszeiger wird Lesezeile, im Bild wie im Text – praktisch, wenn man im Bild eine Stelle sucht |
| Lesen | `F8` (oder `#`) | erstes rotes Wort der Lesezeile ist richtig → Whitelist. Nochmal `F8` = nächstes. Ohne rotes Wort in der Lesezeile: das nächste weiter unten auf der Seite |
| Lesen | `Enter` | steht in der Lesezeile ein rotes Wort: direkt dorthin; sonst wie `F2` |
| Lesen | `F2` | die Lesezeile frei bearbeiten (Satzzeichen, Fußnotenzeichen, alles, was die Automatik nicht bemerkt) |
| Lesen | `Bild↓` `Bild↑`, `Pos1` `Ende` | Seite vor/zurück, Seitenanfang/-ende |
| Lesen | `G` | gehe zu Seite: oben erscheint eine Eingabezeile für die Seitenzahl |
| Lesen | `S` (oder `/`, `Strg`+`F`, am Mac auch `Cmd`+`F`) | im ganzen Buch suchen; `N` nächste, `Umschalt`+`N` vorige Fundstelle (siehe unten) |
| Lesen | `+` `−` `0` | Zoom des Seitenbildes (auch `Strg`+Mausrad über dem Bild) |
| Lesen | `Strg`+`+` `Strg`+`−` `Strg`+`0` | Schriftgröße des Textes für dieses Buch (auch `Strg`+Mausrad über dem Text); bleibt gespeichert. Von selbst wählt das Programm sie so, dass eine gedruckte Zeile auch rechts in eine Zeile passt – `Strg`+`0` stellt das wieder ein |
| Lesen | `Umschalt`+Mausrad | eine breite Tabelle seitwärts rollen; mit der Lesezeile rollt sie von selbst |
| Lesen | `R` | Seite neu laden (nach Änderungen in einem anderen Editor) |
| Korrektur | `Enter` | übernehmen und weiterlesen (steht in derselben Zeile noch ein rotes Wort, kommt dieses zuerst) |
| Korrektur / Zeile bearbeiten | `F7` (oder `-` am Zeilenende) | Trennzeichen `¬` an der Schreibmarke einfügen. Mitten in der Zeile bleibt `-` ein Bindestrich; endet die Zeile schon mit `¬`, setzt `-` einen Bindestrich davor (`Ost-¬` / `Preußen`) |
| Korrektur / Zeile bearbeiten | `Umschalt`+`Enter` | Zeile an der Schreibmarke teilen (siehe unten) |
| Korrektur | `F8` (oder `#`) | Wort ist richtig → Whitelist |
| Korrektur | `↓` `↑` | einen Korrekturvorschlag ins Feld setzen (siehe unten); `Enter` übernimmt ihn |
| Korrektur | `Tab` | nächstes rotes Wort, ohne zu ändern; bei einem getrennten Wort zuerst in die zweite Hälfte |
| Korrektur | `Esc` | zurück zum Lesen, ohne zu ändern |
| Lesen / Korrektur | `F9` | Serienkorrektur (siehe unten) |
| Lesen | `U` | letzte Serienkorrektur zurücknehmen |
| Lesen | `F` | Fußnoten beginnen mit der Lesezeile (siehe unten) |
| Lesen | `T` | Tabelle: aus getrennten Zeilen eine Tabelle machen bzw. wieder auflösen (siehe unten) |
| Lesen | `H` | Überschrift: Ebene 1 → 2 → 3 → keine (siehe unten) |
| Lesen | `A` | hier beginnt ein Absatz – noch einmal `A` nimmt es zurück (siehe unten) |
| Lesen | `I` | Inhalt: alle Überschriften des Buchs, `Enter` springt hin (siehe unten) |
| Lesen | `V` | Lesezeile mit der nächsten Zeile verbinden; `Umschalt`+`V` trennt eine so verbundene Zeile wieder |
| Lesen | `Strg`+`⌫` (Mac: `⌘`+`⌫`) | Lesezeile löschen, bzw. alle mit `Umschalt`+`↓`/`↑` markierten – für Rauschen vom Scanrand (siehe unten) |
| Lesen | `Strg`+`Z` (Mac: `⌘`+`Z`) | zuletzt gelöschte Zeilen zurückholen |
| Lesen | `W` | Whitelist anzeigen |
| Lesen | `D` | Wörterbuch: welche Rechtschreibung gilt in diesem Buch (siehe unten) |
| Lesen | `Umschalt`+`↓` / `↑` | Zeilen markieren, für eine Notiz oder zum Löschen (innerhalb der Seite); jede andere Taste hebt die Markierung auf |
| Lesen / Korrektur | `F4` oder Rechtsklick auf die Markierung | Notiz für Obsidian aus der markierten Passage, sonst aus der Lesezeile (siehe unten) |
| Lesen | `Z` | nach dem Zusammenführen zweier Arbeitsstände: zur nächsten Zeile, die an beiden Rechnern anders berichtigt wurde; `1` behält die hiesige Fassung, `2` nimmt die andere (siehe [Ein Buch als PDF sichern](pdf-sichern.md)) |
| Lesen | `O` | Notizordner für dieses Buch festlegen |
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

Neben der Auswahl steht, die wievielte Seite von wie vielen Sie vor sich haben („4 / 30“); die Pfeile `←` und `→`
links und rechts davon blättern wie `Bild↑` und `Bild↓`.

## Getrennte Wörter

Am Zeilenende getrennte Wörter schreibt das Programm mit dem Trennzeichen `¬`: `Zu¬` / `kunft`. Beide
Teile werden zusammen geprüft. Bei der Korrektur erscheinen beide Zeilen als Eingabefelder, die Schreibmarke steht im
ersten. In die zweite Hälfte kommen Sie mit `Tab` oder indem Sie mit `→` über das Zeilenende hinausgehen –
zurück mit `Umschalt`+`Tab` oder `←` am Zeilenanfang (`↓` und `↑` tun es auch, solange es keine Korrekturvorschläge
gibt; sonst wählen sie den Vorschlag). `Enter` übernimmt beide Zeilen. `F7` fügt das Zeichen ein, am Zeilenende auch `-` (auf dem MacBook ohne `fn` zu
erreichen).

Auch ein Wort, das **über die Seitengrenze** getrennt ist (`Ge¬` am Ende der einen Seite, `walt` am Anfang der nächsten,
die Seitenzahl dazwischen), wird als Ganzes geprüft. Ist es unbekannt, sind beide Hälften rot; der Hinweis sagt dann, dass
das Wort auf der anderen Seite weitergeht, und Sie ändern auf jeder Seite ihre Hälfte.

## Korrekturvorschläge

Sobald Sie ein rotes Wort zur Korrektur öffnen – mit der `Leertaste`, mit `Enter` auf einer Zeile mit rotem Wort,
mit `Tab` zum nächsten, per Klick auf das Wort oder weil nach `Enter` in derselben Zeile noch eines steht –, zeigt das
Programm in einem kleinen Menü unter dem Wort Vorschläge, das Wahrscheinlichste zuerst (höchstens sechs):

1. **Was Sie in diesem Buch schon einmal daraus gemacht haben.** Wer `Würllemberg` einmal zu `Württemberg` berichtigt
   hat, bekommt das beim nächsten `Würllemberg` als ersten Vorschlag – das Programm lernt aus Ihrem Korrekturprotokoll,
   auch aus Serienkorrekturen. Was Sie am häufigsten daraus gemacht haben, steht vorn.
2. **Typische Lesefehler der Fraktur-Erkennung**, rückgängig gemacht: `b`/`d`, `f`/`s`, `n`/`u`, `r`/`t`, `ll`/`tt`,
   fehlende Umlautpunkte. Aus `ber` wird `der`, aus `Bolk` `Volk`, aus `Zutunft` `Zukunft` – aber nur, wenn das Ergebnis
   ein bekanntes Wort ist (Wörterbuch, Whitelist oder häufig im Buch). Was im Buch oft vorkommt, steht vorn.
3. **Das Wörterbuch** (Hunspell). Diese Vorschläge brauchen ein, zwei Sekunden. Das Programm rechnet sie deshalb
   schon für die nächsten roten Wörter aus, während Sie noch lesen – kommen Sie dort an, stehen sie meist sofort da.
   Sonst erscheinen sie etwas später; die ersten beiden Gruppen stehen immer sofort da. Haben Sie inzwischen schon
   einen Vorschlag gewählt, bleibt der stehen – die Wörterbuchvorschläge werden nur hinten angefügt. Ihre Tasten
   bremst das Rechnen nicht: Es hält an, solange das Programm etwas für Sie erledigt. Für Wörter mit nur zwei Buchstaben fragt das Programm das
   Wörterbuch nicht.

`↓` setzt den ersten Vorschlag ins Feld, jedes weitere `↓` den nächsten, `↑` geht zurück (bis zum Wort, wie es erkannt
wurde); ein Klick auf einen Vorschlag tut dasselbe. `Enter` übernimmt wie immer. Wollen Sie keinen der Vorschläge,
tippen Sie einfach.

Findet das Programm zu einem Wort nichts, erscheint kein Menü. Beim freien Bearbeiten
einer Zeile (`F2`) und in der Tabelle gibt es keine Vorschläge, ebenso nicht bei einer rot markierten Seitenzahl in der
Kopfzeile – dort steht die erwartete Zahl schon im Hinweis über dem Feld.

## Serienkorrektur (F9)

Derselbe Lesefehler kommt in einem Buch oft dutzendfach vor (`ber` statt „der“, `bie` statt „die“). Die
Serienkorrektur zeigt alle Fundstellen eines Wortes auf einmal und ersetzt sie nach einem kurzen Blick auf
die Bildausschnitte.

- Wer zum Beispiel `ber` → `der` korrigiert, sieht danach den Hinweis „‚ber‘ kommt noch 74× im Buch vor –
  F9 zeigt alle Stellen“. Das gilt, bis Sie selbst weitergehen – auch wenn das Programm schon zum nächsten roten
  Wort derselben Zeile gesprungen ist.
- Stehen Sie auf einem roten Wort, nimmt `F9` dieses Wort – in der Korrektur ebenso wie beim Lesen (das rote Wort
  der Lesezeile). Haben Sie die Verbesserung schon ins Feld getippt, steht sie gleich als Ersetzung da, sonst tippen
  Sie sie ein.
- Sonst geben Sie beide Wörter frei ein.

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
  wird das getrennte Wort dabei zusammengezogen (`Zu¬` + `kunft` → `Zukunft`). Stehen die beiden Zeilen auch im
  Seitenbild untereinander, fragt das Programm erst nach (noch einmal `V`): Daraus würde eine überlange Zeile, die im
  Druck zwei sind. Um einen **Absatz** zu kennzeichnen, verbinden Sie keine Zeilen – dafür gibt es `A` (siehe unten).
- **Wieder trennen:** `Umschalt`+`V` auf einer verbundenen Zeile trennt sie genau dort, wo sie verbunden wurde, samt
  Bildausschnitt – mehrmals hintereinander auch mehrere Verbindungen. Das geht, solange die Zeile seither nicht
  geändert wurde.

Das Programm teilt bzw. vereinigt dabei auch den **Bildausschnitt** der Zeile (beim Teilen anteilig an der Trennstelle;
ist er mehrere Zeilen hoch, waagrecht zwischen den gedruckten Zeilen).
So behält jede Textzeile ihre Stelle im Seitenbild – anders als beim Ändern der Zeilenzahl in einem fremden Editor.
Innerhalb einer Tabelle wird die Tabelle danach neu durchgezählt: Verrutschte Spalten stehen wieder richtig.

## Rauschen vom Scanrand löschen

Bei Scans mit dunklem Rand oder angeschnittener Nachbarseite liest die Texterkennung manchmal Zeilen, die gar kein Text
sind – oben oder unter der Seitenzahl stehen dann Buchstabenketten wie `BTB`, `LLL AAA` oder `E NN SE HE K`. Solche Zeilen
löschen Sie im Lesemodus mit `Strg`+`⌫` (am Mac `⌘`+`⌫`, die Taste *delete*): Die Lesezeile verschwindet, ohne
Rückfrage. Mehrere Zeilen auf einmal: mit `Umschalt`+`↓`/`↑` markieren, dann `Strg`+`⌫`.

Versehentlich gelöscht? `Strg`+`Z` (am Mac `⌘`+`Z`) holt die zuletzt gelöschten Zeilen an ihre Stelle zurück, auch
mehrmals hintereinander. Die Entf-Taste allein löscht absichtlich nichts – auf sie gerät man beim Lesen zu leicht.

Die Kopfzeile, der Fußnotenstrich, die Seitenzahl unten und Zeilen einer Tabelle lassen sich so nicht löschen. Wie beim
Teilen und Verbinden fällt der Bildausschnitt der Zeile mit weg, die übrigen Zeilen behalten ihre Stelle im Seitenbild;
jede Löschung steht im Protokoll `korrekturen.log`.

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
nächste Ebene, nach Ebene 3 wieder gewöhnlicher Text. Überschriften erscheinen größer und fett, ohne sichtbare
Steuerzeichen.

Steht eine Überschrift über zwei Zeilen („Drittes Kapitel.“ / „Die Reise nach Odessa.“), geben Sie beiden Zeilen
dieselbe Ebene – das Programm fasst sie zu einer Überschrift zusammen. Die Ebenen vergeben Sie am besten im ganzen Buch
gleich: Kapitel Ebene 1, Abschnitte darin Ebene 2; hat das Buch Teile, sind die Teile Ebene 1 und die Kapitel Ebene 2.

**Inhalt (`I`)** zeigt alle Überschriften des Buchs, eingerückt nach Ebene, mit der gedruckten Seitenzahl – so sehen
Sie, ob ein Kapitel fehlt. `↓` `↑` wählen, `Enter` oder ein Klick springt hin, `Esc` schließt. Beim
[Sichern als PDF](pdf-sichern.md) werden die Überschriften das Inhaltsverzeichnis des PDFs, das jeder PDF-Reader in der
Seitenleiste zeigt. Ein späterer EPUB-Export bildet daraus Kapitel und ein anklickbares Inhaltsverzeichnis.

## Absätze (A)

Im Druck endet jede Zeile am Rand; wo ein Absatz beginnt, zeigt nur der Einzug seiner ersten Zeile. Für ein späteres
E-Book, in dem der Text frei fließt, muss das Programm die Absätze kennen. Beim ersten Öffnen eines Buchs erkennt es
sie selbst am Einzug im Seitenbild und rückt die erste Zeile jedes Absatzes auch im Text ein; unten in der Statuszeile
steht, wie viele es gefunden hat.

Wo es sich geirrt hat: `A` auf der Lesezeile setzt dort einen Absatzanfang, noch einmal `A` nimmt ihn wieder weg.
`U` nimmt alle erkannten Absatzanfänge auf einmal zurück, solange danach keine Serienkorrektur kam (`U` sagt vorher,
was es zurücknimmt). Erkannt wird das Buch danach nicht noch einmal – die Absätze setzen Sie dann mit `A` von Hand.

Erkannt wird nur, was eindeutig aussieht: Die Zeile ist gegenüber ihren Nachbarn eingerückt, und die Zeile davor endet
mit einem Satzzeichen. Verse, Listen und Register bleiben so meist unberührt. Ohne Zeilenlage im Bild (ein Buch aus
einem EPUB ohne PDF) oder in einem Buch ohne Einzüge erkennt das Programm keine Absätze. In der Textdatei steht ein
Absatzanfang als `<p>` am Zeilenanfang, wie im EPUB.

## Weitere Auszeichnung

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

    Seite 57, Zeile 3–4, [[0 Quellenangabe|Leibbrandt 1928]]

Oben Platz für die eigene Anmerkung, unter dem Strich das Zitat (am Zeilenende getrennte Wörter sind zusammengezogen) und die
Seite – die gedruckte Seitenzahl aus der Kopfzeile oder vom Seitenende; fehlt sie oder passt sie nicht zu den Nachbarseiten, die Zahl, die
sich aus den Nachbarseiten ergibt; sonst die PDF-Seite –, die Zeilen (gezählt wie „Zeile 3/42“ in der
Kopfleiste des Programms) und der Verweis auf die Quellenangabe des Buchs.
Diese Datei `0 Quellenangabe.md` legt das Programm beim ersten Zettel als Vorlage an; tragen Sie dort ein, woher das Buch
stammt (Universitätsbibliothek, Fernleihe …) und die Zitierweise, wie Zotero sie liefert. So hat jeder Zettel per Klick
seine vollständige Quelle. Das Zitat liegt außerdem in der Zwischenablage.

Ist Obsidian installiert, öffnet es den neuen Zettel sofort und kommt unter Windows in den Vordergrund (der Ordner muss in einem Vault liegen, den Obsidian kennt).
Ohne Obsidian bleibt die Datei einfach im Ordner – es ist gewöhnliches Markdown.

Markierungen, die Sie auf dem Kindle gemacht haben, werden auf dieselbe Weise zu Zetteln: [Markierungen vom Kindle](kindle.md).

## Eine Seite ersetzen

Eine Seite war schief eingescannt, abgeschnitten oder unscharf, und das Buch ist sonst in Ordnung? Dann muss nicht das
ganze Buch neu erkannt werden. Fotografieren oder scannen Sie die Seite noch einmal und klicken Sie in der Kopfleiste
auf **Seite ersetzen …** (nur am Rechner, auf dem das Programm läuft):

1. Datei wählen – eine Bilddatei (JPG, PNG, TIF) oder ein PDF. Bei einem PDF mit mehreren Seiten geben Sie an, welche
   Seite gemeint ist; vorgeschlagen wird die Nummer der Seite, auf der Sie gerade stehen.
2. Schrift wählen (Fraktur oder Antiqua) und **Seite ersetzen**.

Das Seitenbild wird ausgetauscht und der Text **nur dieser Seite** neu erkannt – mit Tesseract; ohne Tesseract mit dem
Text, den ein durchsuchbares PDF schon mitbringt. Alle anderen Seiten bleiben, wie sie sind, auch Ihre Korrekturen
dort. Die bisherige Fassung der Seite – Text, Zeilenlage und Bild – liegt danach gesichert im Buchordner
(`vorher-<Datum>.zip`); in der Bibliothek holt **Frühere Fassung** sie zurück.

## Über das Heimnetz mitlesen

Wird das Programm mit der Option `--lan` gestartet, ist es auch von anderen Geräten im selben Netz
erreichbar (die Adresse steht beim Start im Fenster). Es gibt keinen Passwortschutz – nur im eigenen
Heimnetz verwenden. Bücher hinzufügen kann man nur an dem Rechner, auf dem das Programm läuft.
