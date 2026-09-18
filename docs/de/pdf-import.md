# PDF oder Bilder einlesen

Haben Sie ein Buch als gescanntes PDF oder als Ordner mit Seitenfotos, kann der Fraktur-Korrektor den Text
selbst erkennen. Er benutzt dafür das freie Programm **Tesseract**, das auf Ihrem Rechner läuft – es wird
nichts ins Internet übertragen. Tesseract muss einmal installiert werden:
[Werkzeuge installieren](install-tools.md).

## So geht es

1. In der Bibliothek auf **PDF oder Bilder einlesen (Texterkennung) …** klicken.
2. Oben zeigt das Fenster, ob Tesseract und das Fraktur-Modell vorhanden sind. Das Modell (5 MB, von der
   Universitätsbibliothek Mannheim) lädt das Programm beim ersten Mal selbst herunter.
3. **PDF wählen …** oder – bei Einzelbildern (JPG, PNG, TIF) – **Ordner wählen …**
4. Titel eintragen und die **Schrift** wählen: Fraktur oder Antiqua (lateinische Schrift).
5. **Texterkennung starten.** Ein Balken zeigt den Fortschritt; rechnen Sie mit wenigen Sekunden je Seite.
   Mit *Abbrechen* lässt sich der Vorgang jederzeit stoppen.

## Durchsuchbare PDFs: Text übernehmen

Viele PDFs sind schon „durchsuchbar“: Ein anderes Programm (ABBYY FineReader, OCRmyPDF, der Scanner selbst) hat
den Text bereits erkannt und unsichtbar hinter das Seitenbild gelegt. Der Fraktur-Korrektor bemerkt das und fragt:

- **Text übernehmen** – dauert nur Sekunden, auch bei mehreren hundert Seiten. Die Seitenbilder werden unverändert
  aus dem PDF genommen. Tesseract wird dafür nicht gebraucht.
- **Text neu erkennen** – sinnvoll, wenn der vorhandene Text schlecht ist, zum Beispiel weil ein Frakturbuch mit
  einem Programm für lateinische Schrift erkannt wurde.

Im Zweifel erst übernehmen und die Ampel ansehen. Ist sie nicht grün, das Buch noch einmal einlesen und neu erkennen lassen.

## Die Ampel

Nach der Erkennung schätzt das Programm, wie gut das Ergebnis ist. Es benutzt dafür zwei Werte: wie sicher
sich Tesseract bei den Wörtern war, und wie viele Wörter im Wörterbuch stehen. (Bei übernommenem Text zählt nur das
Wörterbuch – ein PDF speichert nicht, wie sicher die Erkennung war.)

| Ampel | Bedeutung | Was tun? |
|---|---|---|
| 🟢 grün | Gute Erkennung, etwa so gut wie Transkribus. | Einfach lesen und korrigieren. |
| 🟡 gelb | Brauchbar, aber mit vielen Lesefehlern. | Für wenige Seiten in Ordnung. Für ein ganzes Buch lohnt sich [Transkribus](transkribus.md). |
| 🔴 rot | Schlechte Erkennung. | Nicht von Hand korrigieren – erst die Vorlage verbessern (ScanTailor) oder [Transkribus](transkribus.md) benutzen. |

Der farbige Punkt erscheint auch in der Bibliothek vor dem Buchtitel. Die Werte jeder einzelnen Seite stehen
in der Datei `qualitaet.json` im Buchordner.

Ein eingelesenes Buch können Sie jederzeit durch eine bessere Fassung ersetzen: Lesen Sie es einfach noch
einmal ein (es entsteht ein zweiter Ordner) und entfernen Sie den alten Eintrag aus der Bibliothek.

## Schlechte Vorlagen mit ScanTailor aufbereiten

Texterkennung ist nur so gut wie das Bild. Typische Probleme sind: zwei Buchseiten auf einem Foto, schiefe
oder gewölbte Seiten, dunkle Ränder, Finger im Bild. Meldet das Programm, dass **die Zeilenenden viel
schlechter sind als der Rest**, ist die Seite zum Bund hin gewölbt.

Das freie Programm **ScanTailor Advanced** behebt all das: Es trennt Doppelseiten, richtet sie gerade,
entzerrt Wölbungen und schneidet Ränder ab. ([Installation](install-tools.md))

1. Im Fenster *PDF oder Bilder einlesen* das PDF wählen und auf **Erst mit ScanTailor aufbereiten …** klicken.
   Das Programm speichert jede PDF-Seite als Bild (ScanTailor kann keine PDFs öffnen) und startet ScanTailor.
2. In ScanTailor: **Neues Projekt**. Als Eingabeordner den Ordner wählen, den der Fraktur-Korrektor anzeigt
   (er endet auf `scantailor`). Den vorgeschlagenen Ausgabeordner `out` beibehalten.
3. Die sechs Schritte links von oben nach unten durchgehen. Meist genügt es, in jedem Schritt unten auf den
   Pfeil ▶ zu klicken (»alle Seiten bearbeiten«) und das Ergebnis durchzublättern:
   *Ausrichtung korrigieren* → *Seiten aufteilen* → *Schräglage korrigieren* → *Inhalt auswählen* → *Ränder* →
   *Ausgabe*. Im Schritt *Ausgabe* für Fraktur: 600 dpi, Modus *Schwarz-Weiß*; bei gewölbten Seiten dort
   *Entzerren* einschalten.
4. Zurück im Fraktur-Korrektor steht der Ordner `…/scantailor/out` schon im Eingabefeld. Auf
   **Texterkennung starten** klicken.

## Grenzen

- Mehrspaltiger Satz (Zeitungen, Lexika) wird nicht spaltenweise gelesen.
- Das mitgelieferte Wörterbuch kennt die Rechtschreibung von 1901 bis 1996. Bei neueren Büchern („dass“)
  und bei Drucken vor 1901 („Thür“, „giebt“) fällt die Wörterbuchquote deshalb niedriger aus, als die
  Erkennung verdient.
