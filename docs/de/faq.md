# Häufige Fragen und Fehlerbehebung

Hier stehen die Meldungen und Situationen, die am häufigsten Fragen aufwerfen – jeweils mit dem nächsten Schritt.
Was hier nicht steht, erklären die anderen Seiten der Hilfe; sie sind jeweils verlinkt.

## Start und Installation

**Windows meldet „Der Computer wurde durch Windows geschützt“.**
Das ist die übliche Warnung für Programme, die noch wenige Menschen heruntergeladen haben, kein Zeichen für ein
Problem. Klicken Sie auf *Weitere Informationen* und dann auf *Trotzdem ausführen* – siehe
[Programm installieren](install.md).

**Der Mac sagt, das Programm könne nicht geöffnet werden, weil der Entwickler nicht verifiziert werden kann.**
Bei der fertigen Fassung von der Veröffentlichungsseite sollte diese Meldung nicht erscheinen. Kommt sie doch (zum
Beispiel bei einer selbst gebauten Fassung): Meldung schließen, dann *Apfelmenü → Systemeinstellungen → Datenschutz &
Sicherheit*, unten bei *Sicherheit* auf **Dennoch öffnen**. Der Knopf erscheint nur in der Stunde nach dem
Startversuch. Denselben Weg brauchen Sie für ScanTailor, siehe [Werkzeuge installieren](install-tools.md).

**Windows fragt nach der Firewall-Freigabe.**
Beim gewöhnlichen Start fragt Windows nicht, denn das Programm ist dann nur auf Ihrem eigenen Rechner erreichbar.
Die Nachfrage kommt nur, wenn Sie es mit der Option `--lan` für andere Geräte im Heimnetz gestartet haben. Erlauben Sie
den Zugriff für *private Netzwerke*, sonst erreichen die anderen Geräte das Programm nicht. Ins Internet geht in
keinem Fall etwas – siehe [Über das Heimnetz mitlesen](usage.md).

**„Der Port 8765 ist belegt: ein anderes Programm benutzt ihn.“**
Das Programm braucht auf Ihrem Rechner eine Adresse, und die hat bereits ein anderes Programm. Prüfen Sie zuerst,
ob der Fraktur-Korrektor nicht schon läuft (Symbol im Infobereich der Taskleiste bzw. im Dock): Ein zweiter
Doppelklick startet ihn nicht noch einmal, sondern zeigt nur das Fenster wieder. Ist es ein anderes Programm,
beenden Sie es – oder starten Sie den Fraktur-Korrektor mit `--port <nummer>`, etwa `--port 8766`; die Adresse im
Browser lautet dann `http://localhost:8766`.

**Es geht kein Fenster auf.**
Öffnen Sie Ihren Browser und geben Sie <http://localhost:8765> ein. Das Programm läuft – der Browser ist nur sein
Fenster. Konnte es nicht starten, zeigt es stattdessen ein Meldungsfenster mit dem Grund.

**Ich habe das Browserfenster geschlossen – läuft das Programm noch?**
Ja. Beenden Sie es über das Symbol im Infobereich der Taskleiste (Windows) oder im Dock bzw. in der Menüleiste (Mac);
siehe [Programm installieren](install.md). Ein Doppelklick auf das Programm holt das Fenster jederzeit zurück.

**„Das Wörterbuch fehlt – der Ordner ‚dict‘ des Programms ist nicht vollständig.“**
Die Wörterbücher gehören zum Programm; ohne sie kann es keine Wörter prüfen. Installieren Sie das Programm noch
einmal. Beim Start aus dem Quelltext: den Ordner `dict/` wiederherstellen oder ein eigenes Hunspell-Wörterbuch mit
`--dic <pfad>` angeben (ohne die Endungen `.dic`/`.aff`).

## Öffnen und Einlesen

**„Die angegebene Datei bzw. der Ordner wurde nicht gefunden.“**
Der Pfad stimmt nicht mehr – die Datei wurde verschoben oder umbenannt, oder ein USB-Stick oder Netzlaufwerk ist nicht
angeschlossen. Suchen Sie die Datei mit dem Knopf *Datei wählen …* noch einmal heraus.

