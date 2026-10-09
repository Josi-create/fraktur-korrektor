# Werkzeuge installieren

*Stand: 9. Oktober 2026.*

**Haben Sie den Fraktur-Korrektor unter Windows oder auf dem Mac [installiert](install.md), ist alles Nötige schon
dabei:** die Texterkennung Tesseract (Fassung 5.5.3) mit den Modellen für Fraktur und Antiqua wird mitgeliefert.
Diese Seite brauchen Sie nur, wenn

- Sie gewölbte oder fleckige Scans mit **ScanTailor** aufbereiten möchten – das ist ein eigenes Programm
  (Doppelseiten teilen und schiefe Seiten geraderichten kann der Fraktur-Korrektor selbst:
  [Scans vorbereiten](pdf-import.md)), oder
- Sie unter **Linux** arbeiten – dort kommt Tesseract aus dem Paketmanager –, oder
- Sie den Fraktur-Korrektor aus dem Quelltext starten (`python server.py`); dann fehlt Tesseract.

| Programm | Wozu | Nötig? |
|---|---|---|
| **Tesseract** | Texterkennung: [PDF oder Bilder einlesen](pdf-import.md) | unter Windows und macOS im fertigen Programm enthalten; unter Linux selbst installieren |
| **ScanTailor Advanced** | schlechte Scans aufbereiten (Wölbung entzerren, Flecken und Ränder entfernen) | nur bei schwierigen Vorlagen; Doppelseiten und Schieflage erledigt das Programm selbst |

Der Fraktur-Korrektor findet beide Programme von selbst, wenn sie am üblichen Ort installiert sind. Beim Öffnen
eines PDF zeigt das Fenster, was gefunden wurde; ebenso die Startseite, solange die Bibliothek noch leer ist.

## Tesseract – nur unter Linux und beim Start aus dem Quelltext

**Windows**

1. Laden Sie das Installationsprogramm der Universitätsbibliothek Mannheim herunter:
   <https://github.com/UB-Mannheim/tesseract/wiki> (die Datei heißt etwa
   `tesseract-ocr-w64-setup-5.5.3.20260724.exe`).
2. Doppelklick, die Fragen mit *Weiter* bestätigen. Den vorgeschlagenen Ordner
   (`C:\Program Files\Tesseract-OCR`) beibehalten.
3. Fraktur-Korrektor neu starten.

**Mac**

1. Falls noch nicht vorhanden, den Paketmanager [Homebrew](https://brew.sh/) installieren (die Startseite
   zeigt den einen Befehl, den man ins Programm *Terminal* kopiert).
2. Im Terminal eingeben: `brew install tesseract tesseract-lang`
3. Fraktur-Korrektor neu starten.

`tesseract-lang` bringt das Antiqua-Modell `deu` mit, dazu das ältere Fraktur-Modell `frk`; frak2021 lädt der
Fraktur-Korrektor trotzdem dazu (siehe unten).

**Linux:** `sudo apt install tesseract-ocr tesseract-ocr-deu` (Debian, Ubuntu, Mint) bzw.
`sudo dnf install tesseract tesseract-langpack-deu` (Fedora) oder das Paket Ihrer Distribution.

Das **Fraktur-Modell** `frak2021` der UB Mannheim (5 MB) ist im fertigen Programm für Windows und macOS enthalten.
Unter Linux und beim Start aus dem Quelltext lädt der Fraktur-Korrektor es beim ersten Einlesen selbst herunter
(dafür braucht es einmal eine Internetverbindung) und legt es unter `~/.fraktur-korrektor/tessdata` ab. Das gilt auch,
wenn schon ein älteres Fraktur-Modell installiert ist (`deu_latf`, `deu_frak`, `frk`, `Fraktur`) – frak2021 erkennt
besser. Nur wenn das Herunterladen nicht klappt, nimmt er das ältere. Welches Modell gerade da ist, zeigt das Fenster
beim Öffnen eines PDF („Fraktur-Modell: …“).

## ScanTailor Advanced

**Windows**

1. Von <https://github.com/ScanTailor-Advanced/scantailor-advanced/releases> die neueste Datei herunterladen,
   deren Name auf `x64.zip` endet – derzeit `ScanTailor-Advanced-1.1.1x64.zip` von Version 1.1.1 (April 2026).
   Die neueren Versionen 1.2.0 und 1.2.1 gibt es nur für Linux.
