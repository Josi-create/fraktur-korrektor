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
| 📕 **Gesichertes Buch (PDF)** – ein PDF, das der Fraktur-Korrektor geschrieben hat, auch auf einem anderen Rechner | wird mit allem, was darin steckt, als Buch angelegt. Siehe [Ein Buch als PDF sichern](pdf-sichern.md) |
| 📄 **PDF** | Ist es schon durchsuchbar, wird der Text in Sekunden übernommen; sonst erkennt Tesseract den Text. Siehe [PDF oder Bilder einlesen](pdf-import.md) |
| 📗 **EPUB** | Liegt ein **gleichnamiges PDF** daneben, erscheint links der Scan und rechts der Text des EPUB. Liegt es woanders, holen Sie es mit **Passendes PDF auswählen …** dazu. Ohne PDF wird das Buch ohne Seitenbilder geöffnet. Liegt daneben das gesicherte PDF desselben Buchs, empfiehlt das Programm das PDF (siehe [Ein Buch als E-Book sichern](epub-sichern.md)) |
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

### Das PDF liegt woanders

Heißt das PDF anders oder liegt es in einem anderen Ordner, findet das Programm es nicht von selbst. Dann steht
unter dem EPUB „kein gleichnamiges PDF daneben“ und darunter der Knopf **Passendes PDF auswählen …**. Wählen Sie
das PDF damit aus – oder fügen Sie seinen Pfad in das Feld ein. Danach geht es weiter wie bei EPUB und PDF im
selben Ordner.

Das Programm prüft dabei an einer Stichprobe, ob das PDF wirklich zu diesem EPUB gehört: Enthält das PDF schon
Text, vergleicht es Wortfolgen von einigen Seiten mit dem EPUB und sagt gleich, ob es passt. Enthält das PDF nur
Bilder, zeigt sich das erst nach der Texterkennung. Gehört das PDF nicht zu diesem Text, wird **kein Buch
angelegt** – Sie wählen ein anderes PDF oder legen das EPUB ohne Seitenbilder an. So kommt nie ein fremder Scan
neben Ihren Text.

### Das PDF kommt später

