#Prüfliste für den Laptop (nach git pull, Server neu starten):

**Commits in dieser Reihenfolge**

1. **#42 Scans vorbereiten** (5840261). Neues Modul [scans.py](scans.py): Doppelseiten erkennen und teilen, Schieflage messen und geraderichten, nur mit PyMuPDF. Beim Untersuchen eines PDF oder Bilderordners empfiehlt die Bibliothek das Aufbereiten, mit Vorschau und verschiebbarer Trennlinie. Ergebnis landet in `<Buchordner>/aufbereitet` und wird wie bisher das ScanTailor-Ergebnis bevorzugt. Hilfe und ScanTailor-Texte angepasst. Das Abschneiden von Fingern und Rändern ist nicht gebaut.
2. **#66 Zwei Arbeitsstände zusammenführen** (2fecd5d). Der einfache Fall war schon da. Neu ist [merge.py](merge.py): Änderungen aus dem gesicherten PDF werden über das Korrekturprotokoll nachgespielt, Wortlisten und Lesezeichen vereinigt. Konflikte landen in `konflikte.json`, in der Leseansicht orange umrandet, mit Taste Z zum Springen und 1 oder 2 zum Wählen der Fassung.
3. **#26 FAQ** (91f13a8). Neue Hilfeseite in beiden Sprachen mit 37 Fragen, aus jeder Fehlermeldung der Bibliothek verlinkt. Der Gatekeeper-Ablauf am Mac stammt aus RELEASE.md, nicht aus eigener Beobachtung.
4. **#37 Zweispaltiger Satz** (12691f7). Rein geometrisch über die Zeilenkästen in [pagexml.py](pagexml.py), für alle Importwege. Drei und mehr Spalten bleiben bewusst wie bisher. Tesseract-Blöcke und TextRegions werden nicht ausgewertet, das steht begründet im Docstring.
5. **#40 PDF hinzufügen** (ec760a0). Im Öffnen-Dialog lässt sich zum EPUB ein PDF von anderswo wählen, mit Plausibilitätsprüfung. Bei einem vorhandenen Textbuch entsteht daraus ein neues Buch mit den bisherigen Korrekturen.
6. **Absicherung** (d6cb092). Ein Test des letzten Issues hatte in Ihren echten Bücherordner geschrieben. Die Testumgebung setzt jetzt einen eigenen Bücherordner je Instanz.

**Bitte selbst erledigen**

- In `C:\Users\johan\Fraktur-Korrektor` liegen fünf Ordner „Probe“ bis „Probe (5)“ aus den Tests. Sie enthalten nur drei Zeilen Kunsttext und stehen nicht in der Bibliotheksliste. Das Löschen wurde mir verweigert, bitte entfernen Sie sie selbst.
- Ein Agent hatte kurz einen Ordner „Fotos“ dort angelegt und selbst wieder entfernt. Ihre sechs echten Buchordner sind unberührt.

**Im Browser ausprobieren, weil nicht automatisch prüfbar**

- Ein echtes Handy-Foto-PDF öffnen: kommt die Empfehlung, stimmt die Trennlinie, wie lange dauert ein ganzes Buch? Gedrehte Seiten werden als Graustufen-JPEG geschrieben.
- Ein Buch PC, Laptop, PC mit Korrekturen an beiden Stellen durchspielen, dann Taste Z, 1, 2 in der Leseansicht. Ist die Taste Z und der Text „Vom anderen Rechner“ verständlich?
- Eine zweispaltige Lexikonseite mit Tesseract einlesen und die Reihenfolge prüfen. Eine Seite mit nebeneinanderstehenden Fußnoten an einer Kopie neu erkennen lassen.
- Dateidialog „Passendes PDF auswählen“ beim EPUB, und bei sehr schlechter OCR, ob die Schwellen `MINFIT` und `MINMATCH` in epub.py ein passendes PDF nicht fälschlich ablehnen.
- Kopfleiste der Leseansicht bei schmalen Fenstern: zwei neue Links („Scans vorbereiten“, „Häufige Fragen“) machen es eng.

Der Test `test_cache_speichern_aus_zwei_threads` schlug unter Windows zweimal mit einem Berechtigungsfehler fehl, auch auf unverändertem `main`. Das ist vorbestehend und nicht behoben.



**Prüfliste für den Laptop** (nach `git pull`, Server neu starten):

1. **Scans vorbereiten (#42).** Ein Handy-Foto-PDF oder Fotoordner über „Öffnen …“ untersuchen. Erscheint der Kasten „Das Programm sieht sich einige Seiten an“ und danach die Empfehlung mit dem Knopf „Scans vorbereiten …“? In der Vorschau: Trennlinie mit Maus und Pfeiltasten verschieben, Häkchen „geraderichten“ zeigt den gemessenen Winkel. Nach „Übernehmen“: Reihenfolge links vor rechts, Drehrichtung, weiße Ecken sind gewollt, Farbe geht verloren. Laufzeit bei einem ganzen Buch beobachten. Ist der Ordner `aufbereitet` anschließend als Empfehlung vorausgewählt?
2. **Zusammenführen (#66).** Ein Buch am PC als PDF sichern, am Laptop einlesen, dort zwei Zeilen ändern und ein Wort in die Wortliste nehmen, wieder sichern. Am PC inzwischen eine andere Zeile und dieselbe Zeile anders ändern. PDF am PC einlesen: Empfehlung „Zusammenführen“ vorausgewählt? Ergebnismeldung mit Zahlen verständlich? In der Leseansicht: orange Zeile, Link oben, Taste Z springt hin, 1 behält, 2 übernimmt, Esc später. Sind „Vom anderen Rechner“ und die Taste Z für Ihre Zielgruppe verständlich?
3. **Häufige Fragen (#26).** Link in der Fußzeile der Bibliothek und neben „Hilfe (F1)“ in der Leseansicht. Eine Fehlermeldung provozieren, etwa einen nicht vorhandenen Pfad öffnen: hängt der Link „Häufige Fragen“ an der Meldung? Bitte den Mac-Abschnitt (Gatekeeper, „Dennoch öffnen“) gegenlesen, er stammt aus RELEASE.md.

5. **PDF zum EPUB (#40).** EPUB ohne gleichnamiges PDF öffnen: Knopf „Passendes PDF auswählen …“, Dateidialog am Mac, Stichprobenzeile danach. Ein absichtlich falsches PDF muss abgelehnt werden. Bei einem vorhandenen Textbuch: Bibliothek, Bearbeiten, „PDF hinzufügen“, Korrekturen im neuen Buch vorhanden?
6. **Allgemein.** Kopfleiste der Leseansicht bei schmalem Fenster, Konsole des Browsers auf Fehler, und ob in `~/Fraktur-Korrektor` keine unerwarteten Ordner entstehen.

