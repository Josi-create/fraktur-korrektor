# Markierungen vom Kindle

Wer auf dem Kindle liest und dabei markiert, kann die Markierungen als Zettel in [Obsidian](https://obsidian.md)
übernehmen – genauso wie die Zettel, die beim Lesen im Fraktur-Korrektor mit `F4` entstehen (siehe
[Bedienung](usage.md)). Nach dem Vorbild von Niklas Luhmanns Zettelkasten: eine Markierung je Zettel, jeder mit
Quellenangabe.

## Welche Bücher gehen?

**Alle Bücher ohne Kopierschutz** – das sind vor allem die, die Sie selbst auf den Kindle gebracht haben: per
*Send to Kindle* geschickt oder mit dem Kabel kopiert, etwa ein E-Book, das Sie mit dem Fraktur-Korrektor gesichert
haben (siehe [Ein Buch als E-Book sichern](epub-sichern.md)). Ihre Markierungen darin werden immer zu Zetteln.

**Gekaufte Bücher** aus dem Kindle-Shop sind kopiergeschützt. Neuere Kindles speichern zu einer Markierung nur noch die
Stelle im Buch, nicht den Text (siehe unten), und an den verschlüsselten Text kommt das Programm nicht heran. Aus
gekauften Büchern übernimmt es deshalb nur, was der Kindle noch in die Datei `My Clippings.txt` geschrieben hat – bei
Ihrem Gerät meist alles bis zu einem Tag im Sommer 2026. Das Fenster nennt die gekauften Bücher mit neueren
Markierungen beim Namen. Deren Text finden Sie in Amazons Notizbuch im Browser:
[Markierungen aus gekauften Büchern](kindle-notizbuch.md).

## So geht es

1. Den Kindle mit dem USB-Kabel an den Rechner anschließen und **entsperren** (auf den Bildschirm tippen bzw.
   wischen) – solange die Sperre davor ist, sieht der Rechner seine Dateien nicht. Zeigt der Kindle eine Meldung zur
   USB-Verbindung, tippen Sie dort **nicht** auf **Verbindung trennen**: Sonst sieht der Rechner den Kindle nicht mehr.
2. In der Bibliothek unter der Liste der Bücher auf **Kindle-Markierungen nach Obsidian …** klicken. Unter Windows
   findet das Programm den Kindle von selbst und liest seine Markierungen, das dauert einige Sekunden. Sonst wählen
   Sie die Datei `My Clippings.txt` mit **Datei wählen …** (woher sie kommt, steht weiter unten).
3. Das **Buch** wählen. Die zuletzt gelesenen stehen oben, jeweils mit der Zahl der Markierungen und eigenen Notizen
   und dem Tag der letzten. Bücher, in denen Sie nur Lesezeichen gesetzt haben, stehen darunter mit Namen: Zu einem
   Lesezeichen speichert der Kindle keinen Text, daraus wird kein Zettel.
4. Den **Ordner im Obsidian-Vault** prüfen, in den die Zettel zu diesem Buch kommen. Das Programm schlägt einen vor:
   Liegt ein Buch mit demselben Titel in Ihrer Bibliothek und hat es schon einen Notizordner, dann diesen – so liegen
   die Zettel aus dem Kindle und aus dem Fraktur-Korrektor beisammen. Sonst einen neuen Ordner mit dem Titel des
   Buchs neben dem Notizordner des Buchs, das Sie zuletzt geöffnet haben. Ein letzter neuer Ordner wird angelegt.
5. **Zettel anlegen.** Das Fenster sagt, wie viele es geworden sind, und zeigt auf Wunsch den Ordner.

Die Datei lässt sich auch über **Öffnen …** zeigen: Das Programm erkennt sie und führt zum selben Fenster.

## Wenn der Kindle nicht erscheint

- Ist der Kindle **entsperrt**? Auf den Bildschirm tippen und im Fenster auf **Noch einmal suchen** klicken.
- Haben Sie auf dem Kindle **Verbindung trennen** getippt? Dann das USB-Kabel abziehen und wieder anstecken.
- Hilft das nicht, stecken Sie das Kabel in eine andere USB-Buchse des Rechners.
- Nehmen Sie ein **anderes USB-Kabel**. Manche Kabel laden nur und übertragen keine Daten – der Kindle lädt dann,
  aber der Rechner sieht ihn nicht.

## Wo der Kindle die Markierungen ablegt

Bis Sommer 2026 schrieb der Kindle alle Markierungen, Notizen und Lesezeichen in eine einzige Datei:
`My Clippings.txt` im Ordner `documents` – sie heißt auch auf deutschen Geräten so. Seit einer Aktualisierung der
Kindle-Software (Version 5.19, Sommer 2026) kommt dort nichts Neues mehr hinzu. Neue Markierungen stehen in einer
Datenbank in einem verborgenen Ordner des Kindle, und zwar nur als Stelle im Buch; den Text dazu liest das Programm
aus dem Buch selbst. Beides erledigt das Fenster, Sie müssen dafür nichts tun – es nimmt aus beiden Quellen, was es
findet, und jede Markierung nur einmal.

- **Unter Windows** liest das Programm beides vom angeschlossenen Kindle. Dabei kopiert es die Datei, die Datenbank
  und die Bücher, zu denen es Markierungen gibt, in seinen eigenen Ordner; auf dem Kindle verändert es nichts.
- **Ältere Kindles** erscheinen am Rechner als Laufwerk, wie ein USB-Stick. Auch dort findet das Programm alles
  selbst.
- **Am Mac** erscheinen Kindles ab 2024 (etwa der Paperwhite der 12. Generation, der Colorsoft und der Scribe) nicht
  im Finder. Mit Amazons App *Send to Kindle* für Mac öffnet das Menü *Tools* → *USB File Manager* die Dateien des
  Kindle (Stand September 2026); kopieren Sie dort `My Clippings.txt` aus dem Ordner `documents` und wählen Sie
  diese Kopie. Die neuen Markierungen aus der Datenbank kommen am Mac bisher nicht an.
- Markierungen aus der **Kindle-App** auf Handy oder Tablet stehen weder in der Datei noch in der Datenbank des
  Geräts.
- **Eine Kopie veraltet.** Haben Sie `My Clippings.txt` von Hand kopiert, nennt das Fenster den Tag des jüngsten
  Eintrags. Fehlt ein Buch, schließen Sie den Kindle an und öffnen Sie das Fenster noch einmal.

## Was in den Zetteln steht

Jede Markierung wird ein Zettel, fortlaufend nummeriert wie die Zettel aus `F4`, zum Beispiel `12 Seite 57.md`:

    **Anmerkung**

    Vgl. Stumpp, S. 40

    ---

    > Die Kolonisten zogen nach Osten. Der Weg war weit.

    Seite 57, Position 180–183, [[0 Quellenangabe|Die Reise nach Rußland]]

- **Seite und Position.** Die Seite steht nur da, wenn das E-Book Seitenzahlen der gedruckten Ausgabe mitbringt;
  viele haben keine. Die Position ist die Zählung des Kindle und findet die Stelle im E-Book wieder.
- **Ihre eigenen Notizen** vom Kindle stehen als Anmerkung über dem Zitat, zu dem sie gehören. Eine Notiz ohne
  Markierung wird ein Zettel ohne Zitat.
- **Erweiterte Markierungen.** Zieht man eine Markierung auf dem Kindle länger, legt er einen neuen Eintrag an und
  lässt den alten stehen. Das Programm nimmt nur die längere Fassung.
- **Die Kopiergrenze.** Manche Verlage begrenzen, wie viel sich aus einem Buch markieren lässt. Ist die Grenze
  erreicht, speichert der Kindle statt des Texts nur einen Hinweis. Das Programm sagt, wie viele Markierungen das
  betrifft.
- **Die Quellenangabe.** Beim ersten Zettel legt das Programm im Ordner die Datei `0 Quellenangabe.md` an, mit Titel,
  Autor und dem Vermerk *Kindle-Ausgabe*. Tragen Sie dort die Zitierweise ein, wie Zotero sie liefert – jeder Zettel
  verweist per Klick darauf. Eine schon vorhandene Quellenangabe bleibt, wie sie ist.

## Nach dem Weiterlesen

Öffnen Sie das Fenster einfach wieder. Markierungen, die schon als Zettel im Ordner stehen, übergeht das Programm
– es erkennt sie am Zitat und an der Stelle (Seite, Position). Neue Zettel bekommen die nächsten Nummern. Haben Sie
auf dem Kindle später eine Notiz zu einer schon übernommenen Markierung geschrieben, kommt sie als eigener Zettel mit
derselben Stelle dazu; den vorhandenen Zettel ändert das Programm nicht. Haben Sie das Zitat oder die Quellenzeile in
einem Zettel von Hand geändert, erkennt das Programm ihn nicht wieder und legt die Markierung noch einmal an.

Das Programm verändert nichts auf dem Kindle und überschreibt keinen Zettel.
