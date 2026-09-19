# Programm installieren

Der Fraktur-Korrektor ist ein fertiges Programm: herunterladen, doppelklicken, loslegen. Sie brauchen **nichts
weiter zu installieren** – die Texterkennung (Tesseract) und die Wörterbücher sind schon dabei.

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

## Der erste Start

Es geht ein Fenster Ihres Browsers auf, und darin steht die Bibliothek – der Browser ist das Fenster des
Programms. Mit **Öffnen …** zeigen Sie dem Programm Ihr erstes Buch; wie das geht, steht unter
[Ein Buch öffnen](add-book.md).

Das Programm läuft nur auf Ihrem Rechner und überträgt nichts ins Internet.

**Beenden:** auf dem Mac über das Symbol im Dock (rechte Maustaste → *Beenden*) oder das kleine Buchsymbol
oben in der Menüleiste; unter Windows über das Symbol im Infobereich der Taskleiste (unten rechts, gegebenenfalls
hinter dem Pfeil `^`). Das Fenster im Browser zu schließen genügt nicht – das Programm läuft dann weiter.

**Es geht kein Fenster auf?** Öffnen Sie Ihren Browser und geben Sie <http://localhost:8765> ein.

## Auf den neuesten Stand bringen

Neue Fassung herunterladen und wie oben installieren, auf dem Mac also erneut in den Ordner *Programme* ziehen
und das Ersetzen bestätigen. Ihre Bücher und Einstellungen bleiben unangetastet.

## Wo liegen meine Sachen?

| Was | Wo |
|---|---|
| eingelesene Bücher | Ordner `Fraktur-Korrektor` in Ihrem Benutzerordner |
| Einstellungen, Liste der Bücher | Ordner `.fraktur-korrektor` in Ihrem Benutzerordner (versteckt) |
| das Programm selbst | Windows: `Programme\Fraktur-Korrektor` · Mac: `Programme/Fraktur-Korrektor.app` |

Sichern Sie von Zeit zu Zeit den Ordner `Fraktur-Korrektor` – darin steckt Ihre ganze Arbeit.

## Wieder entfernen

**Windows:** *Einstellungen → Apps → Installierte Apps → Fraktur-Korrektor → Deinstallieren*.
**Mac:** die `Fraktur-Korrektor.app` aus dem Ordner *Programme* in den Papierkorb ziehen.

Ihre Bücher bleiben dabei erhalten; löschen Sie die beiden oben genannten Ordner von Hand, wenn Sie auch die
loswerden möchten.
