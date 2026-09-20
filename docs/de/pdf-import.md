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

Liegt das Buch **schon in Ihrer Bibliothek**, geht es kürzer: bei dem Buch auf die drei Punkte **⋯** und
**Für ScanTailor vorbereiten** – dann stehen Eingabe- und Ausgabeordner fest, und ScanTailor startet gleich mit.
Für ein PDF, das noch nicht eingelesen ist:

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
   `…/scantailor/out` hoch – Transkribus trennt Doppelseiten nämlich nicht.

## Grenzen

- Mehrspaltiger Satz (Zeitungen, Lexika) wird nicht spaltenweise gelesen.
