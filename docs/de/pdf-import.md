# PDF oder Bilder einlesen

Haben Sie ein Buch als gescanntes PDF oder als Ordner mit Seitenfotos, kann der Fraktur-Korrektor den Text
selbst erkennen. Er benutzt dafür das freie Programm **Tesseract**, das auf Ihrem Rechner läuft – es wird
nichts ins Internet übertragen. Tesseract ist im fertigen Programm enthalten; nur wer aus dem Quelltext
startet, installiert es selbst: [Werkzeuge installieren](install-tools.md).

**Zum Ausprobieren** eignet sich eine gemeinfreie Ausgabe von Goethes *Faust* (Fraktur, 470 Seiten, 17 MB):
<https://archive.org/download/fausteinetragd00goetuoft/fausteinetragd00goetuoft.pdf>. Sie bringt schon eine Textebene mit – gut, um beide Wege zu vergleichen (siehe unten).

## So geht es

1. In der Bibliothek auf **Öffnen …** klicken und das PDF (**Datei wählen …**) oder den Ordner mit den Seitenbildern
   (**Ordner wählen …**) zeigen. Das Programm erkennt selbst, was es vor sich hat – siehe [Ein Buch öffnen](add-book.md).
2. Das Fenster zeigt, ob Tesseract und das Fraktur-Modell vorhanden sind. Beides ist im fertigen Programm
   enthalten; das Modell stammt von der Universitätsbibliothek Mannheim.
3. Titel eintragen und die **Schrift** wählen: Fraktur oder Antiqua (lateinische Schrift).
4. **Texterkennung starten.** Ein Balken zeigt den Fortschritt; rechnen Sie mit wenigen Sekunden je Seite.
   Mit *Abbrechen* lässt sich der Vorgang jederzeit stoppen.

## Durchsuchbare PDFs: Text übernehmen

Viele PDFs sind schon „durchsuchbar“: Ein anderes Programm (ABBYY FineReader, OCRmyPDF, der Scanner selbst) hat
den Text bereits erkannt und unsichtbar hinter das Seitenbild gelegt. Der Fraktur-Korrektor bemerkt das und fragt:

- **Text übernehmen** – dauert nur Sekunden, auch bei mehreren hundert Seiten. Die Seitenbilder werden unverändert
  aus dem PDF genommen. Tesseract wird dafür nicht gebraucht.
- **Text neu erkennen** – sinnvoll, wenn der vorhandene Text schlecht ist, zum Beispiel weil ein Frakturbuch mit
  einem Programm für lateinische Schrift erkannt wurde.

Im Zweifel erst übernehmen und die Ampel ansehen. Ist sie nicht grün, das Buch noch einmal einlesen und neu erkennen lassen.

Stammt das PDF aus einer Bibliothek und enthält keinen Text, lohnt ein Blick auf deren Seiten: Oft liegt der
erkannte Text dort getrennt vom PDF bereit (hOCR oder ALTO) und lässt sich nachträglich über das Buch legen –
siehe [Text aus einer Bibliothek](add-book.md).

## Die Ampel

Nach der Erkennung schätzt das Programm, wie gut das Ergebnis ist. Es benutzt dafür zwei Werte: wie sicher
sich Tesseract bei den Wörtern war, und wie viele Wörter im Wörterbuch stehen. (Bei übernommenem Text zählt nur das
Wörterbuch – ein PDF speichert nicht, wie sicher die Erkennung war.)

| Ampel | Bedeutung | Was tun? |
|---|---|---|
| 🟢 grün | Gute Erkennung, etwa so gut wie Transkribus. | Einfach lesen und korrigieren. |
| 🟡 gelb | Brauchbar, aber mit vielen Lesefehlern. | Für wenige Seiten in Ordnung. Für ein ganzes Buch lohnt sich [Transkribus](transkribus.md). |
| 🔴 rot | Schlechte Erkennung. | Nicht von Hand korrigieren – erst die Vorlage verbessern (*Scans vorbereiten*, siehe unten) oder [Transkribus](transkribus.md) benutzen. |

Der farbige Punkt erscheint auch in der Bibliothek vor dem Buchtitel. Die Werte jeder einzelnen Seite stehen
in der Datei `qualitaet.json` im Buchordner.