**In der Bibliothek steht bei einem Buch „Ordner nicht gefunden“.**
Der Buchordner liegt nicht mehr dort, wo das Programm ihn kennt. Liegt er auf einem Stick oder Netzlaufwerk, schließen
Sie es an. Haben Sie ihn verschoben: Eintrag mit dem ✕ aus der Liste nehmen und den Ordner am neuen Ort mit
**Öffnen …** wieder aufnehmen – die Dateien und Ihre Arbeit bleiben unangetastet.

**„In diesem Ordner liegen keine Seitendateien (001.txt, 002.txt, …).“**
Der Ordner ist kein Buchordner des Programms. Zeigen Sie mit **Öffnen …** stattdessen auf das PDF, die Bilder oder den
Transkribus-Export; das Programm erkennt selbst, was es ist, und legt daraus ein Buch an – siehe
[Ein Buch öffnen](add-book.md).

**„Darin war weder PAGE-XML noch hOCR, ALTO oder Text zu finden.“**
Der Export enthält nichts, was das Programm lesen kann. Aus Transkribus laden Sie das Ergebnis als **PAGE XML**
herunter (nur damit stehen die Zeilen später neben dem Bild) – siehe [Mit Transkribus arbeiten](transkribus.md).

**„Tesseract ist nicht installiert.“**
Im fertigen Programm ist die Texterkennung enthalten. Die Meldung erscheint beim Start aus dem Quelltext oder wenn
das Programm Tesseract nicht findet: Klicken Sie neben der Meldung auf *Programm zeigen …* und wählen Sie die
Programmdatei, oder installieren Sie Tesseract – siehe [Werkzeuge installieren](install-tools.md). Bücher, die schon
Text mitbringen (durchsuchbare PDFs, EPUB, Transkribus), lassen sich auch ohne Tesseract öffnen.

**„Das Fraktur-Modell konnte nicht heruntergeladen werden.“**
Im fertigen Programm ist das Modell dabei. Beim Start aus dem Quelltext lädt das Programm es beim ersten Einlesen
einmalig herunter (5 MB) und legt es in Ihrem Benutzerordner ab; dafür braucht es einmal eine Internetverbindung.
Stellen Sie die Verbindung her und versuchen Sie es noch einmal – danach geht es ohne.

**„Für PDF-Dateien fehlt das Python-Paket PyMuPDF.“**
Nur beim Start aus dem Quelltext: `pip install pymupdf` ausführen. Ordner mit Seitenbildern gehen auch ohne.

**„Mehr als 999 Seiten – bitte das Buch teilen.“**
Ein Buch hat im Programm höchstens 999 Seiten. Teilen Sie das PDF in zwei Teile (in jedem PDF-Programm möglich) und
lesen Sie beide als eigene Bücher ein.

**Die Ampel steht auf Rot.**
Der erkannte Text ist so schlecht, dass sich Korrigieren von Hand nicht lohnt. Meist liegt es an der Vorlage:
Doppelseiten, schiefe oder gewölbte Seiten. Lassen Sie die Scans vorbereiten und den Text neu erkennen, oder nehmen
Sie Transkribus – die Empfehlung unter der Ampel sagt, was in Ihrem Fall passt. Siehe
[PDF oder Bilder einlesen](pdf-import.md).

**Es sind zwei Buchseiten auf einem Bild, oder die Seiten sind schief.**
**Scans vorbereiten** beim Buch in der Bibliothek teilt Doppelseiten und richtet schiefe Seiten gerade, mit Vorschau der
Trennlinie. Das Ergebnis lassen Sie danach als neues Buch erkennen – siehe [PDF oder Bilder einlesen](pdf-import.md).

**Die Seitenbilder fehlen, es gibt nur Text.**
Klicken Sie beim Buch auf **Seitenbilder hinzufügen** und zeigen Sie auf den Bilderordner, das PDF oder ein anderes Buch,
das die Bilder schon hat – siehe [Ein Buch öffnen](add-book.md).

**„Das geht nur an dem Rechner, auf dem das Programm läuft.“**
Sie lesen über das Heimnetz von einem anderen Gerät aus mit. Bücher öffnen, einlesen oder vorbereiten kann man nur an
dem Rechner, auf dem das Programm gestartet wurde. Lesen und korrigieren geht überall.

**„Dieses PDF scheint nicht zu diesem Text zu gehören.“**
Sie haben zu einem EPUB oder Textbuch ein PDF gewählt, dessen Wortlaut kaum mit dem Text übereinstimmt – vermutlich ein
anderes Buch oder eine andere Ausgabe. Angelegt wurde nichts. Wählen Sie das richtige PDF, oder legen Sie das EPUB ohne
Seitenbilder an – siehe [Ein Buch öffnen](add-book.md).

