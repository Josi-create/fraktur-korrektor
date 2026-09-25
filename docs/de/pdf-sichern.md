# Ein Buch als PDF sichern

Ein Buch des Fraktur-Korrektors ist ein Ordner mit vielen Dateien: Seitenbilder, eine Textdatei je Seite,
Ihre Wortliste, das Lesezeichen, das Protokoll Ihrer Korrekturen. Um ein Buch **mitzunehmen** – auf den Laptop, zu
einem Kollegen, in eine Sicherung –, packt das Programm alles in **eine einzige PDF-Datei**.

## Was in dem PDF steckt

| | |
|---|---|
| **Seitenbilder** | Jede Buchseite ist eine PDF-Seite, das Bild unverändert – nichts wird neu berechnet oder verkleinert. |
| **Der Text** | liegt unsichtbar über dem Bild, Zeile für Zeile an der richtigen Stelle. In jedem PDF-Reader können Sie damit **suchen, Text kopieren** oder sich das Buch **vorlesen** lassen – mit Ihren Korrekturen. |
| **Inhaltsverzeichnis** | Die Überschriften, die Sie mit `H` ausgezeichnet haben, stehen im Inhaltsverzeichnis des PDFs (in der Seitenleiste des PDF-Readers, oft „Lesezeichen“ genannt) – ein Klick springt zum Kapitel. |
| **Ihr Arbeitsstand** | hängt als Anhang `fraktur-korrektor.zip` im PDF: die Texte aller Seiten, die Lage der Zeilen im Bild, Wortliste, Lesezeichen, Korrekturprotokoll, Erscheinungsjahr und Rechtschreibung. Acrobat und Firefox zeigen den Anhang in der Seitenleiste; andere Reader lassen ihn einfach unbeachtet. |

Das PDF lässt sich also mit jedem Programm lesen, das PDF kann – und der Fraktur-Korrektor macht daraus wieder
ein Buch, in dem Sie genau dort weiterarbeiten, wo Sie aufgehört haben.

## So sichern Sie

1. In der **Bibliothek** beim Buch auf **Als PDF sichern** klicken – oder in der Leseansicht oben auf **Sichern …**
   und dort auf **Als PDF sichern**.
2. Das PDF kommt in den Ordner, in dem auch der Buchordner liegt. Soll es gleich auf einen USB-Stick oder in
   einen Cloud-Ordner, wählen Sie dort einen anderen Ordner.
3. **PDF schreiben.** Bei einem Buch mit 300 Seiten dauert das wenige Sekunden. Danach zeigt das Programm, wo die
   Datei liegt, und öffnet auf Wunsch den Ordner.

Das PDF heißt wie das Buch. Sichern Sie dasselbe Buch später noch einmal an dieselbe Stelle, wird das alte PDF
ersetzt – es stammt ja vom selben Buch. Eine fremde Datei gleichen Namens wird nie überschrieben; dann heißt das
neue PDF „… (2).pdf“.

## So lesen Sie es auf einem anderen Rechner ein

1. Fraktur-Korrektor starten, **Öffnen …**, das PDF wählen.
2. Das Programm erkennt den Anhang und zeigt „gesichertes Buch (PDF)“ mit Datum und Zahl der Korrekturen.
3. **Buch übernehmen** legt das Buch im Bücherordner an – mit Seitenbildern, Text, Wortliste und Lesezeichen –
   und trägt es in die Bibliothek ein.

Gibt es dort schon ein Buch dieses Namens, entsteht ein zweites mit dem Zusatz „(2)“; nichts wird
überschrieben.

## Auf zwei Rechnern arbeiten: das Buch aktualisieren

Der übliche Ablauf: am PC begonnen, als PDF gesichert, am Laptop eingelesen und dort weitergearbeitet, wieder
gesichert – und zurück am PC soll es im **vorhandenen** Buch weitergehen, nicht in einer Kopie „(2)“.

Das Programm erkennt beim Öffnen des PDF, dass dasselbe Buch schon in der Bibliothek liegt (jedes Buch trägt eine
feste Kennung, die im PDF mitreist), und sieht nach, ob hier seit dem Sichern etwas geschehen ist:

- **Nichts geschehen** – alles, was hier im Korrekturprotokoll steht, steht auch im PDF: Dann lautet die Empfehlung
  **Vorhandenes Buch aktualisieren**. Das Buch bekommt Text, Seitenbilder, Wortliste, Lesezeichen und Protokoll
  aus dem PDF; die bisherige Fassung wird vorher gesichert (`vorher-<Datum>.zip`, zurückzuholen über **Frühere
  Fassung**). Wer lieber ein zweites Buch möchte, wählt das daneben.
- **An beiden Stellen weitergearbeitet** – hier wie dort neue Korrekturen: Dann lautet die Empfehlung
  **Zusammenführen**. Das Programm spielt die Änderungen aus dem PDF auf das vorhandene Buch nach, Zeile für Zeile –
  Korrekturen, geteilte und verbundene Zeilen, Fußnotenstriche –, vereinigt die Wortlisten und übernimmt das
  Lesezeichen, das weiter hinten liegt. Ihre hiesigen Korrekturen bleiben. Seitenbilder kommen nur für Seiten, die
  hier keines haben. Auch hier wird die bisherige Fassung vorher gesichert. Am Ende sagt das Programm, wie viele
  Änderungen es übernommen hat und wie viele Zeilen Sie ansehen müssen.

  **Zeilen ansehen:** Wurde dieselbe Zeile an beiden Stellen anders berichtigt, entscheidet das Programm nicht
  selbst. Die hiesige Fassung bleibt stehen, die Zeile ist in der Leseansicht orange umrandet, und oben in der
  Kopfleiste steht, wie viele solcher Zeilen es gibt. Die Taste `Z` springt zur nächsten und zeigt beide Fassungen:
  `1` behält die hiesige, `2` übernimmt die vom anderen Rechner, `Esc` verschiebt die Entscheidung. Wurde eine
  Zeile dort geteilt oder verbunden, hier aber inzwischen anders berichtigt, zeigt das Programm, was dort geschah,
  und Sie erledigen es bei Bedarf mit den gewohnten Tasten.

  Zusammengeführt werden die Änderungen, die das Programm selbst festgehalten hat (Korrekturprotokoll). Was in einem
  anderen Editor direkt in den Textdateien geändert wurde, kennt es nicht: Beim Aktualisieren ersetzt der Stand aus
  dem PDF auch das (es liegt dann nur noch in der Sicherung), beim Zusammenführen bleibt es hier erhalten, kommt aber
  vom anderen Rechner nicht mit.

## Was Sie wissen sollten

- Das PDF ist etwa so groß wie der Buchordner – die Seitenbilder machen den Löwenanteil aus.
- Der unsichtbare Text sitzt **zeilengenau**: Beim Suchen springt der Reader zur richtigen Zeile, die Markierung
  beim Ziehen mit der Maus trifft aber nicht jedes Wort genau.
- Ein Buch ohne Seitenbilder (etwa aus einem EPUB) bekommt Seiten mit sichtbarem Text.
- Zum Lesen auf E-Book-Reader, Tablet oder Handy gibt es [Als E-Book sichern](epub-sichern.md); dort lässt sich das PDF
  gleich daneben sichern.
- Nach dem Zusammenführen enthält das Korrekturprotokoll auch die Einträge vom anderen Rechner. Sichern Sie danach
  wieder als PDF und lesen es dort ein, genügt dort das einfache Aktualisieren – so pendelt ein Buch beliebig oft
  zwischen zwei Rechnern.
