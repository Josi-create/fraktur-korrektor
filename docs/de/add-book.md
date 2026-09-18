# Ein Buch hinzufügen

Die Startseite des Programms ist die **Bibliothek**. Sie zeigt alle Bücher, die Sie schon einmal geöffnet
haben, das zuletzt benutzte zuoberst. Ein Klick auf ein Buch öffnet es an der Stelle, an der Sie aufgehört
haben.

## Einen Export aus Transkribus importieren

1. Exportieren Sie in Transkribus Ihr Dokument. Wichtig ist das Häkchen bei **PAGE XML** (bei „Transkribus
   Document“). Wenn Sie zusätzlich **Bilder exportieren** anhaken, übernimmt der Fraktur-Korrektor die
   Seitenbilder gleich mit. Sie erhalten eine ZIP-Datei.
2. Klicken Sie in der Bibliothek auf **Transkribus-Export importieren …**
3. Wählen Sie die ZIP-Datei (**ZIP-Datei wählen …**). Entpacken müssen Sie sie nicht.
4. Geben Sie dem Buch einen Titel – oder lassen Sie das Feld leer, dann gilt der Titel aus Transkribus.
5. Nur wenn der Export keine Bilder enthält: Geben Sie den Ordner an, in dem die Seitenbilder liegen
   (PNG oder JPG, in der Reihenfolge der Seiten).
6. **Importieren.** Das Programm legt einen neuen Buchordner an und zeigt danach **Buch öffnen**.

Beim Import erkennt das Programm Kopfzeilen (Seitenzahlen) und trennt Fußnoten vom Haupttext. Wo das nicht
stimmt, korrigieren Sie es beim Lesen mit der Taste `F` (siehe [Bedienung](usage.md)).

Ein Import überschreibt nie ein vorhandenes Buch. Gibt es den Titel schon, entsteht ein zweiter Ordner mit
dem Zusatz „(2)“.

## Einen vorhandenen Buchordner öffnen

**Buchordner öffnen …** zeigt den Ordner-Dialog Ihres Betriebssystems. Wählen Sie den Ordner, in dem die
Seitendateien `001.txt`, `002.txt`, … liegen.

## Was in einem Buchordner liegt

| Datei | Inhalt |
|---|---|
| `001.txt`, `002.txt`, … | der Text, eine Datei je Seite: optional `# Kopfzeile`, Haupttext, `---`, Fußnoten |
| `img/001.png` … | die Seitenbilder (PNG oder JPG) |
| `lines.json` | wo jede Textzeile im Seitenbild steht |
| `whitelist.txt` | Wörter, die Sie mit `F8` als richtig bestätigt haben |
| `lesezeichen.json` | Ihre Leseposition |
| `korrekturen.log` | Protokoll aller Änderungen |

Die Textdateien dürfen Sie auch mit einem anderen Editor bearbeiten, sogar während das Programm läuft.
Ändern Sie dabei nur nicht die Zahl der Zeilen einer Seite, sonst passt die Zuordnung zum Bild nicht mehr.

## Ein Buch aus der Liste entfernen

Das ✕ rechts entfernt nur den Eintrag aus der Bibliothek. Die Dateien bleiben unangetastet.
