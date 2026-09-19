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

1. **Konto anlegen** auf [transkribus.org](https://www.transkribus.org/) und anmelden.
2. **Sammlung anlegen** (Collection) und darin das **Dokument hochladen**. Hochgeladen werden Seitenbilder
   oder ein PDF – welche Dateien das bei Ihnen sind:
   - Haben Sie das Buch **schon im Fraktur-Korrektor eingelesen** – etwa nach der Aufbereitung mit ScanTailor –,
     nehmen Sie die Bilder aus dem Ordner **`img`** in Ihrem Buchordner. Das sind genau die aufbereiteten Seiten.
     Nach dem Einlesen nennt das Programm diesen Ordner; **Ordner zeigen …** öffnet ihn und legt den Pfad in die
     Zwischenablage. In Transkribus dann alle Bilder darin auswählen und hochladen.
   - Sonst genügt das **PDF** Ihres Scans; Transkribus zerlegt es selbst in Seiten.

   Tipp: Schlechte Scans vorher mit ScanTailor aufbereiten – siehe [PDF oder Bilder einlesen](pdf-import.md).
3. **Texterkennung starten.** Wählen Sie ein Modell für gedruckte Texte. Für deutsche Fraktur hat sich das
   öffentliche Modell **„Transkribus Print M1“** bewährt; es erkennt Fraktur und Antiqua. Die Layout-Erkennung
   (Zeilen finden) läuft dabei automatisch mit.
4. Warten, bis der Auftrag fertig ist (je nach Andrang Minuten bis Stunden; Sie bekommen eine Nachricht).
5. **Exportieren:** Dokument wählen → *Export*. Wichtig ist das Format **PAGE XML** (unter „Transkribus
   Document“). Haken Sie auch den Export der **Bilder** an, dann hat der Fraktur-Korrektor gleich die
   Seitenbilder. Sie erhalten einen Link zu einer **ZIP-Datei**.
6. Im Fraktur-Korrektor: Bibliothek → **Öffnen …** → **Datei wählen …** → die ZIP-Datei. Entpacken müssen Sie sie
   nicht; das Programm erkennt den Export. Einzelheiten: [Ein Buch öffnen](add-book.md).

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