**„Dieses PDF wurde nicht mit dem Fraktur-Korrektor gesichert.“**
Das PDF enthält keinen Arbeitsstand. Lesen Sie es mit **Öffnen …** ein wie jedes andere PDF.

**„In diesem Buch stecken schon Korrekturen – es wird nicht ersetzt.“**
*Text neu erkennen lassen* ersetzt das eben eingelesene Buch – aber nur, solange das Programm es selbst eingelesen hat
und noch keine Arbeit darin steckt. Sobald Sie korrigiert oder ein Wort bestätigt haben, bleibt das Buch stehen. Lesen
Sie das PDF stattdessen mit **Öffnen …** als neues Buch ein; das alte nehmen Sie bei Bedarf mit dem ✕ aus der Liste und
löschen den Ordner von Hand.

## Lesen und Korrigieren

**Oben steht „(keine Bildzuordnung für diese Seite)“.**
Das Programm weiß für jede Zeile, wo sie im Seitenbild steht (Datei `lines.json` im Buchordner). Diese Zuordnung geht
der Reihe nach: erste Textzeile – erste Bildzeile, zweite – zweite. Stimmt die Zahl der Textzeilen nicht mehr mit der
Zahl der Bildzeilen überein, kann das Programm sie nicht mehr sicher zuordnen und lässt es lieber: Der Text bleibt
lesbar und korrigierbar, aber das Bild wandert nicht mehr Zeile für Zeile mit. Ursachen:

- Sie haben die Textdatei in einem anderen Editor bearbeitet und dabei Zeilen eingefügt, gelöscht oder umbrochen.
  Stellen Sie dort die alte Zeilenzahl wieder her (die Kopfzeile `# …` und die Fußnotenlinie `---` zählen nicht mit).
  Zeilen teilen oder verbinden Sie besser im Programm mit `Umschalt`+`Enter` und `V` – dann führt es das Bild mit.
- Der Text kam aus einem Textexport ohne Zeilenlage (siehe [Ein Buch öffnen](add-book.md)). Holen Sie den Export aus
  Transkribus als **PAGE XML** und lesen Sie ihn mit *Erkannten Text einlesen* noch einmal ein.
- Ein Import hat die Seite verändert: **Frühere Fassung** in der Bibliothek holt Text und Zeilenlage von vorher zurück.

Betrifft es nur eine Seite, hilft auch **Seite ersetzen …** in der Kopfleiste: Die Seite wird neu erkannt und bekommt
dabei eine neue Zeilenlage – Ihre Korrekturen auf dieser Seite gehen dabei allerdings verloren (die vorige Fassung liegt
in der Sicherung). Siehe [Bedienung](usage.md).

**„Die Datei wurde inzwischen außerhalb geändert – Seite wird neu geladen.“**
Die Textdatei der Seite sieht anders aus als das, was Ihr Browser zeigt – meist, weil sie gleichzeitig in einem
Editor oder an einem zweiten Gerät bearbeitet wurde. Das Programm überschreibt dann nichts, sondern lädt die Seite
neu. Wiederholen Sie die Korrektur. Sie dürfen die Textdateien jederzeit in einem Editor bearbeiten; drücken Sie danach
im Programm `R`, damit die Seite neu geladen wird.

**Fast alles ist rot.**
Dann passt das Wörterbuch nicht zum Buch. Drücken Sie `D` und lassen Sie die Rechtschreibung gelten, in der das Buch
gedruckt ist (vor 1901: „Thür“, „giebt“; 1901–1996: „daß“; danach: „dass“). Das Fenster zeigt, wie viele rote Wörter
es vorher und nachher gibt. Namen und Orte bestätigen Sie einmal mit `F8` – das gilt dann für das ganze Buch. Siehe
[Bedienung](usage.md).

**Die Seitenzahl in der Kopfzeile ist rot.**
Sie passt nicht zu den Nachbarseiten – die Texterkennung liest in Fraktur gern „16“ als „46“. Der Hinweis nennt die
Zahl, die dort stehen müsste; `Leertaste` und `Enter` berichtigen sie wie ein Wort.