Haben Sie das EPUB schon ohne PDF geöffnet und vielleicht darin korrigiert, müssen Sie nicht von vorn anfangen: In
der Bibliothek steht bei einem solchen Textbuch der Knopf **PDF hinzufügen** (siehe [Ein Buch weiterbearbeiten](#ein-buch-weiterbearbeiten)).
Es entsteht ein **neues Buch** daneben: Seitenbilder und Zeilen aus dem PDF, der Wortlaut aus dem Textbuch – mit
allen Korrekturen, die Sie dort schon gemacht haben, und mit Ihrer Wortliste. Das Textbuch selbst bleibt, wie es
war; wenn Sie es nicht mehr brauchen, nehmen Sie es mit dem ✕ aus der Liste. Ein neues Buch muss es sein, weil die
Seiten des Textbuchs nichts mit den Seiten des Scans zu tun haben – Protokoll und Lesezeichen gehören zum
Textbuch.

## Export aus Transkribus

Beim Import erkennt das Programm Kopfzeilen (Seitenzahlen) und trennt Fußnoten vom Haupttext. Wo das nicht
stimmt, korrigieren Sie es beim Lesen mit der Taste `F` (siehe [Bedienung](usage.md)). Enthält der Export keine
Seitenbilder, sucht das Programm im gewählten Ordner nach einem Bilderordner mit genau so vielen Bildern, wie der
Export Seiten hat, und schlägt ihn vor.

Nichts wird je überschrieben: Gibt es den Titel schon, entsteht ein zweiter Ordner mit dem Zusatz „(2)“.

## Ein Buch weiterbearbeiten

Ein Buch entsteht selten in einem Zug: Erst lesen Sie ein PDF ein, dann lassen Sie die Seiten vorbereiten
(Doppelseiten teilen, geraderichten), dann lassen Sie den Text bei Transkribus erkennen. **Dafür müssen Sie nicht jedes Mal von vorn anfangen.**

In der Bibliothek steht unter jedem Buch eine Reihe von Knöpfen. Neben **Buch öffnen** stehen dort weitere
Wege:

| | Wozu |
|---|---|
| **Erkannten Text einlesen** | Der Text von Transkribus – oder der, den eine Bibliothek zu ihrem Digitalisat herausgibt – tritt an die Stelle des bisherigen. Ihre Seitenbilder, Ihre Wortliste und Ihr Lesezeichen bleiben, wo sie sind. Angeben können Sie die ZIP-Datei, den entpackten Ordner oder die Textdatei des Exports, oder einen Ordner mit hOCR- oder ALTO-Dateien (siehe unten). |
| **Seitenbilder hinzufügen** | Für Bücher, die nur aus Text bestehen – etwa ein Transkribus-Export ohne Bilder. Zeigen Sie auf einen Bilderordner, auf das PDF, aus dem die Seiten stammen, oder auf ein anderes Buch, das die Bilder schon hat. |
| **PDF hinzufügen** | Für ein Textbuch aus einem EPUB, das ohne PDF geöffnet wurde. Zeigen Sie auf das PDF des Scans: Es entsteht ein neues Buch mit den Seiten des Scans und Ihrem Text samt Korrekturen (siehe [EPUB und PDF zusammen](#epub-und-pdf-zusammen)). |
| **Für Transkribus vorbereiten** | Das Programm nennt Ihnen den Ordner, den Sie hochladen, legt ihn in die Zwischenablage und öffnet ihn im Dateifenster. |
| **Scans vorbereiten** | Teilt Doppelseiten und richtet schiefe Seiten gerade – mit Vorschau der Trennlinie. Das Ergebnis lassen Sie danach als neues Buch erkennen. Siehe [PDF oder Bilder einlesen](pdf-import.md). |
| **Für ScanTailor vorbereiten** | Startet ScanTailor und nennt Ein- und Ausgabeordner – für gewölbte Seiten, Flecken, dunkle Ränder. |
| **Frühere Fassung** | Holt einen Text zurück, den ein späterer Import ersetzt hat. Erscheint nur, wenn es etwas zurückzuholen gibt. |

So müssen Sie sich nie merken, wo die Bilder zu einem Buch liegen – das weiß das Programm.

### Wie die Seiten zueinander finden

Kommt ein Text von Transkribus zurück, muss jede Seite wieder zu ihrem Bild finden. Fehlt im Export auch nur
eine Seite, stünde bei blinder Zuordnung der Reihe nach ab da jeder Text neben dem falschen Bild. Darum geht
das Programm in dieser Reihenfolge vor:

1. **Über die Dateinamen.** Beim Einlesen merkt sich das Programm, wie das Bild jeder Seite ursprünglich hieß
   (`quellen.json`). Im Transkribus-Export stehen dieselben Namen – das passt eindeutig.
2. **Über den Wortlaut.** Gibt es keine Namen, vergleicht das Programm die Wörter: Dieselbe Buchseite bleibt
   erkennbar, auch wenn die eine Texterkennung schlechter war als die andere. Sichere Treffer sind die Anker,
   Seiten ohne Text (Bildtafeln) ergeben sich aus deren Abstand.
3. **Der Reihe nach** – nur, wenn hier wie dort gleich viele Seiten vorliegen.

Bleiben dabei einzelne Seiten unklar – weil links und rechts von ihnen die Zählung nicht zusammenpasst –,
lässt das Programm sie aus und sagt, wie viele es waren. Dort steht dann noch der alte Text. Geht gar nichts
auf, bricht es ab, statt den Text neben falsche Bilder zu legen. Dann legen Sie den Export mit **Öffnen …** als eigenes Buch an.

Dasselbe gilt für **Seitenbilder aus einem anderen Buch**: Sie zeigen auf das Buch, das die Bilder hat, und das
Programm vergleicht die Texte beider Bücher – es ist ja dasselbe Werk, nur anders erkannt. Darum darf das
Bilderbuch ruhig mehr Seiten haben als das, dem die Bilder fehlen.

### Woran Sie ein Buch in der Bibliothek erkennen

Hinter dem Titel stehen kleine Kennzeichen: **Tesseract**, **Transkribus**, **PDF-Text** – woher der Text
stammt – und **ScanTailor**, wenn die Seitenbilder damit aufbereitet wurden. Daneben steht, wie viele Wörter
das Wörterbuch nicht kennt („20 % rote Wörter"). Das ist dieselbe Zahl, die Sie beim Lesen als rote Wörter
sehen; alte Schreibweisen und Namen sind darunter, es sind also nicht lauter Fehler. Der farbige Punkt vor dem
Titel ist die Ampel aus dem Einlesen.

Nach diesen Kennzeichen richten sich auch die Knöpfe darunter: **Scans vorbereiten**, **Für Transkribus
vorbereiten** und **Für ScanTailor vorbereiten** sind grau, wenn sie wenig bringen – bei grüner Ampel, wenn der
Text schon aus Transkribus stammt oder die Seiten schon aufbereitet sind. **Erkannten Text einlesen** ist grau,
wenn der Text schon aus Transkribus oder von einer Bibliothek stammt oder wenn Sie schon viel korrigiert haben
(ab 50 Korrekturen): Der neue Text enthielte Ihre Korrekturen nicht. Lesen Sie ihn dann am besten *als neues Buch*
ein – das ist in diesem Fall schon vorgewählt, und das bisherige Buch bleibt, wie es ist. Die grauen Knöpfe
funktionieren trotzdem; das Programm sagt vorher, warum es davon abrät, und fragt nach.

Der Knopf **Umbenennen** gibt einem Buch einen anderen Namen, etwa wenn es noch wie die Datei heißt, aus der es
kam. Der Ordner auf der Festplatte bleibt dabei, wie er ist.

### Textexport statt PAGE XML

Transkribus kann seinen Text auch als einfache Textdatei ausgeben; die liest das Programm ebenso. Sie verlieren
dabei aber etwas: Eine Textdatei sagt nicht, wo die Zeilen im Bild stehen. Der Text steht dann zwar richtig auf
seiner Seite, lässt sich aber nicht mehr Zeile für Zeile neben dem Seitenbild mitführen – es sei denn, die neue
Erkennung teilt die Zeilen genau so auf wie die alte. Das Programm sagt Ihnen hinterher, für wie viele Seiten
das zutraf. Wenn Sie die Zeilen im Bild brauchen, holen Sie den Export noch einmal als **PAGE XML**.

### Text aus einer Bibliothek (hOCR, ALTO)

Viele Bibliotheken haben ihre Digitalisate längst durch eine Texterkennung geschickt – nur steckt dieser Text
selten im PDF, das man herunterladen kann. Das PDF enthält dann nichts als Bilder, und der Fraktur-Korrektor
schlägt zu Recht vor, den Text neu zu erkennen. Der Text der Bibliothek ist aber oft gut und lohnt die Mühe,
ihn zu holen. Er kommt in einem von zwei Formaten: **hOCR** (Dateien mit der Endung `.html` oder `.hocr`) oder
**ALTO** (`.xml`), jeweils eine Datei je Seite, und beide bringen mit, wo jede Zeile im Bild steht.

Wo man ihn findet, ist von Bibliothek zu Bibliothek verschieden: im Viewer unter „Volltext“ oder „OCR“, in
einer Schnittstelle, oder auf Nachfrage bei der Bibliothek. Die Bayerische Staatsbibliothek etwa gibt ihn je
Seite unter `https://api.digitale-sammlungen.de/ocr/<Kennung>/<Seite>` heraus; die Kennung (`bsb…`) steht auf dem
Deckblatt des PDF (Stand September 2026). Das Programm lädt nichts aus dem Internet – die Dateien holen Sie
selbst und legen sie in einen Ordner.

Dann geht es so:

1. Das PDF wie gewohnt einlesen (Tesseract oder, wenn das PDF Text enthält, den übernehmen). Dieser Text ist das
   Gerüst, an dem die Seiten der Bibliothek wiedererkannt werden.
2. In der Bibliothek beim Buch **Erkannten Text einlesen** wählen und auf den Ordner mit den hOCR- oder
   ALTO-Dateien zeigen.

Die Seiten finden sich am Wortlaut (siehe oben) – darum stört es nicht, dass das PDF vorn ein Deckblatt der
Bibliothek trägt, das in ihren Textdateien nicht vorkommt. Sind die Bilder der Bibliothek dieselben wie im PDF,
passen auch die Zeilenkästchen; das Buch trägt danach das Kennzeichen **Bibliothek**.

### Wenn schon Korrekturen im Buch stecken

Dann warnt das Programm: Der neue Text enthält Ihre Arbeit nicht. Sie haben die Wahl, ihn
trotzdem in dieses Buch zu übernehmen oder daneben ein neues anzulegen – die Seitenbilder kommen dabei mit.
Die bisherige Fassung wird in jedem Fall zuerst gesichert: als `vorher-<Datum>.zip` im Buchordner. Über den
Knopf **Frühere Fassung** holen Sie sie jederzeit zurück – und weil auch das Zurückholen vorher sichert, kommen
Sie ebenso wieder vorwärts. Gefällt Ihnen ein Import nicht, ist das der Weg zurück; Sie müssen nichts noch
einmal einlesen oder erkennen lassen.

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
| `quellen.json` | wie das Bild jeder Seite ursprünglich hieß – damit ein späterer Transkribus-Export sich zuordnen lässt |
| `vorher-….zip` | Sicherung der Textfassung, die ein übernommener Transkribus-Text ersetzt hat |

Die Textdateien dürfen Sie auch mit einem anderen Editor bearbeiten, sogar während das Programm läuft.
Ändern Sie dabei nur nicht die Zahl der Zeilen einer Seite, sonst passt die Zuordnung zum Bild nicht mehr.

## Ein Buch aus der Liste entfernen

Das ✕ rechts entfernt nur den Eintrag aus der Bibliothek. Die Dateien bleiben unangetastet.