Ein eingelesenes Buch können Sie jederzeit durch eine bessere Fassung ersetzen: Lesen Sie es einfach noch
einmal ein (es entsteht ein zweiter Ordner) und entfernen Sie den alten Eintrag aus der Bibliothek.

## Doppelseiten, schiefe Seiten, dunkle Ränder: Scans vorbereiten

Texterkennung ist nur so gut wie das Bild. Wer ein Buch im Lesesaal abfotografiert, hat meist **zwei Buchseiten
auf einem Bild**, die Seiten liegen **schief**, und am Rand sind **Tischplatte, Buchkante oder ein Finger** mit
im Bild. Alles drei erledigt das Programm selbst, bevor es den Text erkennt:

1. Über **Öffnen …** das PDF oder den Ordner mit den Fotos zeigen. Das Programm sieht sich einige Seiten an.
   Stehen zwei Seiten nebeneinander, liegen sie schief oder läuft ein dunkler Rand an der Seite entlang, erscheint
   die Empfehlung **Scans vorbereiten …**.
2. Darauf klicken. Sie sehen die erste Doppelseite mit einer **roten Linie**. Steht sie in der Bundmitte? Sonst
   ziehen Sie sie mit der Maus dorthin oder verschieben sie mit den Pfeiltasten `←` `→` (mit `Umschalt` in
   größeren Schritten). Die Linie gilt für alle Seiten; auf jeder einzelnen sucht das Programm die Falz noch einmal
   in der Nähe und passt die Linie an. Drei Häkchen sagen, was geschehen soll: **Doppelseiten an der Linie
   teilen**, **Schiefe Seiten geraderichten** – dahinter steht der gemessene Winkel – und **Dunkle Ränder und
   Finger entfernen**. Bei diesem Häkchen zeigt ein **grün gestrichelter Kasten** auf der Vorschau, was von der
   gezeigten Seite bleibt; auf jeder anderen Seite misst das Programm neu.
3. **Übernehmen.** Ein Balken zeigt den Fortschritt; rechnen Sie mit etwa einer Sekunde je Seite. Die
   vorbereiteten Seiten kommen in einen eigenen Ordner `aufbereitet` im Buchordner; Ihre Vorlage bleibt unverändert.
   Aus jeder Doppelseite werden zwei Seiten, linke zuerst. Gedreht wird nur, was mehr als 0,3° schief liegt.
   Abgeschnitten wird nur, was deutlich dunkler als das Papier ist und am Bildrand liegt – nie der Text selbst:
   Um den Textblock bleibt immer ein Sicherheitsabstand. Ein Finger, der von unten oder von der Seite hereinragt,
   wird weiß übermalt; ragt er bis an den Text, bleibt dieses Stück stehen, damit keine Buchstaben verloren
   gehen. Ein Schatten, der über die halbe Seite reicht, wird in Ruhe gelassen. Bei Fotos vom Lesesaal-Tisch lohnt
   sich ein Blick auf ein paar vorbereitete Seiten; ist der Schnitt zu knapp oder zu großzügig, lassen Sie die
   Vorlage ohne das Häkchen noch einmal vorbereiten.
4. Danach ist der neue Ordner schon ausgewählt: auf **Texterkennung starten** klicken. Das Programm merkt sich,
   dass die Seiten vorbereitet wurden (Kennzeichen *vorbereitet* in der Bibliothek).

Liegt das Buch **schon in Ihrer Bibliothek** – etwa weil Sie die Doppelseiten erst einmal so haben erkennen
lassen –, steht beim Buch der Knopf **Scans vorbereiten**. Er bereitet die Seitenbilder des Buchs auf und bietet
anschließend an, den Text neu erkennen zu lassen; es entsteht ein neues Buch, das bisherige bleibt.

**Einfacher ist es, gar keine Doppelseiten zu fotografieren.** Ein paar Aufnahmetipps: jede Seite einzeln und
bildfüllend, das Buch flach halten (mit der freien Hand oder einem Gewicht am Rand), die Kamera parallel zur Seite,
gleichmäßiges Licht ohne Schatten der eigenen Hand. Dann bleibt dem Programm nichts zu teilen und wenig zu drehen.

## Gewölbte Seiten, Flecken, dunkle Ränder: ScanTailor

