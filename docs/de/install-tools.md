# Werkzeuge installieren

**Haben Sie den Fraktur-Korrektor [installiert](install.md), ist alles Nötige schon dabei:** die Texterkennung
Tesseract mit den Modellen für Fraktur und Antiqua wird mitgeliefert. Diese Seite brauchen Sie nur, wenn

- Sie schwierige Scans mit **ScanTailor** aufbereiten möchten – das ist ein eigenes Programm, oder
- Sie den Fraktur-Korrektor aus dem Quelltext starten (`python server.py`); dann fehlt Tesseract.

| Programm | Wozu | Nötig? |
|---|---|---|
| **Tesseract** | Texterkennung: [PDF oder Bilder einlesen](pdf-import.md) | im fertigen Programm enthalten |
| **ScanTailor Advanced** | schlechte Scans aufbereiten (Doppelseiten trennen, geraderichten, entzerren) | nur bei schwierigen Vorlagen |

Der Fraktur-Korrektor findet beide Programme von selbst, wenn sie am üblichen Ort installiert sind. Beim Öffnen
eines PDF zeigt das Fenster, was gefunden wurde.

## Tesseract – nur beim Start aus dem Quelltext

**Windows**

1. Laden Sie das Installationsprogramm der Universitätsbibliothek Mannheim herunter:
   <https://github.com/UB-Mannheim/tesseract/wiki> (die Datei heißt etwa `tesseract-ocr-w64-setup-….exe`).
2. Doppelklick, die Fragen mit *Weiter* bestätigen. Den vorgeschlagenen Ordner
   (`C:\Program Files\Tesseract-OCR`) beibehalten.
3. Fraktur-Korrektor neu starten.

**Mac**

1. Falls noch nicht vorhanden, den Paketmanager [Homebrew](https://brew.sh/) installieren (die Startseite
   zeigt den einen Befehl, den man ins Programm *Terminal* kopiert).
2. Im Terminal eingeben: `brew install tesseract tesseract-lang`
3. Fraktur-Korrektor neu starten.

**Linux:** `sudo apt install tesseract-ocr tesseract-ocr-deu` (Debian/Ubuntu) bzw. das Paket Ihrer Distribution.

Das **Fraktur-Modell** `frak2021` der UB Mannheim (5 MB) ist im fertigen Programm enthalten. Beim Start aus dem
Quelltext lädt der Fraktur-Korrektor es beim ersten Einlesen selbst herunter und legt es unter
`~/.fraktur-korrektor/tessdata` ab. Sind bereits Fraktur-Modelle installiert (`deu_latf`, `deu_frak`, `frk`,
`Fraktur`), benutzt er diese.

## ScanTailor Advanced

**Windows**

1. Von <https://github.com/ScanTailor-Advanced/scantailor-advanced/releases> die neueste Datei herunterladen,
   deren Name auf `x64.zip` endet (neuere Versionen ohne ZIP-Datei sind nur für Linux).
2. Die ZIP-Datei entpacken (Rechtsklick → *Alle extrahieren*), zum Beispiel nach `Dokumente\ScanTailor`.
   Eine Installation ist nicht nötig; das Programm heißt `scantailor.exe`.
3. Im Fraktur-Korrektor ein PDF öffnen; im Fenster erscheint dann **Programm zeigen …** – darauf klicken und diese
   `scantailor.exe` auswählen. Das merkt sich der Fraktur-Korrektor.

**Mac:** im Terminal `brew install yb85/homebrew-tap/scantailor-advanced`
(Projekt: <https://github.com/yb85/scantailor-advanced-osx>; Homebrew siehe oben bei Tesseract).

**Linux:** `.deb`-Paket oder AppImage von der oben genannten Seite, oder das Paket Ihrer Distribution.

## Wenn ein Programm nicht gefunden wird

Beim Öffnen eines PDF oder Bilderordners zeigt das Fenster, welche Programme gefunden wurden. Klicken Sie neben der
Meldung auf **Programm zeigen …** und wählen Sie
die Programmdatei (`tesseract.exe` bzw. `scantailor.exe`). Von Hand geht es auch: Der Pfad steht in der Datei
`~/.fraktur-korrektor/config.json` (unter Windows: `C:\Users\<Name>\.fraktur-korrektor\config.json`):

    {
      "tesseract": "D:\\Programme\\Tesseract\\tesseract.exe",
      "scantailor": "D:\\Programme\\ScanTailor\\scantailor.exe"
    }

In derselben Datei lässt sich mit `"buecher"` der Ordner festlegen, in dem neue Bücher angelegt werden
(sonst `Fraktur-Korrektor` in Ihrem Benutzerordner), und mit `"dic"` ein anderes Wörterbuch.
