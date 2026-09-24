# Markierungen vom Kindle

Wer auf dem Kindle liest und dabei markiert, kann die Markierungen als Zettel in [Obsidian](https://obsidian.md)
übernehmen – genauso wie die Zettel, die beim Lesen im Fraktur-Korrektor mit `F4` entstehen (siehe
[Bedienung](usage.md)). Nach dem Vorbild von Niklas Luhmanns Zettelkasten: eine Markierung je Zettel, jeder mit
Quellenangabe.

## So geht es

1. Den Kindle mit dem USB-Kabel an den Rechner anschließen.
2. In der Bibliothek unter der Liste der Bücher auf **Kindle-Markierungen nach Obsidian …** klicken. Erscheint der
   Kindle als Laufwerk, hat das Programm die Datei schon gefunden; sonst wählen Sie sie mit **Datei wählen …**
   (woher sie kommt, steht im nächsten Abschnitt).
3. Das **Buch** wählen. Die zuletzt gelesenen stehen oben, jeweils mit der Zahl der Markierungen und eigenen Notizen.
4. Den **Ordner im Obsidian-Vault** prüfen, in den die Zettel zu diesem Buch kommen. Das Programm schlägt einen vor:
   Liegt ein Buch mit demselben Titel in Ihrer Bibliothek und hat es schon einen Notizordner, dann diesen – so liegen
   die Zettel aus dem Kindle und aus dem Fraktur-Korrektor beisammen. Sonst einen neuen Ordner mit dem Titel des
   Buchs neben dem Notizordner des Buchs, das Sie zuletzt geöffnet haben. Ein letzter neuer Ordner wird angelegt.
5. **Zettel anlegen.** Das Fenster sagt, wie viele es geworden sind, und zeigt auf Wunsch den Ordner.

Die Datei lässt sich auch über **Öffnen …** zeigen: Das Programm erkennt sie und führt zum selben Fenster.

## Die Datei My Clippings.txt

Der Kindle schreibt alle Markierungen, Notizen und Lesezeichen in eine einzige Datei: `My Clippings.txt` im Ordner
`documents` – sie heißt auch auf deutschen Geräten so.

- **Ältere Kindles** erscheinen am Rechner als Laufwerk, wie ein USB-Stick. Das Programm findet die Datei dann selbst.
- **Kindles ab 2024** (etwa der Paperwhite der 12. Generation, der Colorsoft und der Scribe) melden sich als
  Mediengerät. Unter **Windows** erscheint der Kindle im Explorer als Gerät: dort den Ordner `documents` öffnen,
  `My Clippings.txt` auf den Schreibtisch ziehen und diese Kopie wählen. Am **Mac** braucht es ein Zusatzprogramm,
  etwa Amazons App *Send to Kindle* für Mac; darin öffnet das Menü *Tools* → *USB File Manager* die Dateien des
  Kindle (Stand September 2026).
- Markierungen aus der **Kindle-App** auf Handy oder Tablet stehen nicht in dieser Datei, nur die vom Gerät selbst.

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

Lesen Sie die Datei einfach wieder ein. Markierungen, die schon als Zettel im Ordner stehen, übergeht das Programm
– es erkennt sie am Zitat. Neue Zettel bekommen die nächsten Nummern. Haben Sie das Zitat in einem Zettel von Hand
geändert, erkennt das Programm ihn nicht wieder und legt die Markierung noch einmal an.

Das Programm verändert nichts auf dem Kindle und überschreibt keinen Zettel.
