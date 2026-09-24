# Programm installieren

Der Fraktur-Korrektor ist ein fertiges Programm: herunterladen, doppelklicken, loslegen. Sie brauchen **nichts
weiter zu installieren** – die Texterkennung (Tesseract) und die Wörterbücher sind schon dabei (unter Linux
kommt Tesseract aus dem Paketmanager, siehe unten), und Doppelseiten teilen oder schiefe Seiten geraderichten kann
das Programm selbst. Nur für besonders schwierige Vorlagen gibt es das freie Zusatzprogramm ScanTailor, das Sie
bei Bedarf dazuholen: [Werkzeuge installieren](install-tools.md).

Alle Fassungen liegen auf der [Seite der Veröffentlichungen](https://github.com/Josi-create/fraktur-korrektor/releases/latest).

## Windows

1. **Herunterladen:**
   [Fraktur-Korrektor_Setup.exe](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor_Setup.exe)
2. Die heruntergeladene Datei doppelklicken.
3. Windows zeigt beim ersten Mal **„Der Computer wurde durch Windows geschützt“**. Das heißt nicht, dass etwas
   nicht stimmt: Die Meldung erscheint bei jedem Programm, das noch wenige Menschen heruntergeladen haben.
   Klicken Sie auf **Weitere Informationen** und dann auf **Trotzdem ausführen**.

   <!-- Platz für ein Bildschirmfoto der SmartScreen-Meldung -->
4. Dem Assistenten folgen; die Vorgaben können Sie übernehmen. Das Programm wird in Ihren Benutzerordner
   installiert, darum fragt Windows nicht nach einem Administratorkennwort.
5. Fertig. Der Fraktur-Korrektor steht im **Startmenü** und auf dem Schreibtisch.

Es gibt auch eine Fassung ohne Installation: die Datei `Fraktur-Korrektor-v….-win64.zip` entpacken und darin
`Fraktur-Korrektor.exe` doppelklicken. Praktisch für einen USB-Stick.

## Mac

1. **Welchen Mac haben Sie?** Apfelmenü → *Über diesen Mac*. Steht dort bei „Chip“ etwas mit **Apple M**,
   brauchen Sie die Fassung `arm64`; steht dort **Intel**, die Fassung `x86_64`.
2. **Herunterladen:**
   [für Apple Silicon (M1–M4)](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-arm64.dmg)
   · [für Intel](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-x86_64.dmg)
3. Die geladene `.dmg`-Datei doppelklicken. Es öffnet sich ein Fenster mit dem Programmsymbol und dem Ordner
   *Programme*. **Ziehen Sie das Symbol auf den Ordner Programme.**

   <!-- Platz für ein Bildschirmfoto des DMG-Fensters -->
4. Das Fenster schließen, die `.dmg` auswerfen (Klick auf das Auswurfzeichen in der Seitenleiste des Finders).
5. Im Ordner *Programme* den **Fraktur-Korrektor** doppelklicken.

Der Mac braucht macOS 15 (Sequoia) oder neuer.

## Linux

Stand September 2026. Die Linux-Fassung ist ein **AppImage**: eine einzige Datei, die ohne Installation läuft.
Sie ist für gewöhnliche PCs (x86_64) gebaut und braucht eine Distribution ab Ubuntu 22.04, Debian 12 oder Fedora 36.

1. **Herunterladen:**
   [Fraktur-Korrektor-linux-x86_64.AppImage](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-linux-x86_64.AppImage)
2. Die Datei **ausführbar machen**: im Dateimanager rechte Maustaste → *Eigenschaften* → Reiter *Berechtigungen*
   → Haken bei *Datei als Programm ausführen* (die Bezeichnungen weichen je nach Oberfläche etwas ab). Im
   Terminal geht es mit `chmod +x Fraktur-Korrektor-linux-x86_64.AppImage`.
3. Die Datei doppelklicken. Es öffnet sich ein kleines Fenster mit den Knöpfen *Im Browser öffnen* und
   *Beenden*, und der Browser zeigt die Bibliothek.
4. **Texterkennung nachrüsten** – nur nötig, wenn Sie PDFs oder Bilder einlesen wollen, für die es noch keinen
   Text gibt. Sie kommt aus dem Paketmanager Ihrer Distribution, im Terminal:

       sudo apt install tesseract-ocr tesseract-ocr-deu      # Ubuntu, Debian, Mint
       sudo dnf install tesseract tesseract-langpack-deu     # Fedora

   Das Frakturmodell lädt das Programm beim ersten Einlesen selbst nach (rund 10 MB, in Ihren Benutzerordner).
   Ob alles da ist, zeigt *Öffnen … → Werkzeuge* in der Bibliothek.

**Es startet nicht?** Auf manchen Systemen fehlt die Unterstützung für das Einhängen von AppImages (FUSE). Dann
hilft im Terminal `./Fraktur-Korrektor-linux-x86_64.AppImage --appimage-extract-and-run`, oder Sie nehmen die
Fassung `Fraktur-Korrektor-v….-linux-x86_64.tar.gz` von der Seite der Veröffentlichungen: entpacken und darin
`Fraktur-Korrektor` doppelklicken.

## Der erste Start

Es geht ein Fenster Ihres Browsers auf, und darin steht die Bibliothek – der Browser ist das Fenster des
Programms. Mit **Öffnen …** zeigen Sie dem Programm Ihr erstes Buch; wie das geht, steht unter
[Ein Buch öffnen](add-book.md).

Das Programm läuft nur auf Ihrem Rechner und überträgt nichts ins Internet.

**Beenden:** auf dem Mac über das Symbol im Dock (rechte Maustaste → *Beenden*) oder das kleine Buchsymbol
oben in der Menüleiste; unter Windows über das Symbol im Infobereich der Taskleiste (unten rechts, gegebenenfalls
hinter dem Pfeil `^`); unter Linux über den Knopf *Beenden* in dem kleinen Fenster. Das Fenster im Browser zu
schließen genügt nicht – das Programm läuft dann weiter.

**Es geht kein Fenster auf?** Öffnen Sie Ihren Browser und geben Sie <http://localhost:8765> ein.

## Auf den neuesten Stand bringen

Neue Fassung herunterladen und wie oben installieren, auf dem Mac also erneut in den Ordner *Programme* ziehen
und das Ersetzen bestätigen. Ihre Bücher und Einstellungen bleiben unangetastet.

## Wo liegen meine Sachen?

| Was | Wo |
|---|---|
| eingelesene Bücher | Ordner `Fraktur-Korrektor` in Ihrem Benutzerordner |
| Einstellungen, Liste der Bücher | Ordner `.fraktur-korrektor` in Ihrem Benutzerordner (versteckt) |
| das Programm selbst | Windows: `Programme\Fraktur-Korrektor` · Mac: `Programme/Fraktur-Korrektor.app` · Linux: die AppImage-Datei, wo Sie sie abgelegt haben |

Sichern Sie von Zeit zu Zeit den Ordner `Fraktur-Korrektor` – darin steckt Ihre ganze Arbeit.

## Wieder entfernen

**Windows:** *Einstellungen → Apps → Installierte Apps → Fraktur-Korrektor → Deinstallieren*.
**Mac:** die `Fraktur-Korrektor.app` aus dem Ordner *Programme* in den Papierkorb ziehen.
**Linux:** die AppImage-Datei löschen.

Ihre Bücher bleiben dabei erhalten; löschen Sie die beiden oben genannten Ordner von Hand, wenn Sie auch die
loswerden möchten.