**Zeilen sind orange umrandet, oben steht eine Zahl.**
Nach dem Zusammenführen zweier Arbeitsstände wurden diese Zeilen an beiden Rechnern verschieden berichtigt. `Z`
springt zur nächsten, `1` behält die hiesige Fassung, `2` nimmt die andere – siehe
[Ein Buch als PDF sichern](pdf-sichern.md).

**Das erste Öffnen dauert lange.**
Beim ersten Mal prüft das Programm jedes Wort des Buchs gegen das Wörterbuch; das kann bis zu einer Minute dauern.
Danach sind die Ergebnisse gespeichert, und es geht schnell.

**Ich habe eine Serienkorrektur falsch gemacht.**
`U` im Lesemodus nimmt die letzte Serie zurück; Zeilen, die Sie seither von Hand geändert haben, bleiben. Jede einzelne
Änderung steht außerdem in `korrekturen.log` im Buchordner.

## Texterkennung und Wörterbücher

**Tesseract oder Transkribus?**
Tesseract ist eingebaut, kostenlos und läuft auf Ihrem Rechner; Transkribus ist ein Internetdienst mit meist besserer
Fraktur-Erkennung, lohnt aber vor allem bei schwierigen Vorlagen. Die Abwägung steht unter
[Mit Transkribus arbeiten](transkribus.md).

**Das Buch ist in Antiqua, nicht in Fraktur.**
Beim Einlesen wählen Sie die Schrift; für Antiqua nimmt das Programm ein anderes Modell. Ein Buch, das beide Schriften
mischt, lesen Sie mit der Schrift ein, die überwiegt.

**Ein Wort ist richtig, aber rot.**
`F8` merkt es sich für das ganze Buch (Whitelist, mit `W` einsehbar). Gängige Abkürzungen, mehrfach vorkommende Siglen
und längere Wörter, die mindestens dreimal im Buch stehen, gelten ohnehin – siehe [Bedienung](usage.md).

**Kann ich ein eigenes Wörterbuch verwenden?**
Ja, für die Rechtschreibung von 1901–1996: ein Hunspell-Wörterbuch (`.dic` und `.aff`) über `--dic <pfad>` oder den
Eintrag `"dic"` in der Datei `config.json` im Ordner `.fraktur-korrektor` Ihres Benutzerordners – siehe
[Werkzeuge installieren](install-tools.md).

## Zusammenarbeit und Sichern

**Wie sichere ich meine Arbeit?**
Jede Korrektur ist sofort gespeichert. Kopieren Sie von Zeit zu Zeit den ganzen Buchordner (wo er liegt, steht unter
[Programm installieren](install.md)), oder sichern Sie das Buch als PDF – eine Datei mit Bildern, Text und
Arbeitsstand: [Ein Buch als PDF sichern](pdf-sichern.md).

**Ich möchte an zwei Rechnern arbeiten.**
Als PDF sichern, am anderen Rechner mit **Öffnen …** einlesen, dort weiterarbeiten, wieder sichern. Zurück am ersten
Rechner erkennt das Programm das Buch wieder und empfiehlt *Aktualisieren* oder – wenn an beiden Stellen korrigiert
wurde – *Zusammenführen*. Siehe [Ein Buch als PDF sichern](pdf-sichern.md).

**„Dieses Buch lässt sich nicht aus dem PDF aktualisieren.“**
Hier wurde seit dem Sichern weitergearbeitet, oder es ist ein anderes Buch. Wählen Sie *Zusammenführen*, wenn das
Programm es anbietet, sonst legen Sie das PDF als neues Buch an.

**Kann jemand anders vom eigenen Gerät aus mitlesen?**
Ja, im selben Heimnetz: Starten Sie das Programm mit der Option `--lan`; die Adresse für die anderen Geräte steht beim
Start. Es gibt keinen Passwortschutz, darum nur im eigenen Netz verwenden. Bücher hinzufügen geht nur am Rechner selbst
– siehe [Bedienung](usage.md).

**Darf ich die Textdateien in einem anderen Programm bearbeiten?**
Ja, jederzeit; das Programm liest geänderte Dateien von selbst neu (`R` lädt die Seite neu). Zwei Dinge beachten:
Jede Zeile muss eine Zeile bleiben, sonst geht die Bildzuordnung verloren (siehe oben), und solche Änderungen stehen
nicht im Korrekturprotokoll – beim Zusammenführen zweier Arbeitsstände kommen sie deshalb nicht mit.