Was das Programm nicht kann: gewölbte Seiten entzerren, Flecken mitten auf der Seite entfernen, ungleichmäßige
Ausleuchtung ausgleichen. Meldet es, dass **die Zeilenenden viel schlechter sind als der Rest**, ist die Seite
zum Bund hin gewölbt. Dafür gibt es das freie Programm **ScanTailor Advanced** ([Installation](install-tools.md)
– auf dem Mac nur mit Umständen). Es trennt auch Doppelseiten und richtet gerade, nur eben mit mehr Handarbeit.

Liegt das Buch **schon in Ihrer Bibliothek**, steht beim Buch der Knopf **Für ScanTailor vorbereiten** – dann
stehen Eingabe- und Ausgabeordner fest, und ScanTailor startet gleich mit. Für ein PDF, das noch nicht eingelesen ist:

1. Über **Öffnen …** das PDF wählen und im Fenster auf **Erst mit ScanTailor aufbereiten …** klicken.
   Das Programm speichert jede PDF-Seite als Bild (ScanTailor kann keine PDFs öffnen) und startet ScanTailor.
2. In ScanTailor: **Neues Projekt**. Als Eingabeordner den Ordner angeben, der auf `scantailor` endet.
   Abtippen müssen Sie ihn nicht: Der Fraktur-Korrektor legt den Pfad in die Zwischenablage (in das Feld
   klicken und einfügen) und öffnet den Ordner zusätzlich im Dateifenster, von wo Sie ihn hineinziehen können.
   Den vorgeschlagenen Ausgabeordner `out` beibehalten.
3. Die sechs Schritte links von oben nach unten durchgehen. Meist genügt es, in jedem Schritt unten auf den
   Pfeil ▶ zu klicken (»alle Seiten bearbeiten«) und das Ergebnis durchzublättern:
   *Ausrichtung korrigieren* → *Seiten aufteilen* → *Schräglage korrigieren* → *Inhalt auswählen* → *Ränder* →
   *Ausgabe*. Im Schritt *Ausgabe* für Fraktur: 600 dpi, Modus *Schwarz-Weiß*; bei gewölbten Seiten dort
   *Entzerren* einschalten.
4. Zurück im Fraktur-Korrektor auf **Zurück** und **Untersuchen** klicken – der Ordner `…/scantailor/out` ist schon
   eingetragen – und dann auf **Texterkennung starten**. Haben Sie das Fenster zwischendurch geschlossen, finden
   Sie den Ordner über **Öffnen …** → **Ordner wählen …**; er heißt `out` und liegt im Buchordner unter
   `scantailor`. Das Programm weist ihn als *Ergebnis von ScanTailor* aus.

   Wichtig: Nur wenn Sie **dieses** Ergebnis einlesen, arbeiten Sie mit den getrennten Seiten weiter. Lesen Sie
   erneut das PDF ein, war die ganze Mühe umsonst.

   Wollen Sie den Text lieber von [Transkribus](transkribus.md) lesen lassen, laden Sie dort die Dateien aus
   `…/scantailor/out` bzw. `…/aufbereitet` hoch – Transkribus trennt Doppelseiten nämlich nicht.

## Zweispaltiger Satz

Zeitungen und Lexika sind meist in zwei Spalten gesetzt. Das Programm erkennt das an der Lage der Zeilen und liest
spaltenweise: erst die linke Spalte von oben nach unten, dann die rechte. Eine Überschrift über beide Spalten
kommt davor; steht unter den Spalten wieder Text über die ganze Breite, folgt er danach. Kurze Fußnoten, die zu
zweit nebeneinanderstehen, bleiben zeilenweise – so sind sie durchnummeriert.

Grenzen: Drei und mehr Spalten, Tabellen und Verzeichnisse mit Seitenzahlen am rechten Rand werden weiter Zeile
für Zeile gelesen; im Zweifel ändert das Programm die Reihenfolge lieber nicht. Hat Tesseract zwei Spalten zu einer
Zeile zusammengezogen, kann das Programm sie nicht mehr trennen. Stimmt die Reihenfolge einer Seite nicht, gibt es
in der Leseansicht keinen Griff, um Zeilen zu verschieben – lassen Sie die Seite dann von
[Transkribus](transkribus.md) lesen: Dort lässt sich jede Spalte als eigener Bereich anlegen, und der Export
ersetzt den Text der Seite.
