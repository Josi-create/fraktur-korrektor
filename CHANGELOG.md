# Änderungen

Format nach [Keep a Changelog](https://keepachangelog.com/de/), Versionen nach [SemVer](https://semver.org/lang/de/).

## [Unveröffentlicht]

### Neu
- **Fußnotenzeichen hochstellen**: Die hochgestellten Zahlen, die im Text auf eine Fußnote verweisen, liest die
  Texterkennung oft als `*` oder klebt sie ans Wort (»beziffert.36«). Gespeichert werden sie wie im EPUB als
  `<sup>36</sup>`; das Bearbeitungsfeld zeigt sie als hochgestellte Ziffern (»³⁶«) statt der Auszeichnung, und
  `Strg`+`Umschalt`+`+` (wie in Word, am Mac mit `⌘`) stellt die Ziffern vor der Schreibmarke – oder die markierten –
  hoch bzw. wieder normal. Hochgestellte Ziffern, die ins Feld kommen (auch eingefügte), werden beim Speichern und beim
  Teilen zu `<sup>` (`korrlib.sup_markup`, im Reader `supMark`).
- **Fußnotenzeichen vorschlagen**: Auf Seiten mit Fußnoten markiert das Programm ein `*` direkt am Wort und am Wort
  klebende Ziffern blau (Markierung `fnref`, nicht `*)` und nicht Stellenangaben wie »S.12«); `Leertaste` springt hin,
  die vermutete Nummer steht schon hochgestellt im Feld, `Enter` übernimmt sie. Die Nummer ergibt sich aus der
  Zählung in Lesereihenfolge (`Book.footnote_refs`), verankert an schon hochgestellten Nummern, an passenden
  angeklebten Ziffern und an den lesbaren Nummern der Fußnoten unten – von diesen gilt nur die längste Folge, die mit
  den Seiten wächst (`footnote_anchors`), damit verstümmelte (»3« statt 36) nicht stören. In einem Buch mit 279 Seiten
  stimmen die Vorschläge überall, wo die Fußnoten lesbar sind; wo die Erkennung viele Zeichen verschluckt hat, liegen sie
  daneben – eine richtig hochgestellte Nummer korrigiert die folgenden. Notizen (`F4`) zitieren ohne Fußnotenzeichen.
  Selbsttest-Taste `CtrlShift:<taste>`.
- **Fußnoten ohne Fußnotenstrich erkennen**: Hat die Texterkennung die Fußnoten nicht abgetrennt – ihre hochgestellten
  Nummern liest sie oft als »3!«, »°«, »S,«, an denen die Erkennung beim Einlesen scheitert –, setzt das Programm beim
  ersten Öffnen eines Buchs (auch eines vorhandenen) den Trenner `---` selbst, als gewöhnlichen Eintrag wie mit `F`.
  Erkannt am Seitenbild (`Book.footnote_starts`): Vor dem Block steht der größte Abstand der Seite (mindestens 1,8
  Zeilenabstände – dort sitzt im Druck der Strich), und die kleinere Schrift fasst mehr Zeichen je Bildpunkt
  Zeilenbreite. In einem Buch mit 279 Seiten lag das Verhältnis im Fußnotenblock bei 1,20–1,28, auf Seiten ohne
  Fußnoten um 1,0; verlangt wird 1,12. Nur auf Seiten ohne Trenner und nur in Büchern mit Fußnoten (Muster auf
  wenigstens drei Seiten, und mindestens ein Zehntel der Seiten hat Fußnoten) – in einem Roman ohne Fußnoten wäre es
  Rauschen unter Bildern. Einmal je Buch (Merkzeile `fussnoten` im Protokoll); `F` verschiebt oder entfernt den Strich,
  das Zusammenführen spielt ihn nach. Die Statuszeile sagt, auf wie vielen Seiten. Danach erst werden die Absätze
  erkannt, die so vor den Fußnoten enden.
- **Kolumnentitel als Textzeile erkennen**: Neuere Bücher tragen oben auf jeder Seite Buch- oder Kapiteltitel und
  Seitenzahl (»Stalins Bauernopfer am Schwarzen Meer 9«, auch »28 …« auf linken Seiten). Die Texterkennung liest das
  als gewöhnliche Zeile – oft auch Titel und Zahl als zwei –, die Kopfzeile blieb leer: Der Titel stand im Fließtext,
  wurde auf jeder Seite geprüft, und Notizen nannten die Dateiseite. Genau wie die Seitenzahl unten erkennt das
  Programm ihn jetzt beim Lesen am Muster des ganzen Buchs (`korrlib.head_lines`): derselbe Wortlaut ohne Ziffern in
  einer der beiden obersten Textzeilen von mindestens drei Seiten, auf mindestens einem Drittel der Seiten, und die
  Seitenzahlen darin passen zu den Nachbarseiten. Er erscheint blass wie die Kopfzeile, wird nicht geprüft, gehört
  nicht zu Absätzen, getrennten Wörtern über die Seitengrenze oder der Zeilenlänge und lässt sich nicht löschen; seine
  Zahl ist die Seitenzahl (auch für die Warnung vor Lesefehlern). Die Dateien ändern sich nicht. Ein Kolumnentitel
  ohne Zahl bleibt Text.
- **Schriftgröße passend zur Zeilenlänge des Buchs**: Bei Büchern im Großformat mit rund 100 Zeichen je Zeile brach
  rechts jede gedruckte Zeile zweimal um – Text und Seitenbild liefen auseinander, und das Eingabefeld zeigte nur einen
  Teil der Zeile. Jetzt wählt der Reader die Schriftgröße je Buch so, dass eine volle Zeile (95 % der Zeilen im
  Haupttext sind höchstens so lang, `zeichen` in `/api/overview`) auch rechts in eine Zeile passt, beim Ändern der
  Fenstergröße neu; nie größer als bisher eingestellt, nicht kleiner als 60 %. `Strg`+`+`/`−` stellen die Größe für
  dieses Buch fest ein, `Strg`+`0` wieder auf passend. Das Eingabefeld hat jetzt dieselbe Schriftgröße wie der Text
  (bisher immer 19 Pixel).
- **Verbundene Zeilen wieder trennen (`Umschalt`+`V`)**: Wer mit `V` gedruckte Zeilen verbunden hatte – etwa, um einen
  Absatz zu kennzeichnen –, bekam eine überlange Zeile, die im Text viermal umbrach, im Seitenbild einen hohen Rahmen
  und sich im Eingabefeld kaum bearbeiten ließ. `Umschalt`+`V` trennt eine so verbundene Zeile genau an der Stelle, die
  das Protokoll kennt, auch für Verbindungen aus früheren Fassungen; mehrmals gedrückt, auch mehrere. `V` merkt sich
  jetzt die beiden Bildrahmen in `lines.json` (`vorher`), dann kommen sie genau zurück; bei älteren Verbindungen wird
  der hohe Rahmen nach dem Zeilenabstand der übrigen Zeilen waagrecht geteilt (zu wenige auf der Seite: aus dem ganzen
  Buch). Dasselbe gilt für `Umschalt`+`Enter` im Feld: Ein mehrzeiliger Rahmen wird zwischen den gedruckten Zeilen
  geteilt statt nebeneinander.
- **`V` fragt nach**, wenn die beiden Zeilen auch im Seitenbild untereinander stehen: `V` ist für Zeilen gedacht, die
  die Texterkennung fälschlich getrennt hat; einen Absatz setzt `A`. Ein zweites `V` verbindet trotzdem
  (`/api/lines` mit `force`; das Zusammenführen zweier Arbeitsstände fragt nicht).
- **Absätze** (#67): Für ein späteres E-Book muss das Programm wissen, wo ein Absatz beginnt. Ein Absatzanfang steht als
  `<p>` am Anfang seiner ersten Zeile, ohne Schlusszeichen – der Absatz reicht bis zum nächsten, auch über die
  Seitengrenze; die Zeilenzahl bleibt, wie sie ist. Beim ersten Öffnen eines Buchs – auch eines vorhandenen – erkennt
  das Programm die Absätze am Einzug im Seitenbild: gegenüber den Nachbarzeilen derselben Spalte um 0,45 bis 3
  Zeilenhöhen eingerückt, und die Zeile davor endet mit einem Satzzeichen (nicht mit `¬`). In drei Büchern mit
  Transkribus-, Textebenen- und hOCR-Zeilen lagen Absätze bei 0,6–2,2 Zeilenhöhen, gewöhnliche Zeilen unter 0,3; auf den
  geprüften Seiten war jeder erkannte Anfang ein echter. Gesetzt wird nur, wenn 1–25 % der Zeilen Absatzanfänge wären,
  sonst hat das Buch keine Einzüge oder keine brauchbare Zeilenlage. Die Statuszeile sagt, wie viele es waren. Der
  Lauf ist als Serie protokolliert: `U` nimmt ihn ganz zurück (und fragt vorher mit eigenem Wortlaut, `/api/series_last`),
  danach erkennt das Programm das Buch nicht noch einmal. `A` setzt oder entfernt einen Absatzanfang von Hand. Der
  Reader rückt die erste Zeile eines Absatzes ein wie im Druck; beim Verbinden zweier Zeilen fällt ein `<p>` mitten in
  der Zeile weg. Hilfe *Bedienung* (DE/EN): Abschnitt *Absätze (A)*.
- **Beispielbuch** (#4): `beispiel/` enthält acht Seiten aus Goethes *Faust* (Cotta 1862, gemeinfrei; Scan der
  University of Toronto bei archive.org) – Titelblatt mit Bibliotheksstempel, der Anfang von »Nacht« und die
  Prosaszene »Trüber Tag. Feld.« mit Silbentrennung. Eingelesen mit dem eigenen Weg (Tesseract, frak2021), unkorrigiert:
  Ampel grün, ein paar rote Wörter zum Ausprobieren. `python server.py beispiel`; Quelle und Rechte in
  `beispiel/README.md`. Was beim Lesen darin entsteht (Lesezeichen, Protokoll …), übergeht Git. Ein Test prüft, dass
  jede Textzeile ihre Bildzeile hat.
- **Rauschen vom Scanrand löschen** (#73): Zeilen, die die Texterkennung aus einem dunklen Rand oder einer
  angeschnittenen Nachbarseite gelesen hat (`BTB`, `LLL AAA`), löscht im Lesemodus `Strg`+`⌫` (Mac: `⌘`+`⌫`) – die
  Lesezeile oder alle mit `Umschalt`+`↓`/`↑` markierten, ohne Rückfrage; `Strg`/`⌘`+`Z` holt die zuletzt gelöschten
  Zeilen zurück, auch mehrmals hintereinander. `Entf` allein bleibt absichtlich ohne Wirkung. Kopfzeile,
  Fußnotenstrich, Seitenzahl unten und Tabellenzeilen sind geschützt. Die Bildzeilen fallen aus `lines.json` mit weg und
  kommen beim Zurückholen an ihren Platz in der Folge zurück (Zeilenzahl = Bildzuordnung); gemerkt wird das in
  `geloescht.json` samt Nachbarzeilen – hat sich die Seite so verändert, dass die Stelle unklar ist, bleibt die Zeile
  gelöscht und eine Meldung sagt es. Protokoll: `loeschen:ID` bzw. `zurueck:ID`, eine Zeile je Eintrag. Das
  Zusammenführen zweier Arbeitsstände spielt beides nach; eine Zeile, die hier inzwischen anders lautet, wird nicht
  gelöscht, sondern als Konflikt gezeigt. `/api/lines/<seite>` mit `kind=delete`, `/api/undelete`. Am Mac zeigt die
  Tastenleiste jetzt `⌘` statt `Strg`. Hilfe *Bedienung* (DE/EN): Abschnitt *Rauschen vom Scanrand löschen*.
- **Seitenzahl unten auf der Seite**: Neuere Bücher (und ältere auf Kapitelanfängen) tragen die Seitenzahl unten. Das
  Programm erkennt sie dort jetzt von selbst – eine kurze Zeile unter den letzten drei, die fast nur aus einer Zahl
  besteht, Rauschen vom Seitenrand daneben (»i 20«, »44ä«, »— 137 —«) inbegriffen, Bogensignaturen (»4 *«) nicht. Das
  gilt nur, wenn das ganze Buch das Muster zeigt (mindestens ein Drittel der Seiten ohne Zahl in der Kopfzeile hat unten
  eine, die zu einer Nachbarseite passt); Jahreszahlen und Fußnotennummern am Seitenende bleiben so außen vor. Die Zahl
  gilt dann wie die aus der Kopfzeile: für die Seitenangabe in Notizen, für die Warnung vor Lesefehlern (»35« statt 39
  wird rot, bei gleicher Stellenzahl), und ein über die Seitengrenze getrenntes Wort wird über sie hinweg als Ganzes
  geprüft. Der Reader zeigt sie blass wie die Kopfzeile. Dateien ändern sich dabei nicht.
- **Inhalt (Taste `I`)**: alle mit `H` ausgezeichneten Überschriften des Buchs, eingerückt nach Ebene, mit gedruckter
  Seitenzahl; `Enter` oder Klick springt hin. Zwei Zeilen derselben Ebene untereinander (»Drittes Kapitel.« / »Die Reise
  nach Odessa.«) sind eine Überschrift. Schnittstelle `/api/headings`.
- **Inhaltsverzeichnis im gesicherten PDF**: Die Überschriften werden die Lesezeichen des PDFs (Seitenleiste jedes
  PDF-Readers); die Tiefe ergibt sich aus der Abfolge der Ebenen, damit keine übersprungen wird.
- **`--last`**: Ohne Buchordner gestartet, öffnet der Browser gleich das zuletzt gelesene Buch (Lesezeichen, Öffnen
  und Einlesen merken sich das) statt der Bibliothek; ein Buch, dessen Ordner fehlt, wird übergangen, ohne Bücher
  bleibt es bei der Bibliothek. Die Bibliothek bleibt unter `/` erreichbar. Gedacht für eine Startdatei wie
  `py server.py --lan --last`.
- **Hilfeseite »Bücher selbst fotografieren«** (#43, DE/EN): jede Seite einzeln, Kamera parallel, Seite bildfüllend
  (Faustregel 1800 Bildpunkte für 15 cm), Licht, Reihenfolge und Dateinamen, eine Probe vor dem Archivbesuch, was
  bei Doppelseiten hilft, Buch-Scan-Apps wie vFlat mit Preis (Stand September 2026) und dem Hinweis, dass die
  Fotos durch eine fremde App laufen. In der Hilfe nach *Ein Buch öffnen*, verlinkt aus der Übersicht, *PDF oder
  Bilder einlesen* und den *Häufigen Fragen*. Beispielfotos fehlen noch (es gibt keine gemeinfreie Vorlage im
  Repository).
- **iPhone-Fotos im Format HEIC**: Das Programm kann sie nicht lesen, sagt das jetzt aber beim Öffnen, statt
  »nichts gefunden« zu melden, und nennt den Ausweg (per Kabel übertragen oder das iPhone auf *Maximale
  Kompatibilität* stellen) – auch in der Hilfeseite und den Häufigen Fragen.
- **README und *Programm installieren*** (#57, Teil): Der Satz »es muss nichts nachinstalliert werden« stimmt jetzt
  genauer – Doppelseiten und Schieflage erledigt das Programm selbst, ScanTailor ist ein Zusatz für schwierige
  Vorlagen. Ob ScanTailor enger eingebunden wird, ist offen.
- **Nachbesserungen aus der Durchsicht** (#61, #71): Der Kindle-Dialog vergisst beim erneuten Öffnen den Ordner des
  vorigen Buchs (sonst landeten Zettel beim falschen Buch). Schon übernommene Zettel erkennt das Programm am ganzen
  Zitat samt Quellenzeile – ein kurzes Zitat, das wie ein längeres anfängt, und eine Notiz aus einem Wort, das in
  einem Zitat vorkommt, gelten nicht mehr fälschlich als vorhanden; eckige Klammern im Ordnernamen verdoppeln die
  Zettel nicht mehr (`os.listdir` statt `glob`). Eine erst nach dem Übernehmen auf dem Kindle geschriebene Notiz kommt
  als eigener Zettel. Eine Textdatei gilt nur als Kindle-Datei, wenn ihre Kennzeilen danach aussehen (eine
  unterstrichene Überschrift genügt nicht mehr). Ist der Zielordner eine Datei oder schreibgeschützt, erscheint eine
  Meldung statt »Failed to fetch« – beim Kindle wie bei `F4`. Gleiche Titel werden in jeder Schrift erkannt (zwei
  kyrillische Titel galten als gleich). Ein Titel mit `[ ] |` zerbricht den Obsidian-Verweis der `F4`-Zettel nicht mehr.
- **Kindle-Markierungen nach Obsidian** (#61): Aus jeder Markierung auf dem Kindle wird ein Zettel wie mit `F4` –
  fortlaufend nummeriert, das Zitat mit Seite und Position, Verweis auf `0 Quellenangabe` (beim ersten Mal mit Titel,
  Autor und »Kindle-Ausgabe« angelegt); eine eigene Notiz vom Kindle wird die Anmerkung über dem Zitat, eine Notiz
  ohne Markierung ein Zettel ohne Zitat. Einstieg in der Bibliothek unter der Bücherliste; »Öffnen …« erkennt
  `My Clippings.txt` (auch umbenannt, am Inhalt) und das Kindle-Laufwerk und führt dorthin. Ein als Laufwerk
  angeschlossener Kindle wird von selbst gefunden (nur Wechseldatenträger, damit ein getrenntes Netzlaufwerk nicht
  bremst); Kindles ab 2024 melden sich als Mediengerät, der Hinweis im Fenster und die neue Hilfeseite *Markierungen
  vom Kindle* (DE/EN) erklären den Weg. Neues Modul `kindle.py`: Kennzeilen deutsch und englisch, BOM und CRLF,
  abgekürzte Positionen älterer Geräte; eine erweiterte Markierung ersetzt den kürzeren Eintrag davor, die
  Kopiergrenze des Verlags wird gezählt statt als Zitat übernommen. Vorgeschlagen wird der Notizordner eines
  gleichnamigen Buchs der Bibliothek, sonst ein neuer Ordner neben dem zuletzt benutzten Notizordner. Schon
  vorhandene Zettel erkennt das Programm am Zitat – die Datei lässt sich nach jedem Lesen wieder einlesen.
  `/api/kindle_scan`, `/api/kindle_notes` (nur lokal); die Zettel-Helfer (`notes_ready`, `note_source`,
  `note_number`) teilt sich `F4` jetzt mit dem Kindle. Selbsttest: `/bibliothek#kindle=<datei>|<ordner>`.
- **Vorbereiten-Knöpfe nach Ampel und Herkunft** (#69): *Scans vorbereiten*, *Für Transkribus vorbereiten* und *Für
  ScanTailor vorbereiten* treten in der Bibliothek grau zurück, wenn sie wenig bringen – bei grüner Ampel, wenn der
  Text schon aus Transkribus stammt (dann auch die beiden Bildvorbereitungen: sie bräuchten eine neue Erkennung, die
  bei Fraktur selten besser ist) oder wenn die Seiten schon mit ScanTailor bzw. dem Programm selbst aufbereitet sind.
  Benutzbar bleiben sie: Der Tooltip und im Dialog *Weiterbearbeiten* eine Zeile darunter sagen, warum, ein Klick
  fragt nach. Nach dem eingebauten Vorbereiten bleibt ScanTailor frei – es kann gewölbte Seiten und Flecken. Ohne
  Ampel (Buch noch nicht bewertet) ändert sich nichts.
  Ebenso *Erkannten Text einlesen*: grau, wenn der Text schon aus Transkribus oder von einer Bibliothek stammt oder
  im Buch schon 50 und mehr Korrekturen stecken – der neue Text enthielte sie nicht. Dann ist im Dialog auch *als
  neues Buch anlegen* vorgewählt, das bisherige Buch bleibt samt Korrekturen daneben stehen.
- **Buch umbenennen** (#71): Knopf *Umbenennen* in der Bibliothek, auch im Dialog *Weiterbearbeiten*. Ein Buch, das
  noch wie seine Datei heißt (`asjflkasjdfl.pdf`), bekommt einen richtigen Namen – in der Bibliothek, oben in der
  Leseansicht, in Notizen für Obsidian und als Dateiname beim Sichern als PDF. Der Ordner bleibt, wie er ist, damit
  die Adresse `/buch/<id>`, offene Tabs und das Lesezeichen weiter stimmen (`/api/rename`, nur lokal).
- **Doppelklick ins Seitenbild** (#70): Die Zeile unter dem Mauszeiger wird Lesezeile, links wie rechts – auch auf
  der vorigen oder nächsten Seite im Bildstapel und bei zweispaltigem Satz. Ein Doppelklick auf eine Abbildung oder den
  leeren Rand (weiter als eine Zeilenhöhe von jeder Zeile entfernt) verstellt nichts. Selbsttest: `keys=imgdbl:002:1`.
- **Korrekturvorschläge im Voraus** (#68): Während Sie lesen, rechnet das Programm die Wörterbuchvorschläge für die
  nächsten drei roten Wörter aus (der Reader meldet sie über `/api/suggest_ahead`, sobald sich die Liste ändert);
  kommt man dort an, stehen sie sofort da statt nach ein bis fünf Sekunden.
- **Hilfe, Entwurf zum Gegenlesen** (#23, #24, #25 – noch nicht abgeschlossen): *Mit Transkribus arbeiten*
  bekommt den Abschnitt *Was es kostet* (Konten, Credits je Seite, Rechenbeispiel, Grenzen des kostenlosen
  Kontos), Fehlerquoten und Stand der öffentlichen Fraktur-Modelle, den aktuellen Exportweg. *PDF oder Bilder
  einlesen* bekommt *Der Weg im Überblick* (Einlesen → Ampel → Scans vorbereiten → ScanTailor → Transkribus) und
  einen Absatz zu Tesseract und dem Modell frak2021. Neue Seite *Andere Programme im Vergleich*
  (`docs/de/vergleich.md`, `docs/en/vergleich.md`): ABBYY FineReader, Transkribus, Tesseract, OCR4all/LAREX,
  eScriptorium/Kraken, OCR-D, gImageReader, PoCoTo – Preis, Fraktur, Korrekturkomfort, Datenschutz, Lernkurve,
  Export, Plattform, mit Quelle und Stand-Datum je Angabe. Alle drei Seiten tragen oben den Vermerk »Entwurf vom
  24. September 2026«; die Angaben zu fremden Programmen sind gegen die offiziellen Seiten geprüft, aber vom
  Betreiber noch nicht gegengelesen.
- **Linux-Fassung als AppImage** (#45, noch ohne Probelauf auf einem Linux-Rechner): Der Release-Workflow bekommt
  einen Auftrag auf `ubuntu-22.04`, der mit derselben PyInstaller-Spec baut und mit `scripts/build_appimage.sh`
  ein `Fraktur-Korrektor-linux-x86_64.AppImage` (fester Name, Dauerlink) und ein `…-linux-x86_64.tar.gz` als
  Rückfall packt; beides läuft vorher durch `scripts/smoke_test.py`. »Run workflow« hat den Haken `nur_linux`.
  Tesseract wird unter Linux nicht mitgeliefert, sondern aus dem Paketmanager erwartet (`/usr/bin/tesseract`
  jetzt auch ohne vollen PATH gefunden); das Frakturmodell lädt das Programm wie bisher nach. Der Starter zeigt
  unter Linux ein kleines Fenster mit *Im Browser öffnen* und *Beenden* (tkinter, ohne Display die Konsole) und
  setzt `LD_LIBRARY_PATH` für Kindprozesse auf den Wert des Systems zurück, damit Tesseract und der Browser
  nicht die Bibliotheken aus dem Bundle laden. `packaging/linux/` mit `AppRun` und `.desktop`-Eintrag;
  Anleitung in *Programm installieren* (DE/EN), Bauschritte in `RELEASE.md`.
- **Hilfe als Website** (#27): `tools/build_site.py` schreibt die Seiten aus `docs/de` und `docs/en` mit derselben
  Vorlage und Navigation wie im Programm (`server.help_html`, jetzt ohne laufenden Server aufrufbar) nach `site/`,
  dazu eine Startseite mit Sprachwahl und dem Überblick aus der README; Links zwischen den Seiten sind relativ,
  Links auf Programmfunktionen bleiben als Text mit dem Hinweis »im Programm«. Der Workflow `pages.yml` baut sie bei
  jedem Push auf `main` und veröffentlicht sie über GitHub Pages unter <https://josi-create.github.io/fraktur-korrektor/>,
  sobald Pages im Repository eingeschaltet ist. Tests prüfen, dass jede Hilfeseite herauskommt und alle Links
  aufgehen.
- **Community-Dateien** (#28): `CONTRIBUTING.md` (Einrichtung, Aufbau, was nicht brechen darf, Stil, Testumgebung,
  Hilfe auch ohne Programmieren), `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1 im offiziellen Wortlaut),
  `SECURITY.md` (was lokal bleibt, was `--lan` öffnet, wie man Lücken meldet), `CITATION.cff`; jeweils deutsch mit
  englischer Fassung `*.en.md`. Issue-Vorlagen für Fehlerbericht und Vorschlag in beiden Sprachen (ohne Buchinhalte
  hochzuladen – Urheberrecht), `config.yml` verweist auf die Häufigen Fragen, Pull-Request-Vorlage mit Checkliste.
  README-Abschnitt *Mitmachen*. Ein Test prüft, dass jede Datei ihr Gegenstück in der anderen Sprache hat und die
  Version in `CITATION.cff` mit `pyproject.toml` übereinstimmt.
- **EPUB: das PDF von anderswo dazuholen** (#40): Liegt neben einem EPUB kein gleichnamiges PDF, bietet *Öffnen …*
  den Knopf *Passendes PDF auswählen …* (Dateidialog, nur am Rechner selbst); danach läuft es wie bei EPUB und PDF im
  selben Ordner. Vorher prüft eine Stichprobe (`epub.pdf_fit`: Vier-Wort-Folgen einiger Seiten der Textebene), ob
  das PDF zu dem Text gehört; ohne Textebene entscheidet der Anteil zugeordneter Zeilen nach der Texterkennung.
  Passt es nicht, wird nichts angelegt und die Meldung nennt den nächsten Schritt. Für ein schon angelegtes
  Textbuch (EPUB ohne PDF) gibt es in der Bibliothek *PDF hinzufügen*: Es entsteht ein neues Buch mit Seitenbildern
  und Zeilen aus dem PDF und dem Wortlaut des Textbuchs samt seinen Korrekturen und seiner Wortliste
  (`epub.transplant_book`); das Textbuch bleibt unangetastet, weil Protokoll und Lesezeichen zu seinen Seiten
  gehören. Selbsttest `#pair=<epub>|<pdf>`, Hilfe unter *Ein Buch öffnen*.
- **Zweispaltiger Satz** (#37): Zeitungen und Lexika werden spaltenweise gelesen – linke Spalte von oben nach
  unten, dann die rechte – statt Zeile für Zeile verschränkt. `pagexml.columns` erkennt die Spalten an den
  Zeilenkästen (eine durchgehende Lücke in der Mitte, beide Seiten nebeneinander und breit), darum gilt es für
  alle Wege: Tesseract, PDF-Textebene, Transkribus, hOCR und ALTO. Eine Zeile über die Seitenmitte (Überschrift)
  trennt Abschnitte, die je für sich geprüft werden. Nebeneinanderstehende kurze Fußnoten bleiben zeilenweise,
  einspaltige Seiten unverändert; drei Spalten, Tabellen und Verzeichnisse mit Seitenzahlen rechts bleiben Zeile
  für Zeile. Hilfe unter *PDF einlesen* und *Transkribus*.
- **Häufige Fragen und Fehlerbehebung** (#26): neue Hilfeseite `faq` in beiden Sprachen – Firewall-Nachfrage, belegter
  Port, SmartScreen und Gatekeeper, fehlendes Wörterbuch, verlorene Bildzuordnung, 409-Konflikt nach dem Bearbeiten in
  einem Editor, orange Zeilen nach dem Zusammenführen und die übrigen Fehlermeldungen des Programms, je mit dem nächsten
  Schritt. Verlinkt aus der Hilfeübersicht, der Kopfleiste des Readers, der Fußzeile der Bibliothek und aus jeder
  Fehlermeldung der Bibliothek.
- **Scans vorbereiten** (#42): Doppelseiten teilen und schiefe Seiten geraderichten erledigt das Programm jetzt selbst,
  nur mit PyMuPDF (`scans.py`). Beim Untersuchen eines PDF oder Bilderordners sieht es sich einige Seiten an
  (Seitenverhältnis, helle Lücke oder Falzschatten in der Bundmitte, Neigung der Zeilen über das Projektionsprofil)
  und empfiehlt *Scans vorbereiten …*; die Vorschau zeigt die erste Doppelseite mit einer Trennlinie, die sich mit
  der Maus oder den Pfeiltasten verschieben lässt und auf jeder Seite noch einmal an der Falz feinjustiert wird.
  Gedreht wird ab 0,3°. Das Ergebnis liegt in `<Buchordner>/aufbereitet`, wird beim Untersuchen wie ein
  ScanTailor-Ergebnis bevorzugt und in der Bibliothek als *vorbereitet* gekennzeichnet. Für Bücher der
  Bibliothek gibt es den Knopf *Scans vorbereiten* (auch in der Leseansicht). ScanTailor bleibt für gewölbte
  Seiten, Flecken und dunkle Ränder; Hilfe und Oberflächentexte sagen das jetzt so, dazu Aufnahmetipps.
  **Ränder und Finger** (Punkt 3 des Issues): drittes Häkchen *Dunkle Ränder und Finger entfernen*, nach dem
  Teilen und Drehen. `scans.paper_box` sucht auf dem Messbild zusammenhängende Flächen, die deutlich dunkler als
  das Papier sind (auch Schatten und Haut, nicht nur Druckerschwärze), den Bildrand berühren und dick sind –
  Textzeilen sind dünn. Was eine Kante fast ganz entlangläuft (Tischplatte, Buchkante, Schatten), wird
  abgeschnitten, ein Fleck (Finger, Klammer) weiß übermalt – beides nur außerhalb des Textblocks mit
  Sicherheitsabstand; was in den Text ragt, bleibt, und eine dunkle Fläche über der halben Seite wird in Ruhe
  gelassen. Die Vorschau zeigt den Schnittkasten grün gestrichelt, die Empfehlung nennt dunkle Ränder, wenn sie
  auf mindestens der Hälfte der Stichprobe vorkommen. `aufbereitung.json` bekommt `raender`, `beschnitten` und je
  Seite `schnitt`; alte Dateien ohne diese Angaben gelten als unbeschnitten.
- **Korrekturvorschläge** (#41): Ein kleines Menü unter dem roten Wort zeigt Vorschläge, `↓`/`↑` setzen sie ins
  Feld, Klick ebenso, `Enter` übernimmt. Zuerst, was in diesem Buch schon einmal aus dem Wort gemacht wurde
  (gelernt aus `korrekturen.log`: `Würllemberg` → `Württemberg`), dann typische Lesefehler der Fraktur-OCR rückgängig
  gemacht (`b`/`d`, `f`/`s`, `n`/`u`, `r`/`t`, `ll`/`tt`, Umlautpunkte – nur wenn ein bekanntes Wort herauskommt, häufige
  im Buch zuerst), zuletzt Hunspell. Hunspell braucht über spylls Sekunden je Wort und kommt darum in einer zweiten
  Anfrage nach; die ersten Vorschläge stehen sofort da.
- **Eine Seite ersetzen** (#52): *Seite ersetzen …* in der Kopfleiste der Leseansicht tauscht das Seitenbild gegen eine
  Bilddatei oder eine PDF-Seite und erkennt nur diese Seite neu (Tesseract, ohne Tesseract die Textebene des PDF).
  Text, Zeilenlage und Bild der Seite kommen vorher in `vorher-<Datum>.zip`; *Frühere Fassung* holt auch das Bild
  zurück. Die Sicherungen enthalten jetzt außerdem Wortliste und Lesezeichen.
- **Zwei Arbeitsstände zusammenführen** (#66): Wurde seit dem Sichern an beiden Rechnern korrigiert, empfiehlt
  *Öffnen …* **Zusammenführen**. `merge.py` spielt die Einträge aus dem `korrekturen.log` des PDF, die hier fehlen,
  auf das vorhandene Buch nach – Korrekturen, Serien, geteilte und verbundene Zeilen (samt `lines.json`),
  Fußnotenstriche, neu erkannte Seiten –, vereinigt die Wortlisten und nimmt das weiter hinten liegende Lesezeichen;
  Seitenbilder nur für Seiten ohne Bild. Nachgespielte Einträge kommen wortgleich ins Protokoll, darum reicht beim
  nächsten Wechsel in die andere Richtung wieder das einfache Aktualisieren (der Vergleich der Protokolle ist jetzt
  mengenweise statt als Präfix). Wurde dieselbe Zeile an beiden Stellen anders berichtigt, bleibt die hiesige
  Fassung und die Zeile kommt nach `konflikte.json`: In der Leseansicht ist sie orange umrandet, `Z` springt hin und
  zeigt beide Fassungen (`1` behalten, `2` übernehmen). Vorher wird der Stand wie beim Aktualisieren gesichert; der
  Notizordner eines Rechners überlebt das Aktualisieren jetzt.
- **Buch aus dem gesicherten PDF aktualisieren** (#66, einfacher Fall): Liegt dasselbe Buch schon in der Bibliothek und
  ist hier seit dem Sichern nichts geschehen (alles, was hier im Protokoll steht, steht auch im PDF), empfiehlt
  *Öffnen …* **Vorhandenes Buch aktualisieren** statt einer Kopie „(2)“; die bisherige Fassung wird gesichert. Wurde
  an beiden Stellen korrigiert, wird zusammengeführt (siehe oben).
- **Getrennte Wörter über die Seitengrenze** (`Ge¬` | `# 23` | `walt`) werden als Ganzes geprüft, Kopfzeile und Fußnoten
  dazwischen stören nicht. Ist das Wort unbekannt, sind beide Hälften rot, und der Hinweis nennt die andere Seite.
- **Erste Schritte beim ersten Start** (#19): Die leere Bibliothek zeigt, ob Wörterbuch, Tesseract und ScanTailor da
  sind – Haken oder Kreuz, dahinter *So installieren* und *Programm zeigen …* –, und was als Nächstes zu tun ist.
- **Ein Buch als PDF sichern und auf einem anderen Rechner weiterlesen** (#58): *Als PDF sichern* (Bibliothek oder
  Leseansicht) schreibt eine Datei mit den Seitenbildern (unverändert eingepackt), dem Text unsichtbar darüber
  (Suchen, Kopieren, Vorlesen in jedem PDF-Reader – mit den Korrekturen) und dem ganzen Arbeitsstand als Anhang
  `fraktur-korrektor.zip`: Seitentexte, Zeilenlage, Wortliste, Lesezeichen, Protokoll, Einstellungen. *Öffnen …*
  erkennt ein solches PDF („gesichertes Buch“, mit Datum und Zahl der Korrekturen) und legt daraus wieder ein Buch
  an, die Bilder verlustfrei. Ein zweites Sichern desselben Buchs ersetzt sein eigenes PDF, fremde Dateien nie.
  Jedes Buch bekommt dafür eine feste Kennung (`buch.json`), an der ein anderer Rechner es wiedererkennt;
  das Zusammenführen zweier Arbeitsstände ist noch offen (#66). Neues Modul `pdfbuch.py`, Hilfeseite
  *Ein Buch als PDF sichern*.
- **Schriftgröße des Textes** (`Strg`+`+`/`−`/`0` oder `Strg`+Mausrad über dem Text) – unabhängig vom Zoom des
  Seitenbildes (`+`/`−`/`0`), die Einstellung bleibt erhalten. **Breite Tabellen** liefen bisher rechts aus dem Fenster,
  ohne dass man hinkam: Jetzt rollt die Tabelle mit der Lesezeile seitwärts mit, von Hand mit `Umschalt`+Mausrad.
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
- **README neu, auch auf Englisch** (#62, #20 zum Teil): Sie beginnt mit dem, was das Programm für Leser ohne
  Technikkenntnisse tut – alte Bücher lesen, berichtigen und daraus zitieren –, dann *Was es kann*, *Für wen?* und ein
  Beispielzettel für Obsidian (Exzerpieren nach dem Vorbild von Luhmanns Zettelkasten). Der veraltete Satz »Ziel ist ein
  sauberer Text als Grundlage für ein Epub« ist weg. Start aus dem Quelltext mit allen Optionen, `--lan`, Wörterbücher,
  Buchordner und Kommandozeilenwerkzeuge stehen jetzt in `CONTRIBUTING.md`/`CONTRIBUTING.en.md`. Neue `README.en.md`;
  der Test der Community-Dateien prüft auch sie. Die Startseite der Website übernimmt den neuen Überblick ohne den
  Verweis auf die englische README. README und Hilfe sagen jetzt richtig, dass die Tastenleiste unten steht, unter Bild
  und Text (nicht mehr »oben rechts«).
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
- **Silbentrennung nach der Erkennung mit Tesseract**: Das Frakturmodell frak2021 liest den Doppelstrich ⸗ am
  Zeilenende oft als Gedankenstrich (»unend—« / »licher«, auch »ver—-«). Das Einlesen machte daraus bisher kein `¬`,
  das getrennte Wort war dann rot. Jetzt gilt ein Strich direkt am Wort, auf den klein weitergeschrieben wird, als
  Trennung; ein Gedankenstrich mit Leerzeichen davor bleibt einer. Betrifft neu eingelesene Bücher.
- **Zwei Änderungen an derselben Seite kurz hintereinander** (#72): Windows vergibt Änderungszeiten von Dateien in
  Schritten von bis zu etwa 15 ms (HFS+ am Mac in Sekunden). Wurde eine Seite zweimal so schnell geschrieben – beim
  Zusammenführen etwa Teilen und gleich danach Verbinden –, bekam sie dieselbe Zeit, und das Programm arbeitete mit
  der vorigen Fassung weiter: Das Verbinden wurde als Konflikt gemeldet, der Fußnotenstrich danach auf die veraltete
  Seite gesetzt. Daher kam der gelegentlich scheiternde Test unter Windows. Nach jedem Schreiben liest das Programm die
  Seite jetzt sicher neu; dasselbe gilt für die Whitelist (ein zweites Wort kurz nach dem ersten blieb sonst rot).
- **Hilfe: Taste für den Notizordner**: Die Tastentabelle in *Bedienung* nannte `N` – das springt zur nächsten
  Fundstelle. Der Notizordner liegt auf `O`, wie im Fließtext darunter und in der Kopfleiste (»Notizen (O)«).
- **Hilfe: zerschossene Tabelle in »Ein Buch öffnen«**: Die erste Spalte einer Tabelle brach nie um – gedacht für
  Tastenkürzel und Dateinamen. Mit ganzen Sätzen darin (»Buch – ein Ordner, an dem Sie …«) wurde sie so breit, dass die
  zweite Spalte aus der Seite ragte. Das gilt jetzt nur noch für schmale Tabellen mit durchweg kurzen Einträgen links
  (`server.short_table`); eine Tabelle, die trotzdem zu breit ist, lässt sich seitwärts rollen, statt aus dem Kasten
  zu ragen. Betraf auch *Mit Transkribus arbeiten* und die Vergleichstabelle, im Programm wie auf der Website.
- **Zwei Spalten neben einem Bild wurden verschränkt** (#37): Läuft eine Spalte neben Fotos schmaler weiter, galt sie
  als zu schmal für eine Spalte – in einem Zeitschriftenartikel lag sie mit 29,7 % des Satzspiegels knapp unter der
  Schwelle von 30 %, und der obere Teil der Seite wurde Zeile für Zeile gelesen. Die Schwelle liegt jetzt bei 20 %;
  die Seitenzahlen eines Inhaltsverzeichnisses bleiben mit unter 10 % weiter außen vor. Bereits eingelesene Seiten
  ändern sich dadurch nicht, erst beim Neuerkennen.
- **F9 nimmt das rote Wort, auf dem man steht**: Beim Lesen das rote Wort der Lesezeile, in der Korrektur das offene
  Wort samt der schon getippten Verbesserung als Ersetzung. Vorher gewann das Angebot zur letzten Korrektur („‚ber‘
  kommt noch 74× vor“), auch wenn man längst beim nächsten Wort war, und beim Lesen blieben beide Felder leer. Das
  Angebot gilt jetzt, bis man selbst weitergeht (auch wenn das Programm schon zum nächsten roten Wort derselben
  Zeile gesprungen ist), und die Hinweiszeile zeigt es nur, solange F9 ihm gilt.
- **Return beim Korrigieren reagierte träge** (#68), seit es Korrekturvorschläge gibt: Die Wörterbuchvorschläge
  rechnete spylls im Thread der Anfrage, sekundenlang in reinem Python; das Speichern musste sich den Interpreter mit
  ihm teilen und wartete nach jedem Dateizugriff bis zu 5 ms – bei einem Buch mit 361 Seiten 1–3 s statt 0,07 s.
  Jetzt rechnet ein eigener Thread (`korrlib.Vorschlaege`), der bei jedem Wörterbuchzugriff anhält, solange eine
  andere Anfrage läuft, und aufhört, wenn der Nutzer schon beim nächsten Wort ist. Gemessen an einer Kopie dieses
  Buchs: Speichern während der Vorschlagssuche 0,08 s. Das Zeitbudget von 1,5 s gilt jetzt auch mitten in einem
  Schritt von spylls (vorher bis zu 20 s bei langen Zusammensetzungen; ohne jeden Vorschlag höchstens 7,5 s), und das
  Einlesen des Wörterbuchs zählt nicht mehr mit.
- **ALTO einer Bibliothek: die gelbe Lesezeile im Seitenbild war nur ein Strich unter der Zeile** und wirkte wie
  eine Zeile zu tief. Die SuUB Bremen gibt ihren Zeilen (`TextLine`) eine Höhe von −2 oder 6 Pixeln bei einer
  Lage in Zeilenmitte; nur die Wörter (`String`) haben brauchbare Kästen. Der Zeilenkasten kommt jetzt aus den
  Wortkästen; das `TextLine`-Attribut gilt nur noch für Zeilen ohne Wortkästen. Dazu hängt die SuUB unten an jedes
  PDF-Bild eine graue DFG-Leiste, das Bild ist also höher als der ALTO-Rahmen: Bisher wurde der Rahmen höhenfüllend
  aufs Bild gelegt, womit die Markierung unten auf der Seite eine Zeile zu tief lag. Ist das Bild höher als der
  Rahmen, gilt jetzt die Breite, und der Rahmen sitzt oben. Schon eingelesene Bücher brauchen dafür kein neues Einlesen.
- **Die zweite Hälfte eines getrennten Wortes (`Zu¬` / `kunft`) war mit der Tastatur nicht zu erreichen.** Bei der
  Korrektur führen jetzt `Tab`, `↓` und `→` über das Zeilenende hinaus ins zweite Eingabefeld, `Umschalt`+`Tab`, `↑`
  und `←` am Zeilenanfang zurück. Aus dem zweiten Feld geht `Tab` wie bisher zum nächsten roten Wort.
- **„Text nachlegen“ und Einlesen endeten gelegentlich mit einem unbekannten Fehler:** Speicherten ein Hintergrundauftrag
  und eine Anfrage des Browsers gleichzeitig den Zwischenspeicher der Wortprüfung, schrieben beide über dieselbe
  Zwischendatei, und der zweite fand sie beim Umbenennen nicht mehr (`FileNotFoundError`). Der Text war dann schon
  übernommen, nur die Rückmeldung fehlte. Das Speichern ist jetzt gegen gleichzeitige Zugriffe gesperrt; aufgefallen war
  es als wackelnder Test. Unter Windows schlug das Umbenennen außerdem fehl, solange Virenscanner oder Suche die frisch
  geschriebene Datei gerade offen hatten (`PermissionError`) – das Speichern wartet das jetzt ab.

## [0.5.0] – 2026-09-18

Stand vor Beginn der Veröffentlichungsarbeiten: Lesemodus, Korrekturmodus, Serienkorrektur (F9) mit Rücknahme,
Whitelist, Fußnotentrenner, Lesezeichen, Korrekturprotokoll, `--lan`, Werkzeuge für Transkribus-PAGE-XML.
