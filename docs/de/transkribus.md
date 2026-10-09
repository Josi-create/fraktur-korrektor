# Mit Transkribus arbeiten

*Die Angaben zu Transkribus – Preise, Knöpfe, Modelle – sind am 9. Oktober 2026 auf transkribus.org und
help.transkribus.org nachgeprüft. Transkribus ändert seine Oberfläche und Preise gelegentlich; wenn etwas anders
aussieht, gilt, was Sie dort sehen.*

[Transkribus](https://www.transkribus.org/) ist ein Dienst der europäischen Genossenschaft READ-COOP zur
Texterkennung in historischen Dokumenten. Für Frakturdrucke liefert er meist deutlich bessere Ergebnisse als
Tesseract – vor allem bei mäßigen Vorlagen. Der Fraktur-Korrektor ist für genau diese Arbeitsteilung gebaut:
**Transkribus erkennt, der Fraktur-Korrektor macht das Korrekturlesen bequem.**

## Was man wissen sollte

- Transkribus arbeitet **im Internet**: Ihre Seitenbilder werden auf die Server von READ-COOP in Österreich
  hochgeladen. Nach eigener Angabe bleiben Sie Eigentümer Ihrer Dokumente und können sie jederzeit löschen
  ([Is my data safe?](https://help.transkribus.org/is-my-data-safe)). Bei urheberrechtlich geschützten oder
  vertraulichen Vorlagen sollten Sie das Hochladen trotzdem bedenken.
- Sie brauchen ein **Konto**; das kostenlose genügt zum Ausprobieren. Die Erkennung kostet *Credits*: 50 im
  Monat sind frei, eine gedruckte Seite kostet einen halben Credit (die Zeilenerkennung ist darin enthalten) –
  das reicht für etwa 100 Seiten im Monat, nicht für ein ganzes Buch. Für ein Buch kauft man Credits nach oder
  verteilt die Arbeit auf mehrere Monate. Zahlen und Grenzen: [Was es kostet](#was-es-kostet).
- Es gibt die Web-Anwendung (im Browser) – sie genügt für alles hier Beschriebene. Installieren müssen Sie
  nichts.
- **Zweispaltiger Satz** (Zeitungen, Lexika): Die Layoutanalyse von Transkribus legt in der Regel je Spalte einen
  eigenen Textbereich an; das Programm liest dann spaltenweise – erst links von oben nach unten, dann rechts.
  Sind die Spalten im Ergebnis verschränkt, prüfen Sie in Transkribus die Bereiche der Seite (jede Spalte ein
  Bereich, keine Zeile über beide Spalten hinweg) und exportieren Sie erneut.

## Was es kostet

Transkribus rechnet in *Credits* ab. Die Zahlen hier stammen von <https://www.transkribus.org/plans> und
<https://help.transkribus.org/credit-system> (Stand 9. Oktober 2026); alle Preise verstehen sich
einschließlich 20 % österreichischer Mehrwertsteuer. Prüfen Sie sie vor dem Kauf – sie ändern sich.

| Konto | Credits | Preis |
|---|---|---|
| **Free** | 50 im Monat | kostenlos |
| **Scholar** | 900 im Jahr | 99 € im Jahr (oder 19,99 € im Monat) |
| **Team** (bis 5 Personen) | 1 500 im Jahr | 449 € im Jahr (oder 69 € im Monat) |
| Credits einzeln nachkaufen | 250 | 59,50 €, ohne Abo; verfallen nie |

Was ein Auftrag kostet, je Seite:

| Auftrag | Credits |
|---|---|
| Texterkennung **Druck** samt Zeilen – Ihr Fall | 0,5 |
| Texterkennung Handschrift samt Zeilen | 1 |
| Nur Zeilen finden (Layout, Schritt 4 – meist nicht nötig) | 0,25 |
| Tabellen oder Formularfelder erkennen | 1 |

Hochladen, Herunterladen und Korrigieren kosten nichts.

Rechenbeispiel: Ein Buch mit 400 Seiten braucht 400 × 0,5 = 200 Credits. Mit dem kostenlosen Konto sind das vier
Monate zu je 50 Credits – oder einmal 250 Credits nachkaufen (59,50 €); dann bleiben noch welche übrig. Vor jedem
Auftrag zeigt Transkribus die Kosten an und startet erst auf Ihren Klick (Schritt 5); ein Versehen kostet also
nichts.

**Grenzen des kostenlosen Kontos** (laut Preis- und Hilfeseiten, Stand 9. Oktober 2026):

- Das *Super-Modell* „Text Titan II“ gibt es erst ab dem Scholar-Konto. Für Frakturdrucke genügen die freien
  Modelle aus Schritt 5.
- Der Export als **Page XML** – der einzige, den der Fraktur-Korrektor braucht – ist in allen Konten enthalten,
  ebenso Bilder, Text, Word und PDF. ALTO, METS und TEI gibt es nur in den bezahlten Konten.
- Speicherplatz: 20 GB.
- Die freien Monats-Credits gelten laut Preisseite für den jeweiligen Abrechnungszeitraum; ob Reste in den
  nächsten Monat mitgehen, steht dort nicht. Nachgekaufte Credits verfallen nie.

## Schritt für Schritt

Die Oberfläche von Transkribus ist englisch; die Knöpfe stehen hier darum so, wie sie dort heißen
(Stand: Oktober 2026). Rechnen Sie fürs erste Mal mit einer halben Stunde.

### 1. Konto anlegen und anmelden

Auf [transkribus.org](https://www.transkribus.org/) rechts oben auf **„Get Started"** klicken, das Formular
ausfüllen und die E-Mail-Adresse bestätigen. Danach melden Sie sich jederzeit über **„Log In"** an. Sie landen
in der Web-Anwendung; alles Weitere geschieht dort.

### 2. Eine Sammlung anlegen

Eine *Collection* ist eine Schublade für Ihre Bücher; ohne sie geht es nicht.

1. Links im Menü auf **„Collections"**.
2. Rechts auf **„+ New Collection"**.
3. Einen Namen eintippen, etwa den Buchtitel, und auf **„+ Create"**.

### 3. Die Seitenbilder hochladen

1. Die eben angelegte Sammlung anklicken, sodass sie geöffnet ist.
2. Oben rechts auf **„Upload"**.
3. Die Dateien hineinziehen oder über **„Browse"** auswählen. **Welche Dateien?** Laden Sie immer die
   Bilder hoch, die Sie am Ende lesen wollen – Transkribus trennt keine Doppelseiten und richtet nichts gerade.
   - Haben Sie die Scans im Fraktur-Korrektor **vorbereiten** lassen (Doppelseiten geteilt, geradegerichtet): die
     Dateien aus dem Ordner **`…/aufbereitet`** im Buchordner. Nach **ScanTailor**: die Dateien aus dessen
     Ausgabeordner **`…/scantailor/out`**. Das sind die getrennten, geraden Einzelseiten (TIFF nimmt Transkribus an).
   - Haben Sie dieses Ergebnis schon im Fraktur-Korrektor **eingelesen**: die Bilder aus dem Ordner **`img`**
     dieses Buchs – inhaltlich dasselbe, nur durchnummeriert. **Den Ordner müssen Sie nicht suchen:** In der
     Bibliothek steht beim Buch der Knopf **Für Transkribus vorbereiten**. Das
     Programm nennt den Ordner, legt ihn in die Zwischenablage und öffnet ihn im Dateifenster, sodass Sie ihn
     gleich hineinziehen können. Das ist auch der Weg, der die Seiten später am sichersten wieder zuordnet.
   - War der Scan schon in Ordnung: die Bilder aus `img` Ihres Buchordners oder gleich das **PDF**,
     Transkribus zerlegt es selbst in Seiten.

   Nachsehen lohnt sich: Sind es so viele Dateien, wie das Buch Seiten hat? Bei getrennten Doppelseiten müssen
   es doppelt so viele sein wie Blätter im Scan.
4. Bei **„Title"** einen Namen für das Dokument eintragen.
5. Auf **„Submit"**. Den Fortschritt sehen Sie links im Menü unter **„Processes & Activity"**; bei vielen
   Seiten dauert es.

<!-- Bildschirmfoto: transkribus-hochladen.png – das Upload-Fenster einer Sammlung mit einigen hineingezogenen Seitenbildern, dem ausgefüllten Feld „Title“ und dem Knopf „Submit“ -->

Erlaubt sind laut Transkribus-Hilfe JPG, PNG und TIFF (je Bild bis 20 MB, bis 3000 Dateien auf einmal) sowie
PDF (je Datei bis 512 MB). Empfohlen sind etwa 300 dpi – genau das liefert der Fraktur-Korrektor; mehr bringt
nach Angabe von Transkribus nichts.

### 4. Nur bei schwierigem Satz: die Zeilen vorab finden lassen (Layout)

Die Texterkennung in Schritt 5 sucht die Zeilen von selbst; für ein gewöhnliches Buch können Sie diesen Schritt
überspringen. Lohnend ist er bei **zwei Spalten, Tabellen oder verwinkeltem Satz**: Dann sehen Sie das Ergebnis
an und können es in Transkribus berichtigen, bevor der Text erkannt wird.

1. Im Dokument oben links das Kästchen anklicken, das **alle Seiten auswählt**.
2. Auf **„Process with AI"**.
3. Oben bei *Process Type* statt „Text Recognition" **„Layout Analysis"** wählen. Als Modell empfiehlt die
   Transkribus-Hilfe *Mixed Line Orientation*, *Universal Lines* oder *Horizontal Line Orientation*.
   Kosten: 0,25 Credits je Seite. Dann **„Start recognition"**.

Blättern Sie danach eine Seite durch: Über jeder Textzeile sollte eine Linie liegen. Sitzen die Linien schief
oder fehlen sie, hilft meist ein besseres Bild (ScanTailor) mehr als eine andere Einstellung.

### 5. Den Text erkennen lassen

1. Im Dokument oben links das Kästchen anklicken, das **alle Seiten auswählt**, und auf **„Process with AI"**.

   <!-- Bildschirmfoto: transkribus-auswahl.png – ein geöffnetes Dokument mit angehaktem Kästchen „alle Seiten auswählen“ oben links und dem Knopf „Process with AI“ daneben -->

2. Der Bereich **„Text Recognition"** ist schon gewählt. Im Suchfeld ein Modell suchen – nach dem Namen oder
   nach „Fraktur“:

   | Modell | wofür | Fehlerquote laut Modellseite |
   |---|---|---|
   | **Transkribus Print M1** | alle Drucke, Fraktur und Antiqua, 14 Sprachen – die sichere Wahl | 2,2 % der Zeichen |
   | **ONB_Newseye_GT_M1+** | deutsche Fraktur, spätes 18. bis Mitte 20. Jahrhundert; Zeitungen der Österreichischen Nationalbibliothek | 1,1 % |
   | **NZZ Gold Standard M1+** | deutsche Fraktur 1780–1940; Titelseiten der Neuen Zürcher Zeitung | 0,5 % |

   Die Fehlerquoten stammen von den Modellseiten auf transkribus.org (Stand 9. Oktober 2026) und gelten für die
   Prüfseiten des jeweiligen Modells, nicht für Ihr Buch – die kleinere Zahl ist nicht von selbst das bessere
   Modell für Sie. Im Zweifel *Transkribus Print M1*. Für ein Buch von 1850 bis 1940 lohnt ein Vergleich an zwei,
   drei Seiten. Das *Super-Modell* der bezahlten Konten (**Text Titan II**, seit Juni 2026, Druck und
   Handschrift in zwölf Sprachen) brauchen Sie für sauberen Frakturdruck in der Regel nicht.

   <!-- Bildschirmfoto: transkribus-modellwahl.png – die Seitenleiste nach „Process with AI“: Process Type „Text Recognition“, im Suchfeld „Fraktur“ mit der Trefferliste, darunter die benötigten und die vorhandenen Credits und der Knopf „Start recognition“ -->

3. Transkribus zeigt an, **wie viele Credits** der Auftrag kostet (0,5 je Seite) und wie viele Sie noch haben.
   Erst dann auf **„Start recognition"**.

**Danach dürfen Sie den Rechner ausschalten.** Die Erkennung läuft auf den Servern von READ-COOP in
Österreich, nicht bei Ihnen; Ihr Computer wird dafür nicht gebraucht. Nur beim Hochladen (Schritt 3) muss er
an bleiben, bis es abgeschlossen ist.

Je nach Andrang dauert die Erkennung Minuten bis zu einem Tag. Für ein ganzes Buch geben Sie den Auftrag am
besten abends und sehen am nächsten Morgen nach: Den Stand finden Sie links im Menü unter **„AI Lab"**
(„RUNNING“ heißt: läuft gerade, „CREATED“: wartet noch), das fertige Ergebnis außerdem im Dokument selbst.

### 6. Das Ergebnis herunterladen

1. In der Sammlung das Dokument (oder alle Seiten) auswählen.
2. Oben auf den Knopf **„Action"** und darin auf **„Export"**.
3. Als Format **„Page XML"** wählen – nicht PDF, nicht Word. Darin stecken die Zeilen samt ihrer Lage im
   Bild, und genau das braucht der Fraktur-Korrektor, um den Text Zeile für Zeile neben dem Seitenbild
   mitzuführen. Den einfachen **Textexport** liest das Programm zwar auch, aber der enthält nur den Wortlaut:
   Die Zeilen lassen sich dann nicht mehr im Bild zeigen.

   **Bilder mitnehmen?** Liegt das Buch schon im Fraktur-Korrektor, brauchen Sie sie nicht – die Seitenbilder
   sind ja schon da. Ist es ein neues Buch, wählen Sie zusätzlich **„Images"**: Dann steckt alles in einer
   Datei, und Sie müssen beim Einlesen keine Bilder suchen.
4. Auf **„Start export"**.

   <!-- Bildschirmfoto: transkribus-export.png – das Export-Fenster mit angehaktem „Page XML“ (und „Images“) und dem Knopf „Start export“ -->

5. Sie bekommen eine E-Mail mit einem Link (zwei Wochen gültig). Ohne E-Mail: links im Menü unter
   **„Processes & Activity"** → **„Up- & Downloads"** beim fertigen Export ganz rechts auf die drei Punkte und
   **„Download"**.

   <!-- Bildschirmfoto: transkribus-download.png – „Processes & Activity“ → „Up- & Downloads“ mit einem fertigen Export und dem geöffneten Drei-Punkte-Menü mit „Download“ -->

Sie erhalten eine **ZIP-Datei**. Entpacken müssen Sie sie nicht.

### 7. Zurück in den Fraktur-Korrektor

**Liegt das Buch schon in Ihrer Bibliothek** – weil Sie es vorher mit Tesseract eingelesen haben –, dann
gehört der Text dorthin und nicht in ein neues Buch: in der Bibliothek beim Buch auf
**Erkannten Text einlesen** klicken und die ZIP-Datei wählen. Ihre Seitenbilder bleiben, wo sie sind; Sie
müssen nichts suchen und nichts doppelt anlegen. Das Programm sagt Ihnen danach, wie viele Seiten es ersetzt
hat und wie es sie zugeordnet hat.

**Ist es ein neues Buch:** Bibliothek → **Öffnen …** → **Datei wählen …** → die ZIP-Datei. Das Programm
erkennt den Export von selbst. Fehlen darin die Bilder, schlägt es einen Bilderordner vor, der genau so viele
Bilder hat, wie der Export Seiten – oder Sie fügen die Bilder später mit **Seitenbilder hinzufügen** an.
Einzelheiten: [Ein Buch öffnen](add-book.md).

## Danach

Beim Import trennt das Programm Kopfzeilen und Fußnoten ab und markiert unbekannte Wörter rot. Typische
Verwechslungen der Fraktur (`ber` statt „der“, `bie` statt „die“, `Bolk` statt „Volk“) beheben Sie am
schnellsten mit der **Serienkorrektur** (`F9`) – siehe [Bedienung](usage.md).

## Tesseract oder Transkribus?

| | Tesseract (eingebaut) | Transkribus |
|---|---|---|
| Kosten | kostenlos | 50 Credits im Monat frei (etwa 100 Seiten), ein ganzes Buch kostet Geld oder Monate |
| Datenschutz | alles bleibt auf Ihrem Rechner | Bilder werden hochgeladen |
| Aufwand | ein Klick | Konto, Hochladen, Warten, Export |
| Qualität bei sauberem Scan | gut | sehr gut |
| Qualität bei mäßigem Scan (Handyfotos, gewölbte Seiten) | oft schwach | meist noch gut |

Faustregel: Erst mit Tesseract einlesen. Zeigt die Ampel Grün, sind Sie fertig. Bei Gelb oder Rot lohnt sich
für ein ganzes Buch der Weg über Transkribus.
