# Hilfe

Der Fraktur-Korrektor ist ein Lese- und Korrekturprogramm für Texte, die eine Texterkennung (OCR) aus
gescannten Büchern gewonnen hat – vor allem aus Büchern in Frakturschrift. Links sehen Sie das Seitenbild,
rechts den erkannten Text. Wörter, die das Programm nicht kennt, sind rot markiert. Sie lesen das Buch
einfach durch und verbessern dabei, was Ihnen auffällt. Am Ende steht ein sauberer Text.

Das Programm läuft nur auf Ihrem eigenen Rechner. Es überträgt nichts ins Internet. Der Browser dient
lediglich als Fenster.

## Die drei Schritte

1. **Texterkennung** – Aus den Seitenbildern wird Text. Dafür gibt es zwei Wege:
   - *eingebaut, ein Klick:* [PDF oder Bilder einlesen](pdf-import.md) mit dem freien Programm Tesseract;
     alles bleibt auf Ihrem Rechner. Eine Ampel zeigt danach, wie gut das Ergebnis ist.
   - *für schwierige Vorlagen:* [Transkribus](transkribus.md), ein Internetdienst mit meist besserer
     Fraktur-Erkennung.
2. **Öffnen** – Ein einziger Knopf: Sie zeigen dem Programm eine Datei oder einen Ordner, es erkennt selbst, ob es
   ein PDF, ein EPUB, Seitenbilder, ein Transkribus-Export oder ein schon bearbeitetes Buch ist: [Ein Buch öffnen](add-book.md).
3. **Lesen und korrigieren** – [Bedienung](usage.md). Alles geht mit der Tastatur; die wichtigsten Tasten
   stehen immer oben rechts im Fenster.

## Gut zu wissen

- **Jede Korrektur wird sofort gespeichert**, direkt in den Textdateien des Buchordners. Es gibt kein
  „Speichern“. Zusätzlich führt das Programm in `korrekturen.log` Buch über jede Änderung.
- **Ihre Leseposition** merkt sich das Programm je Buch.
- **Sicherung:** Kopieren Sie ab und zu den ganzen Buchordner – darin steckt Ihre gesamte Arbeit.
- **Beim ersten Öffnen** eines Buchs prüft das Programm jedes Wort gegen das Wörterbuch. Das kann bis zu
  einer Minute dauern, danach geht es schnell.
- **Das Wörterbuch passt sich dem Buch an:** Das Programm schätzt das Erscheinungsjahr und lässt danach die
  Rechtschreibung von 1901–1996 („daß“), die neue („dass“) oder auch Schreibungen vor 1901 („Thür“, „giebt“) gelten.
  Mit der Taste `D` ändern Sie das je Buch – siehe [Bedienung](usage.md). Ein einzelnes Wort merkt sich das Programm
  mit `F8` als richtig.