2. Die ZIP-Datei entpacken (Rechtsklick → *Alle extrahieren*), zum Beispiel nach `Dokumente\ScanTailor`.
   Eine Installation ist nicht nötig; das Programm heißt `scantailor.exe`.
3. Im Fraktur-Korrektor ein PDF öffnen; im Fenster steht dann „ScanTailor ist nicht installiert“ und daneben
   **Programm zeigen …** – darauf klicken und diese `scantailor.exe` auswählen. Das merkt sich der Fraktur-Korrektor.

**Mac:** Hier wird es unbequem – ein fertiges ScanTailor für den Mac gibt es vom Projekt selbst nicht (Stand
Oktober 2026 veröffentlicht es nur Dateien für Windows und Linux).

- Der Weg über Homebrew (`brew install yb85/homebrew-tap/scantailor-advanced`, Version 1.0.19) lädt kein
  fertiges Programm, sondern **baut es auf Ihrem Rechner**. Auf Macs mit Apple-Chip kommt die Programmbibliothek
  Qt dabei fertig mit; auf Intel-Macs gibt es für Qt und seine 38 Bestandteile keine fertigen Pakete mehr – dann
  wird alles gebaut, und das dauert Stunden.
- **Empfohlen:** ein älteres, aber fertiges Programm – *ScanTailor Advanced 1.0.18* von 2022, gebaut von yb85:
  [Scantailor-Advanced-v1.0.18-20220508-macos12.dmg](https://github.com/yb85/scantailor-advanced-osx/releases/download/1.0.18/Scantailor-Advanced-v1.0.18-20220508-macos12.dmg)
  (29 MB, [Übersicht](https://github.com/yb85/scantailor-advanced-osx/releases/tag/1.0.18)). Es hat im Test auf
  macOS 26 einwandfrei gearbeitet. Ziehen Sie *ScanTailor (Advanced)* aus dem Fenster der DMG-Datei in den Ordner
  *Programme* – dort findet es der Fraktur-Korrektor von selbst. Zwei Dinge sind zu beachten:
    - Es ist für **Intel-Macs** gebaut. Auf Macs mit Apple-Chip läuft es nur über *Rosetta*, das macOS beim
      ersten Start selbst anbietet.
    - Es ist **nicht signiert**, darum verweigert macOS zunächst den Start. So erlauben Sie ihn: Programm
      doppelklicken, Meldung wegklicken, dann *Apfelmenü → Systemeinstellungen → Datenschutz & Sicherheit*,
      unten bei *Sicherheit* auf **Dennoch öffnen** und Ihr Anmeldepasswort eingeben. Der Knopf erscheint nur
      etwa eine Stunde lang nach dem Versuch.

  (Älter und für den Notfall ebenfalls zu haben: *ScanTailor Universal 0.2.12* von 2021,
  <https://github.com/trufanov-nok/scantailor-universal/releases/tag/0.2.12>.)

**Für ein einzelnes Buch lohnt der Aufwand selten.** Doppelseiten und schiefe Seiten – der häufigste Fall – erledigt
der Fraktur-Korrektor selbst ([Scans vorbereiten](pdf-import.md)). Ist die Vorlage darüber hinaus so schlecht, dass
ScanTailor nötig wäre, kommen Sie mit [Transkribus](transkribus.md) meist schneller ans Ziel.

**Linux:** `.deb`-Paket oder AppImage von der oben genannten Seite (Version 1.2.1 vom Mai 2026), oder das Paket
Ihrer Distribution.

## Wenn ein Programm nicht gefunden wird

Beim Öffnen eines PDF zeigt das Fenster, welche Programme gefunden wurden (bei einem Bilderordner nur Tesseract);
ebenso die Startseite, solange die Bibliothek noch leer ist. Klicken Sie neben der Meldung auf
**Programm zeigen …** und wählen Sie die Programmdatei (`tesseract.exe` bzw. `scantailor.exe`, auf dem Mac das
Programm *ScanTailor (Advanced)*). Von Hand geht es auch: Der Pfad steht in der Datei
`~/.fraktur-korrektor/config.json` (unter Windows: `C:\Users\<Name>\.fraktur-korrektor\config.json`):

    {
      "tesseract": "D:\\Programme\\Tesseract\\tesseract.exe",
      "scantailor": "D:\\Programme\\ScanTailor\\scantailor.exe"
    }

In derselben Datei lässt sich mit `"buecher"` der Ordner festlegen, in dem neue Bücher angelegt werden
(sonst `Fraktur-Korrektor` in Ihrem Benutzerordner), und mit `"dic"` ein anderes Wörterbuch.
