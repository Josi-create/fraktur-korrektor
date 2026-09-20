# Mit Transkribus arbeiten

[Transkribus](https://www.transkribus.org/) ist ein Dienst der europäischen Genossenschaft READ-COOP zur
Texterkennung in historischen Dokumenten. Für Frakturdrucke liefert er meist deutlich bessere Ergebnisse als
Tesseract – vor allem bei mäßigen Vorlagen. Der Fraktur-Korrektor ist für genau diese Arbeitsteilung gebaut:
**Transkribus erkennt, der Fraktur-Korrektor macht das Korrekturlesen bequem.**

## Was man wissen sollte

- Transkribus arbeitet **im Internet**: Ihre Seitenbilder werden auf die Server von READ-COOP (Innsbruck)
  hochgeladen. Bei urheberrechtlich geschützten oder vertraulichen Vorlagen sollten Sie das bedenken.
- Sie brauchen ein **Konto**; das kostenlose genügt zum Ausprobieren. Die Erkennung kostet *Credits*. Im
  kostenlosen Konto sind 50 Credits im Monat enthalten (Stand September 2026) – das reicht für ein Kapitel,
  nicht für ein ganzes Buch. Für ein Buch kauft man Credits nach oder verteilt die Arbeit auf mehrere Monate.
  Aktuelle Preise: <https://www.transkribus.org/plans>.
- Es gibt die Web-Anwendung (im Browser) – sie genügt für alles hier Beschriebene.

## Schritt für Schritt

Die Oberfläche von Transkribus ist englisch; die Knöpfe stehen hier darum so, wie sie dort heißen
(Stand: September 2026). Rechnen Sie fürs erste Mal mit einer halben Stunde.

### 1. Konto anlegen und anmelden

Auf [transkribus.org](https://www.transkribus.org/) rechts oben auf **„Sign up"**, E-Mail-Adresse bestätigen,
dann **„Log in"**. Sie landen in der Web-Anwendung; alles Weitere geschieht dort.

<!-- Platz für ein Bildschirmfoto der Startseite -->

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
   - Haben Sie den Scan mit **ScanTailor** aufbereitet: die Dateien aus dessen Ausgabeordner
     **`…/scantailor/out`**. Das sind die getrennten, geraden Einzelseiten (TIFF nimmt Transkribus an).
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
5. Auf **„Submit"**. Ein Balken zeigt den Fortschritt; bei vielen Seiten dauert es.

Erlaubt sind JPG, PNG und TIFF (je bis 20 MB, bis 3000 Dateien) sowie PDF (bis 512 MB). Empfohlen sind
etwa 300 dpi – genau das liefert der Fraktur-Korrektor.

<!-- Platz für ein Bildschirmfoto des Upload-Fensters -->

### 4. Die Zeilen finden lassen (Layout)

Dieser Schritt wird gern übersehen, ist aber wichtig: Er zeichnet die Grundlinien, an denen entlang später
gelesen wird. Bei der Texterkennung läuft er nicht zuverlässig mit.

1. Im Dokument oben links das Kästchen anklicken, das **alle Seiten auswählt**.
2. Auf **„Process with AI"**.
3. Oben **„Layout Recognition"** wählen und den Auftrag starten.

Blättern Sie danach eine Seite durch: Über jeder Textzeile sollte eine Linie liegen. Sitzen die Linien schief
oder fehlen sie, hilft meist ein besseres Bild (ScanTailor) mehr als eine andere Einstellung.

### 5. Den Text erkennen lassen

1. Wieder **alle Seiten auswählen** und auf **„Process with AI"**.
2. Der Bereich **„Text Recognition"** ist schon offen. Im Suchfeld ein Modell suchen:

   | Modell | wofür |
   |---|---|
   | **Transkribus Print M1** | alle Drucke, Fraktur und Antiqua – die sichere Wahl |
   | **ONB_Newseye_GT_M1+** | deutsche Fraktur, spätes 18. bis Mitte 20. Jahrhundert |
   | **NZZ Gold Standard M1+** | deutsche Fraktur, 18. bis 20. Jahrhundert |

   Im Zweifel *Transkribus Print M1*. Für ein Buch von 1850 bis 1940 lohnt ein Vergleich an zwei, drei Seiten.
3. Transkribus zeigt an, **wie viele Credits** der Auftrag kostet und wie viele Sie noch haben. Erst dann
4. auf **„Start recognition"**.

**Danach dürfen Sie den Rechner ausschalten.** Die Erkennung läuft auf den Servern von READ-COOP in
Innsbruck, nicht bei Ihnen; Ihr Computer wird dafür nicht gebraucht. Nur beim Hochladen (Schritt 3) muss er
an bleiben, bis der Balken durchgelaufen ist.

Je nach Andrang dauert die Erkennung Minuten bis Stunden. Für ein ganzes Buch geben Sie den Auftrag am besten
abends und sehen am nächsten Morgen nach: Den Stand finden Sie unter **„AI Lab"**, das fertige Ergebnis
außerdem im Dokument selbst.

<!-- Platz für ein Bildschirmfoto der Modellauswahl -->

### 6. Das Ergebnis herunterladen

1. In der Sammlung das Dokument (oder alle Seiten) auswählen.
2. Oben auf den Knopf **„Action"** und darin auf **„Export"**.
3. Als Format **„Page XML"** wählen – nicht PDF, nicht Word. Darin stecken die Zeilen samt ihrer Lage im Bild,
   und genau das braucht der Fraktur-Korrektor.
4. Auf **„Start export"**.
5. Sie bekommen eine E-Mail mit einem Link (zwei Wochen gültig). Ohne E-Mail: links unter
   **„Uploads & downloads"** beim fertigen Export auf die drei Punkte und **„Download"**.

Sie erhalten eine **ZIP-Datei**. Die Bilder brauchen Sie nicht mitzuexportieren, wenn das Buch schon im
Fraktur-Korrektor liegt – beim Öffnen schlägt das Programm Ihren vorhandenen Bilderordner vor.

### 7. Zurück in den Fraktur-Korrektor

**Liegt das Buch schon in Ihrer Bibliothek** – weil Sie es vorher mit Tesseract eingelesen haben –, dann
gehört der Text dorthin und nicht in ein neues Buch: in der Bibliothek beim Buch auf
**Transkribus-Text einlesen** klicken und die ZIP-Datei wählen. Ihre Seitenbilder bleiben, wo sie sind; Sie
müssen nichts suchen und nichts doppelt anlegen. Das Programm sagt Ihnen danach, wie viele Seiten es ersetzt
hat und wie es sie zugeordnet hat.

**Ist es ein neues Buch:** Bibliothek → **Öffnen …** → **Datei wählen …** → die ZIP-Datei. Entpacken müssen
Sie sie nicht; das Programm erkennt den Export und fragt gegebenenfalls nach den passenden Seitenbildern.
Einzelheiten: [Ein Buch öffnen](add-book.md).

## Danach

Beim Import trennt das Programm Kopfzeilen und Fußnoten ab und markiert unbekannte Wörter rot. Typische
Verwechslungen der Fraktur (`ber` statt „der“, `bie` statt „die“, `Bolk` statt „Volk“) beheben Sie am
schnellsten mit der **Serienkorrektur** (`F9`) – siehe [Bedienung](usage.md).

## Tesseract oder Transkribus?

| | Tesseract (eingebaut) | Transkribus |
|---|---|---|
| Kosten | kostenlos | 50 Credits im Monat frei, ein ganzes Buch kostet Geld |
| Datenschutz | alles bleibt auf Ihrem Rechner | Bilder werden hochgeladen |
| Aufwand | ein Klick | Konto, Hochladen, Warten, Export |
| Qualität bei sauberem Scan | gut | sehr gut |
| Qualität bei mäßigem Scan (Handyfotos, gewölbte Seiten) | oft schwach | meist noch gut |

Faustregel: Erst mit Tesseract einlesen. Zeigt die Ampel Grün, sind Sie fertig. Bei Gelb oder Rot lohnt sich
für ein ganzes Buch der Weg über Transkribus.
