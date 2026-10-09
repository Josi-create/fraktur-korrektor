# Programm installieren

Der Fraktur-Korrektor ist ein fertiges Programm: herunterladen, doppelklicken, loslegen. Sie brauchen **nichts
weiter zu installieren** – die Texterkennung (Tesseract) und die Wörterbücher sind schon dabei (unter Linux
kommt Tesseract aus dem Paketmanager, siehe unten), und Doppelseiten teilen oder schiefe Seiten geraderichten kann
das Programm selbst. Nur für besonders schwierige Vorlagen gibt es das freie Zusatzprogramm ScanTailor, das Sie
bei Bedarf dazuholen: [Werkzeuge installieren](install-tools.md).

Alle Fassungen liegen auf der [Seite der Veröffentlichungen](https://github.com/Josi-create/fraktur-korrektor/releases/latest).

Die Anleitung beschreibt Windows 11 und macOS, Stand Oktober 2026. Unter Windows 10 sehen die Fenster etwas anders
aus, die Schritte sind dieselben.

## Windows

1. **Herunterladen:** Klicken Sie auf
   [Fraktur-Korrektor_Setup.exe](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor_Setup.exe).
   Der Browser legt die Datei in den Ordner *Downloads*.
2. **Falls der Browser die Datei zurückhält:** Microsoft Edge meldet manchmal, die Datei werde „nicht häufig
   heruntergeladen“. Klicken Sie in der Liste der Downloads (oben rechts) neben der Datei auf die drei Punkte
   **…**, dann auf **Beibehalten**; im nächsten Fenster auf **Mehr anzeigen** und **Trotzdem beibehalten**.

   <!-- Bildschirmfoto: win-edge-download.png – Microsoft Edge (deutsche Oberfläche) direkt nach dem Herunterladen der Fraktur-Korrektor_Setup.exe: die Downloadliste oben rechts mit der Warnung „wird nicht häufig heruntergeladen“, das Menü der drei Punkte aufgeklappt, „Beibehalten“ sichtbar -->
3. Klicken Sie in der Liste der Downloads auf die Datei (oder doppelklicken Sie sie im Ordner *Downloads*).
4. Beim ersten Mal erscheint ein blaues Fenster: **„Der Computer wurde durch Windows geschützt“**. Das heißt
   nicht, dass etwas nicht stimmt: Die Meldung erscheint bei jedem Programm, das noch wenige Menschen
   heruntergeladen haben. Klicken Sie auf den unterstrichenen Text **Weitere Informationen**.

   <!-- Bildschirmfoto: win-smartscreen.png – Windows 11 (deutsch), das blaue Fenster „Der Computer wurde durch Windows geschützt“ gleich nach dem Doppelklick auf Fraktur-Korrektor_Setup.exe; der Link „Weitere Informationen“ ist zu sehen, unten nur der Knopf „Nicht ausführen“ -->
5. Jetzt steht unten ein zweiter Knopf. Klicken Sie auf **Trotzdem ausführen**. (Als Herausgeber steht dort
   „Unbekannter Herausgeber“ – das Programm ist noch nicht digital unterschrieben.)

   <!-- Bildschirmfoto: win-smartscreen-2.png – dasselbe blaue Fenster nach dem Klick auf „Weitere Informationen“: App „Fraktur-Korrektor_Setup.exe“, Herausgeber „Unbekannter Herausgeber“, unten die Knöpfe „Trotzdem ausführen“ und „Nicht ausführen“ -->
6. Das Installationsprogramm fragt nach der **Sprache** – Deutsch ist vorgewählt, klicken Sie auf **OK**.
7. Es fragt, ob es **nur für Sie oder für alle Benutzer** installieren soll. Klicken Sie auf **Installation nur
   für Sie (empfohlen)**. Dann fragt Windows nicht nach einem Administratorkennwort.

   <!-- Bildschirmfoto: win-installer.png – das Fenster „Installationsmodus auswählen“ des Fraktur-Korrektor-Setups (deutsch) mit den beiden Knöpfen „Installation für alle Benutzer“ und „Installation nur für Sie (empfohlen)“ -->
8. Die **Lizenzvereinbarung** (die GPL, eine freie Lizenz): **Ich akzeptiere die Vereinbarung** anklicken, dann
   **Weiter**.
9. Den vorgeschlagenen **Ziel-Ordner** mit **Weiter** übernehmen.
10. Bei *Zusätzliche Aufgaben* ist **Desktop-Symbol erstellen** angehakt – so lassen, **Weiter**.
11. **Installieren** klicken. Nach wenigen Sekunden ist es fertig.
12. Im letzten Fenster ist **Fraktur-Korrektor starten** angehakt. Klicken Sie auf **Fertigstellen** – das
    Programm startet, siehe [Der erste Start](#der-erste-start).

Der Fraktur-Korrektor steht danach im **Startmenü** und auf dem Desktop.

Es gibt auch eine Fassung ohne Installation: die Datei `Fraktur-Korrektor-v….-win64.zip` von der Seite der
Veröffentlichungen laden, mit rechter Maustaste → *Alle extrahieren …* auspacken und darin
`Fraktur-Korrektor.exe` doppelklicken. Praktisch für einen USB-Stick. Auch hier erscheint beim ersten Start die
blaue Meldung von oben.

## Mac

1. **Welchen Mac haben Sie?** Klicken Sie oben links auf das Apfelsymbol  und dann auf **Über diesen Mac**.
   Steht dort eine Zeile **Chip** mit „Apple M…“ (M1, M2, M3 …), hat Ihr Mac einen Apple-Chip. Steht dort eine
   Zeile **Prozessor** mit „Intel“, ist es ein Intel-Mac.

   <!-- Bildschirmfoto: mac-chip.png – das Fenster „Über diesen Mac“ (deutsche Oberfläche) eines Macs mit Apple-Chip, die Zeile „Chip: Apple M…“ gut lesbar; Seriennummer unkenntlich machen -->
2. **Herunterladen** – die passende Fassung anklicken:
   [für Macs mit Apple-Chip (M1 und neuer)](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-arm64.dmg)
   · [für Macs mit Intel-Prozessor](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-x86_64.dmg).
   Die Datei landet im Ordner *Downloads*; ihr Name endet auf `.dmg` – das ist eine Art Paket, das der Mac
   beim Doppelklick wie ein Laufwerk öffnet.
3. Die geladene Datei doppelklicken. Es öffnet sich ein Fenster mit dem Symbol des Fraktur-Korrektors und dem
   Ordner *Programme* (auf einem englisch eingestellten Mac heißt er *Applications*). **Ziehen Sie das Symbol
   mit gedrückter Maustaste auf den Ordner Programme** und lassen Sie los.

   <!-- Bildschirmfoto: mac-dmg.png – das Finder-Fenster, das sich nach dem Doppelklick auf Fraktur-Korrektor-macos-arm64.dmg öffnet: links das Programmsymbol „Fraktur-Korrektor“, rechts der Ordner „Programme“/„Applications“; am besten mitten im Ziehen, mit dem halbdurchsichtigen Symbol über dem Ordner -->
4. Das Fenster schließen. In der Seitenleiste des Finders steht noch „Fraktur-Korrektor“ mit einem kleinen
   Auswurfzeichen ⏏ daneben – darauf klicken. Die `.dmg`-Datei im Ordner *Downloads* können Sie danach löschen.
5. Im Finder den Ordner *Programme* öffnen und den **Fraktur-Korrektor** doppelklicken.
6. Beim ersten Start fragt der Mac, ob Sie das aus dem Internet geladene Programm wirklich öffnen möchten. Das
   Programm ist bei Apple geprüft und beglaubigt; klicken Sie auf **Öffnen**. Die Frage kommt nur dieses eine Mal.

   <!-- Bildschirmfoto: mac-gatekeeper.png – die Rückfrage von macOS (deutsche Oberfläche) beim ersten Doppelklick auf den Fraktur-Korrektor im Ordner Programme: „„Fraktur-Korrektor“ ist … aus dem Internet geladen … wirklich öffnen?“ mit den Knöpfen „Abbrechen“ und „Öffnen“ (bitte den genauen Wortlaut mitteilen, damit der Text ihn übernehmen kann) -->

Fragt der Mac später, ob der Fraktur-Korrektor auf einen Ordner (etwa *Dokumente*) zugreifen oder Ihren Browser
steuern darf, klicken Sie auf **Erlauben** bzw. **OK**: Das braucht das Programm, um Ihre Bücher zu öffnen und das
schon offene Browserfenster nach vorn zu holen.

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
   *Fraktur-Korrektor beenden*, und der Browser zeigt die Bibliothek.
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

![Die Bibliothek beim ersten Start](img/bibliothek-start.png)

Noch kein eigenes Buch zur Hand? Mit **Beispielbuch öffnen** probieren Sie alles an acht Seiten aus Goethes *Faust* aus – Schritt für Schritt unter [Erste Schritte](first-steps.md).

Das Programm läuft nur auf Ihrem Rechner und überträgt nichts ins Internet.

**Beenden:** Das Fenster im Browser zu schließen genügt nicht – das Programm läuft dann weiter. So beenden Sie es:

- **Windows:** Unten rechts in der Taskleiste, neben der Uhr, steht das Symbol des Fraktur-Korrektors. Sehen Sie
  es nicht, klicken Sie zuerst auf den kleinen Pfeil **^** daneben. Mit der rechten Maustaste auf das Symbol
  klicken und **Fraktur-Korrektor beenden** wählen. (Ein Doppelklick auf das Symbol holt das Browserfenster
  zurück.)

  <!-- Bildschirmfoto: win-infobereich.png – Windows 11 (deutsch), Taskleiste unten rechts: der Pfeil „^“ ist aufgeklappt, mit der rechten Maustaste auf das Fraktur-Korrektor-Symbol geklickt, das Menü „Im Browser öffnen“ / „Fraktur-Korrektor beenden“ ist offen -->
- **Mac:** Mit der rechten Maustaste auf das Symbol im Dock klicken und **Beenden** wählen – oder oben in der
  Menüleiste auf das kleine Buchsymbol klicken und **Fraktur-Korrektor beenden** wählen.
- **Linux:** im kleinen Fenster auf **Fraktur-Korrektor beenden** klicken.

**Es geht kein Fenster auf?** Öffnen Sie Ihren Browser und geben Sie <http://localhost:8765> ein.

## Auf den neuesten Stand bringen

Zuerst das laufende Programm beenden (siehe oben). Dann die neue Fassung herunterladen und genauso installieren
wie beim ersten Mal; unter Windows einfach über die alte Fassung, auf dem Mac erneut in den Ordner *Programme*
ziehen und **Ersetzen** bestätigen. Ihre Bücher und Einstellungen bleiben unangetastet.

## Wo liegen meine Sachen?

| Was | Wo |
|---|---|
| eingelesene Bücher | Ordner `Fraktur-Korrektor` in Ihrem Benutzerordner |
| Einstellungen, Liste der Bücher | Ordner `.fraktur-korrektor` in Ihrem Benutzerordner (versteckt) |
| das Programm selbst | Windows: `AppData\Local\Programs\Fraktur-Korrektor` in Ihrem Benutzerordner (bei „für alle Benutzer“: `Programme\Fraktur-Korrektor`) · Mac: `Programme/Fraktur-Korrektor.app` · Linux: die AppImage-Datei, wo Sie sie abgelegt haben |

Sichern Sie von Zeit zu Zeit den Ordner `Fraktur-Korrektor` – darin steckt Ihre ganze Arbeit.

## Wieder entfernen

**Windows:** *Start → Einstellungen → Apps → Installierte Apps*, beim Fraktur-Korrektor auf die drei Punkte **…**
klicken → **Deinstallieren**.
**Mac:** die `Fraktur-Korrektor.app` aus dem Ordner *Programme* in den Papierkorb ziehen.
**Linux:** die AppImage-Datei löschen.

Ihre Bücher bleiben dabei erhalten; löschen Sie die beiden oben genannten Ordner von Hand, wenn Sie auch die
loswerden möchten.
