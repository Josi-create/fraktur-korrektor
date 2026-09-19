# Ein Buch öffnen

Die Startseite des Programms ist die **Bibliothek**. Sie zeigt alle Bücher, die Sie schon einmal geöffnet
haben, das zuletzt benutzte zuoberst. Ein Klick auf ein Buch öffnet es an der Stelle, an der Sie aufgehört
haben.

## Ein Knopf für alles: „Öffnen …“

Sie müssen nicht wissen, in welcher Form Ihr Buch vorliegt. Klicken Sie auf **Öffnen …** und zeigen Sie dem
Programm eine **Datei** oder einen **Ordner**. Es sieht nach, was darin steckt, und schlägt vor, wie es weitergeht:

| Gefunden | Was dann geschieht |
|---|---|
| 📖 **Buch** – ein Ordner, an dem Sie mit dem Fraktur-Korrektor schon gearbeitet haben | wird sofort geöffnet |
| 📄 **PDF** | Ist es schon durchsuchbar, wird der Text in Sekunden übernommen; sonst erkennt Tesseract den Text. Siehe [PDF oder Bilder einlesen](pdf-import.md) |
| 📗 **EPUB** | Liegt ein **gleichnamiges PDF** daneben, erscheint links der Scan und rechts der Text des EPUB. Ohne PDF wird das Buch ohne Seitenbilder geöffnet |
| 🖼️ **Seitenbilder** – ein Ordner mit JPG, PNG oder TIF | Tesseract erkennt den Text |
| 🗂️ **Export aus Transkribus** – ZIP-Datei oder entpackter Ordner | wird importiert. Siehe [Mit Transkribus arbeiten](transkribus.md) |

Wählen Sie einen ganzen Ordner, findet das Programm oft mehreres – zum Beispiel ein PDF, ein EPUB und ein Buch,
an dem Sie schon korrigiert haben. Dann zeigt es alle Funde mit Seitenzahl und Datum. Der erste ist die
**Empfehlung**:

- Ein Buch, in dem schon **Korrekturen** stecken, steht immer vorn („hier steckt Ihre Arbeit“) – damit Sie nicht
  versehentlich von vorn anfangen.
- Danach kommt, was am weitesten gediehen ist: ein Transkribus-Export vor einem EPUB, ein EPUB vor einem PDF,
  ein PDF vor losen Bildern.
- Ist ein anderer Fund **neuer** als die Empfehlung, steht das dabei.

Sie können jederzeit einen anderen Fund anklicken. Ist die Sache eindeutig, fragt das Programm gar nicht erst.

## EPUB und PDF zusammen

Haben Sie ein Buch schon einmal zu einem EPUB verarbeitet und möchten es noch einmal gegen den Scan lesen? Legen
Sie EPUB und PDF mit gleichem Namen in denselben Ordner – Zusätze wie „(durchsuchbar)“, „(kompakt)“ oder „_OCR“
stören nicht:

    Fatma - Immanuel Walker.epub
    Fatma - Immanuel Walker (durchsuchbar).pdf

Das Programm nimmt Seitenbilder und Zeilen aus dem PDF und setzt den **Wortlaut des EPUB** in diese Zeilen ein.
Trennungen am Zeilenende bleiben erhalten. Kopfzeilen und Fußnoten, die im EPUB an anderer Stelle oder gar nicht
stehen, behalten den Text aus dem PDF. Am Ende erfahren Sie, wie viel Prozent der Zeilen den EPUB-Text tragen.
Gibt es mehrere passende PDFs, wird das durchsuchbare mit der besseren Bildqualität genommen.

Das EPUB selbst wird dabei nicht verändert; Ihre Korrekturen landen in den Textdateien des neuen Buchordners.

## Export aus Transkribus

Beim Import erkennt das Programm Kopfzeilen (Seitenzahlen) und trennt Fußnoten vom Haupttext. Wo das nicht
stimmt, korrigieren Sie es beim Lesen mit der Taste `F` (siehe [Bedienung](usage.md)). Enthält der Export keine
Seitenbilder, sucht das Programm im gewählten Ordner nach einem Bilderordner mit genau so vielen Bildern, wie der
Export Seiten hat, und schlägt ihn vor.

Nichts wird je überschrieben: Gibt es den Titel schon, entsteht ein zweiter Ordner mit dem Zusatz „(2)“.

## Was in einem Buchordner liegt

Neue Bücher legt das Programm unter `Fraktur-Korrektor` in Ihrem Benutzerordner an.

| Datei | Inhalt |
|---|---|
| `001.txt`, `002.txt`, … | der Text, eine Datei je Seite: optional `# Kopfzeile`, Haupttext, `---`, Fußnoten |
| `img/001.jpg` … | die Seitenbilder (JPG oder PNG) |
| `lines.json` | wo jede Textzeile im Seitenbild steht |
| `whitelist.txt` | Wörter, die Sie mit `F8` als richtig bestätigt haben |
| `lesezeichen.json` | Ihre Leseposition |
| `korrekturen.log` | Protokoll aller Änderungen |
| `qualitaet.json` | nach dem Einlesen: die Werte der Ampel je Seite |

Die Textdateien dürfen Sie auch mit einem anderen Editor bearbeiten, sogar während das Programm läuft.
Ändern Sie dabei nur nicht die Zahl der Zeilen einer Seite, sonst passt die Zuordnung zum Bild nicht mehr.

## Ein Buch aus der Liste entfernen

Das ✕ rechts entfernt nur den Eintrag aus der Bibliothek. Die Dateien bleiben unangetastet.
