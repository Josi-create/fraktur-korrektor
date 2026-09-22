# Änderungen

Format nach [Keep a Changelog](https://keepachangelog.com/de/), Versionen nach [SemVer](https://semver.org/lang/de/).

## [Unveröffentlicht]

### Neu
- **Notizen für Obsidian** (#60): Passage markieren, `F4` oder Rechtsklick – das Programm legt im Notizordner des Buchs
  (Taste `O`, Ordner im Obsidian-Vault, gespeichert in `buch.json`) einen fortlaufend nummerierten Zettel an: oben
  Platz für die Anmerkung, unter dem Strich das Zitat und „Seite x“ mit Verweis auf die Quellenangabe des Buchs (`0 Quellenangabe.md`, wird
  als Vorlage für Herkunft und Zotero-Zitierweise angelegt). Obsidian öffnet den Zettel sofort und kommt in den Vordergrund; das Zitat liegt auch in der
  Zwischenablage. Ohne Markierung wird die Lesezeile zum Zettel. Mehrere Zeilen lassen sich auch mit der Tastatur
  markieren: `Umschalt`+`↓`/`↑`, dann `F4`.
- **Das Seitenbild rollt fließend über die Seitengrenze**, wie der Text rechts: Links stehen Vorgänger, Seite und
  Nachfolger untereinander, das Mausrad läuft ohne Sprung von einer Seite in die nächste. Die Bildmaße kommen vom
  Server mit, damit die Nachbarseiten schon richtig liegen, bevor ihre Bilder geladen sind.
- **Suchen im ganzen Buch und Gehe zu Seite** (#56): `S` öffnet oben eine Eingabezeile; das Programm sucht im
  ganzen Buch, ohne Rücksicht auf Groß-/Kleinschreibung und ſ/s, auch über die Zeilentrennung ¬ hinweg, und springt
  zur ersten Fundstelle ab der Leseposition – blau im Text, eingerahmt im Seitenbild. Oben bleibt ein kleines Feld
  mit Suchwort, Zählung („3 / 17“) und Knöpfen: `N` nächste, `Umschalt`+`N` vorige Fundstelle. `G` fragt auf
  dieselbe Weise nach einer Seitenzahl statt über ein Browser-Fenster.
- **Der erkannte Text einer Bibliothek (hOCR, ALTO) lässt sich über ein Buch legen.** Viele Bibliotheken geben
  ihre Digitalisate als PDF ohne Text heraus, obwohl sie den Text längst erkannt haben – er liegt nur getrennt,
  eine Datei je Seite (die Bayerische Staatsbibliothek etwa als hOCR über ihre Schnittstelle). Wer diese Dateien
  in einen Ordner holt, liest sein PDF wie gewohnt ein und wählt dann *Erkannten Text einlesen* (bisher
  *Transkribus-Text einlesen*). Die Seiten finden sich am Wortlaut der ersten Erkennung – ein Deckblatt vorn im
  PDF stört darum nicht –, die Lage der Zeilen im Bild kommt mit, Satzzeichen, die die Bibliothek als eigene
  Wörter führt, hängen wieder am Wort. Das Buch trägt danach das Kennzeichen *Bibliothek*. Das Programm lädt
  weiterhin nichts aus dem Internet; die Hilfe sagt, wo man suchen kann. Geprüft am hOCR der BSB (360 Seiten,
  alle zugeordnet) und am ALTO der SuUB Bremen (309 Seiten; dort ist auch der Trennstrich am Zeilenende ein
  eigenes Wort und wird wieder zu »¬«).
- **Ein Buch weiterbearbeiten, statt jedes Mal ein neues anzulegen** (#44): In der Bibliothek steht bei jedem Buch,
  was möglich ist – *Transkribus-Text einlesen*, *Seitenbilder hinzufügen*, *Für Transkribus vorbereiten*,
  *Für ScanTailor vorbereiten*. Wer sein Buch erst mit Tesseract einliest, die Seiten aufbereitet und
  dann bei Transkribus erkennen lässt, fängt nicht wieder von vorn an und sucht seine Seitenbilder nicht: Der neue
  Text tritt an die Stelle des alten, Bilder, Wortliste und Lesezeichen bleiben. Stecken schon Korrekturen im Buch,
  wird gewarnt und ein neues Buch angeboten – erzwungen wird es nicht. Die bisherige Fassung sichert das Programm
  vorher als `vorher-<Datum>.zip`.
  **Die Seitenzuordnung** geschieht über die Namen der Bilddateien (dafür merkt sich das Programm beim Einlesen in
  `quellen.json`, wie jedes Seitenbild ursprünglich hieß), sonst am Wortlaut der Seiten, erst zuletzt der Reihe nach.
  Fehlt im Export eine Seite, verschiebt sich dadurch nichts; geht keiner der Wege auf, bricht das Programm lieber ab,
  als Text neben falsche Bilder zu legen.
- **Beschriftete Knöpfe an jedem Buch** (#46, #47): In der Bibliothek steht unter jedem Buch, was möglich ist –
  *Buch öffnen*, *Transkribus-Text einlesen*, *Seitenbilder hinzufügen*, *Für Transkribus vorbereiten*,
  *Für ScanTailor vorbereiten*. Dieselben Wege führen aus der Leseansicht dorthin; fehlen die Seitenbilder ganz,
  steht an ihrer Stelle ein Angebot, sie nachzulegen. Auch die Meldung „Seitenbilder fehlen" nach einem Import
  schickt niemanden mehr in den Unterordner `img`, sondern bietet einen Knopf (#49).
- **Seitenbilder nachlegen, woher sie auch kommen** (#40, #51): ein Bilderordner, das PDF, aus dem die Seiten
  stammen, oder **ein anderes Buch**. Im letzten Fall vergleicht das Programm die Texte beider Bücher – dasselbe
  Werk, nur anders erkannt – und weiß daraus, welches Bild zu welcher Seite gehört. Das Bilderbuch darf dabei
  mehr Seiten haben als das, dem die Bilder fehlen.
- **Kennzeichen und Ampel für jedes Buch** (#50): Hinter dem Titel steht, woher der Text stammt (*Tesseract*,
  *Transkribus*, *PDF-Text*) und ob die Seiten mit *ScanTailor* aufbereitet wurden, dazu der Anteil der Wörter,
  die das Wörterbuch nicht kennt. Diesen Anteil rechnet das Programm jetzt auch für Texte aus, die ohne
  Konfidenzwerte kommen – Transkribus liefert keine –, sodass auch ein Transkribus-Buch seine Ampel hat.
- **Transkribus-Textexport lesen** (#53): Wer aus Transkribus „Text" statt „PAGE XML" geholt hat, steht nicht
  mehr vor einer Absage. In der Textdatei trennen zwei Leerzeilen die Seiten; zugeordnet werden sie am Wortlaut
  wie ein XML-Export. Stimmt die Zeilenzahl mit der bisherigen überein, behalten die Zeilen ihre Lage im Bild,
  sonst sagt das Programm, für wie viele Seiten die Zeilenzuordnung verlorengeht – eine Textdatei enthält sie
  nicht. Einzelne Seiten, deren Platz unklar bleibt, lässt es aus, statt alles zu verwerfen.
- **Frühere Fassung zurückholen** (#54): Jeder übernommene Text sicherte schon bisher die Fassung, die er
  ersetzt – jetzt gibt es dafür auch einen Knopf. Er zeigt die gesicherten Fassungen mit Datum und Seitenzahl und
  holt die gewählte zurück; weil das Zurückholen seinerseits sichert, kommt man ebenso wieder vorwärts.
- **Installation für alle** (M4): Der Fraktur-Korrektor wird als fertiges Programm ausgeliefert – Doppelklick, fertig,
  nichts nachinstallieren. Windows: Installer und portables ZIP; Mac: `.app` im `.dmg` für Apple Silicon und Intel.
  **Tesseract und die Modelle `frak2021` und `deu` sind enthalten**, ebenso die Wörterbücher und die Hilfe.
  Weil das Programm kein eigenes Fenster hat, zeigt es ein Symbol im Dock und in der Menüleiste (Windows: im
  Infobereich), über das es sich beenden lässt; ein zweiter Start öffnet nur den Browser auf die laufende Instanz.
  Auf dem Mac kommen die Dateidialoge jetzt vom System. Gebaut wird bei jedem Versions-Tag von GitHub Actions;
  die Mac-App ist signiert und notarisiert, sobald die Apple-Zugangsdaten hinterlegt sind.
  Anleitungen: [Programm installieren](docs/de/install.md), für die Betreuung [RELEASE.md](RELEASE.md).
- **Zeilen teilen und verbinden** mit Erhalt der Bildzuordnung: `Umschalt`+`Enter` im Eingabefeld teilt die Zeile an der
  Schreibmarke, `V` verbindet die Lesezeile mit der nächsten (ein `¬` fällt dabei weg). Der Bildausschnitt in `lines.json`
  wird mitgeteilt bzw. vereinigt; eine Tabelle wird danach neu durchgezählt – verrutschte Spalten stehen wieder richtig.
- **Auszeichnung beim Lesen** (#38): `T` macht aus getrennten Zeilen eine Tabelle (Bereich wählen, Spaltenzahl, Vorschau,
  Spaltenköpfe; `T` auf der Tabelle löst sie wieder auf), `H` zeichnet Überschriften aus (Ebene 1–3). Geschrieben wird XHTML
  wie im EPUB (`<table><tr><td>`, `<h2>`), kein eigenes Format; jede Zeile bleibt eine Zeile, damit die Bildzuordnung hält.
  Dargestellt wird WYSIWYG: Tabellen als Tabelle (jede Zelle bleibt eine Zeile mit Lesecursor und Bildzuordnung),
  Überschriften groß, Schrift-Auszeichnung als Schrift – Steuerzeichen sind weder im Text noch im Eingabefeld zu sehen.
  Die Wortprüfung, Serienkorrektur und die Lage im Bild übergehen die Auszeichnung; getrennte Wörter werden auch hinter
  Auszeichnung zusammengefügt.
- **Wörterbuch je Buch** (Taste `D`): Rechtschreibung 1901–1996, neue Rechtschreibung (mitgeliefert: `dict/de_DE_frami`, GPL)
  und »Schreibungen vor 1901 gelten lassen« (Thür, seyn, giebt – über Regeln); das Programm schätzt das Erscheinungsjahr und
  schlägt die Einstellung vor; das Fenster zeigt die Zahl der roten Wörter vorher/nachher. Gespeichert in `buch.json`.
- Mehr Abkürzungen (wissenschaftlicher Apparat, Bibelstellen); Siglen in Großbuchstaben gelten, wenn sie mehrfach vorkommen.
- Die Ampel misst die Texterkennung unabhängig von der Rechtschreibung des Buchs.
- **Ein Knopf »Öffnen …«** statt dreier: Das Programm untersucht die gezeigte Datei bzw. den Ordner und erkennt Buchordner,
  PDF, EPUB, Seitenbilder und Transkribus-Exporte; bei mehreren Funden Empfehlung mit Seitenzahl und Datum – ein Buch mit
  Korrekturen steht immer vorn, neuere Funde sind markiert; passende Bilderordner zu Exporten ohne Bilder werden vorgeschlagen.
- **EPUB öffnen.** Mit gleichnamigem PDF daneben: links der Scan, rechts der Wortlaut des EPUB, Zeile für Zeile auf die
  Zeilen des PDF gelegt (Trennungen bleiben, Kopfzeilen/Fußnoten behalten den PDF-Text). Ohne PDF: Textbuch ohne Bilder.
- Durchsuchbare PDFs: vorhandenen Text übernehmen statt neu erkennen (570 Seiten in wenigen Sekunden); Zeilen werden
  anhand der Grundlinie geordnet, Randzeichen vom mitgescannten Seitenrand entfernt.
- Seitenbilder werden unverändert aus dem PDF entnommen, wenn die Seite aus einem einzigen Bild besteht (schneller,
  kein Qualitätsverlust); der Fortschrittsbalken zählt fertige Seiten statt der Reihenfolge.
- PDF oder Bilderordner einlesen: Texterkennung mit Tesseract (läuft parallel, Fortschrittsbalken, abbrechbar), Schriftwahl
  Fraktur/Antiqua; das Fraktur-Modell `frak2021` (UB Mannheim) wird bei Bedarf geladen.
- Qualitätsampel nach dem Einlesen (Konfidenz, Wörterbuchquote, schwache Zeilenenden) mit Empfehlung Transkribus bzw.
  ScanTailor; Ampelpunkt in der Bibliothek; Werte je Seite in `qualitaet.json`.
- ScanTailor-Anbindung: PDF-Seiten als Bilder exportieren, ScanTailor starten, Ergebnisordner einlesen; »Programm zeigen …«.
- Hilfeseiten: PDF oder Bilder einlesen, Mit Transkribus arbeiten, Werkzeuge installieren (DE/EN).
- Bibliothek: Start ohne Argumente zeigt alle bekannten Bücher; Buchordner per Dialog öffnen. Mehrere Bücher und
  Browser-Tabs nebeneinander – jedes Buch hat seine eigene Adresse (`/buch/<id>`).
- Transkribus-Export (ZIP oder Ordner) per Knopfdruck importieren, Seitenbilder aus dem Export oder einem Bilderordner; JPG-Bilder.
- Hilfe im Programm (`F1`): `docs/de`, `docs/en` werden im Browser angezeigt.
- Oberfläche auf Deutsch und Englisch.
- Hinweis beim ersten, langsamen Laden eines Buchs; Spenden-Link »Kaffee spendieren« im Fuß der Bibliothek.
- Freies Wörterbuch für die Rechtschreibung von 1901 wird mitgeliefert (`dict/`); das Programm läuft ohne `--dic`.
- Wörterbuchwahl zusätzlich über `~/.fraktur-korrektor/config.json` (`"dic"`).
- `dict/zusatz.txt` (Abkürzungen gelten als richtig) und `dict/fallen.txt` („baß“ wird immer markiert).
- Zwischenspeicher für Wörterbuchprüfungen – schnellerer Start ab dem zweiten Mal.
- Tests (pytest) und CI für Windows, macOS, Linux; `pyproject.toml`; Lizenz GPL-3.0-or-later; ROADMAP.

### Geändert
- **Seitenauswahl mit Blätterpfeilen und „4 / 30“:** Oben steht jetzt `←` Seite [Auswahl] 4 / 30 `→`, gebaut wie das
  Feld der Suche. Die Zahl der roten Wörter in Klammern hinter jeder Seite ist aus der Auswahl verschwunden – sie wurde
  für eine Seitenzahl gehalten; in der Statuszeile steht sie weiterhin.
- **Ein Buch öffnet sich sofort, wenn seine Wörter schon einmal geprüft wurden.** Bisher las das Programm bei jedem Start
  erst das Hunspell-Wörterbuch ein (mehrere Sekunden), auch wenn es danach kein einziges Wort nachschlagen musste, weil alle
  Ergebnisse im Zwischenspeicher lagen. Jetzt wird das Wörterbuch im Hintergrund geladen und nur bei einem wirklich neuen Wort
  abgewartet. Für das erste Öffnen eines Buchs zeigt der Ladebildschirm einen **Fortschrittsbalken** (»Seite 12 von 300
  geprüft«, neue Abfrage `/api/progress`).
- **Die Tastaturhilfe liegt über der ganzen Fensterbreite** (#55), nicht mehr nur über dem Text: Sie braucht so weniger
  Zeilen, das Textfenster wird höher, das Seitenbild gibt dafür oben etwas Höhe ab.
- Der fest eingetragene Pfad zu einem Wörterbuch aus Adobe Photoshop ist entfernt.

### Behoben
- **Die zweite Hälfte eines getrennten Wortes (`Zu¬` / `kunft`) war mit der Tastatur nicht zu erreichen.** Bei der
  Korrektur führen jetzt `Tab`, `↓` und `→` über das Zeilenende hinaus ins zweite Eingabefeld, `Umschalt`+`Tab`, `↑`
  und `←` am Zeilenanfang zurück. Aus dem zweiten Feld geht `Tab` wie bisher zum nächsten roten Wort.
- **„Text nachlegen“ und Einlesen endeten gelegentlich mit einem unbekannten Fehler:** Speicherten ein Hintergrundauftrag
  und eine Anfrage des Browsers gleichzeitig den Zwischenspeicher der Wortprüfung, schrieben beide über dieselbe
  Zwischendatei, und der zweite fand sie beim Umbenennen nicht mehr (`FileNotFoundError`). Der Text war dann schon
  übernommen, nur die Rückmeldung fehlte. Das Speichern ist jetzt gegen gleichzeitige Zugriffe gesperrt; aufgefallen war
  es als wackelnder Test.

## [0.5.0] – 2026-09-18

Stand vor Beginn der Veröffentlichungsarbeiten: Lesemodus, Korrekturmodus, Serienkorrektur (F9) mit Rücknahme,
Whitelist, Fußnotentrenner, Lesezeichen, Korrekturprotokoll, `--lan`, Werkzeuge für Transkribus-PAGE-XML.
