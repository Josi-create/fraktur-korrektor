# Ein Buch als E-Book sichern

Das PDF zeigt Ihr Buch so, wie es gedruckt wurde: Seite für Seite, als Bild. Zum **Lesen auf dem E-Book-Reader, dem
Tablet oder dem Handy** eignet sich ein E-Book besser. Darin fließt der Text und passt sich jeder Bildschirmgröße und
Schriftgröße an. Der Fraktur-Korrektor schreibt dafür eine Datei im verbreiteten Format **EPUB**, und zwar mit dem
Text, den Sie korrigiert haben.

## Was im E-Book steckt

| | |
|---|---|
| **Ihr korrigierter Text** | als fließender Text in Absätzen. Getrennte Wörter am Zeilenende und über die Seitengrenze werden wieder zusammengesetzt. Kopfzeile, Kolumnentitel und Seitenzahl unten gehören nicht zum Text und fehlen. |
| **Inhaltsverzeichnis** | aus den Überschriften, die Sie mit `H` ausgezeichnet haben: in der Lese-App anklickbar, dazu eine Seite **Inhalt** gleich nach der Titelseite, mit der gedruckten Seitenzahl jedes Kapitels. Jedes Kapitel der obersten Stufe beginnt auf einer neuen Seite. |
| **Seitenzahlen der Druckausgabe** | An jedem Seitenwechsel steht klein und grau die Seitenzahl der gedruckten Ausgabe, etwa **[127]**. So können Sie auch aus dem E-Book nach dem Buch zitieren. Lese-Apps, die das unterstützen, springen damit auch direkt zu einer Seite, etwa Thorium Reader mit *Gehe zu Seite*. |
| **Fußnoten** | Das hochgestellte Fußnotenzeichen im Text wird ein Link. Viele Lese-Apps zeigen die Fußnote beim Antippen in einem kleinen Fenster, andere darunter. |
| **Titelseite und Umschlag** | eine Titelseite mit Titel, Autor und Erscheinungsjahr. Die erste Scanseite wird das Umschlagbild, das Lese-Apps in der Bücherliste zeigen. |

Verse, Dialoge, Namenslisten und Register behalten ihre Zeilen: Wo fast jede Zeile groß beginnt und kaum eine bis zum
Rand reicht, bleibt jede gedruckte Zeile eine Zeile. Tabellen, die Sie mit `T` ausgezeichnet haben, erscheinen als
Tabellen.

## So sichern Sie

1. In der **Bibliothek** beim Buch auf **Als E-Book sichern** klicken, oder in der Leseansicht oben auf **Sichern …**
   und dort auf **Als E-Book sichern**.
2. Der Dialog zeigt zuerst, was ins E-Book kommt: wie viele Überschriften, Absätze und Fußnoten, auf wie vielen Seiten
   eine gedruckte Seitenzahl steht. Fehlt etwas, steht darunter, mit welcher Taste Sie es nachholen (siehe unten).
3. **Autor:** erscheint in der Bücherliste der Lese-App, die danach sortiert. Das Programm merkt sich den Namen für das
   nächste Mal. Der Titel ist der Name des Buchs in der Bibliothek; ändern können Sie ihn dort mit *Umbenennen*.
4. **Das PDF gleich daneben sichern** ist vorausgewählt. Dann liegen zwei Dateien mit demselben Namen im Ordner: das
   E-Book zum Lesen und das [gesicherte PDF](pdf-sichern.md) mit Seitenbildern und Ihrem ganzen Arbeitsstand.
5. **E-Book schreiben.** Das dauert auch bei einem dicken Buch nur Sekunden (mit dem PDF etwas länger).

Die Datei heißt wie das Buch und kommt neben den Buchordner, wenn Sie keinen anderen Ordner wählen. Ein E-Book, das
schon von diesem Buch gesichert wurde, wird ersetzt; eine fremde Datei gleichen Namens bleibt unangetastet, dann heißen
E-Book und PDF „… (2)“.

## Das E-Book lesen

- **Mac, iPhone, iPad:** in der App *Bücher*; auf dem Mac genügt ein Doppelklick auf die Datei.
- **Windows, Mac, Linux:** Das kostenlose Programm [Thorium Reader](https://www.edrlab.org/software/thorium-reader/)
  liest E-Books und zeigt die gedruckten Seitenzahlen unter *Gehe zu Seite*. Auch
  [Calibre](https://calibre-ebook.com/) öffnet sie.
- **E-Book-Reader** wie Tolino oder Kobo: die Datei per USB-Kabel auf das Gerät kopieren.
- **Kindle:** über Amazons Dienst [Send to Kindle](https://www.amazon.com/sendtokindle), der EPUB-Dateien annimmt
  (Stand September 2026).

## E-Book und PDF zusammen

Öffnen Sie später das E-Book im Fraktur-Korrektor, und das gesicherte PDF desselben Buchs liegt daneben, dann empfiehlt
das Programm das **PDF**. Nur darin stecken Seitenbilder, Zeilenlage und Ihr Arbeitsstand; aus dem PDF entsteht das
Buch wieder so, wie Sie es verlassen haben. Das E-Book allein würde als Buch ohne Seitenbilder geöffnet.

So können Sie beide Dateien zusammen weitergeben oder auf einen anderen Rechner mitnehmen: Gelesen wird im E-Book,
weitergearbeitet mit dem PDF.

## Damit das E-Book gut wird

Ein E-Book ist nur so gut gegliedert wie das Buch, aus dem es entsteht. Der Dialog nennt, was fehlt:

| Hinweis im Dialog | Was fehlt | Was hilft |
|---|---|---|
| Noch keine Überschriften | Ohne sie hat das E-Book kein Inhaltsverzeichnis und keine Kapitel. | Kapitelanfänge beim Lesen mit `H` auszeichnen, siehe [Bedienung](usage.md). Die Übersicht `I` zeigt alle Überschriften mit Seitenzahl. |
| Keine Absätze gesetzt | Das Programm trennt Absätze dann nur nach einer Regel: nach einer kurzen Zeile, die mit einem Satzzeichen endet. | Absatzanfänge mit `A` setzen. Meist hat das Programm sie beim ersten Öffnen schon am Einzug erkannt. |
| Fußnoten ohne Fußnotenzeichen im Text | Die Texterkennung hat das hochgestellte Zeichen verschluckt oder als `*`, `°` oder an das Wort geklebte Ziffer gelesen. Diese Fußnoten stehen im E-Book ohne Link unter dem Absatz. | Beim Lesen markiert das Programm vermutete Fußnotenzeichen blau; `Leertaste` springt hin, `Enter` stellt die Nummer hoch. Hochgestellt wird sie zum Link. |
| Keine gedruckten Seitenzahlen erkannt | Die Texterkennung hat oben und unten keine Seitenzahl gelesen. | Die Seitenzahl in der Kopfzeile nachtragen (`F2` auf der obersten Zeile). Einzelne Seiten ohne Zahl, etwa Kapitelanfänge, ergänzt das Programm aus den Nachbarseiten. |

Verknüpft werden Fußnotenzeichen, die hochgestellt sind (`<sup>12</sup>`), die wie in älteren Büchern als „12)“ hinter
dem Wort stehen, ein Stern am Wort und am Wort klebende Ziffern, zu denen es auf derselben Seite eine Fußnote mit dieser
Nummer gibt. Eine Fußnote, die unten auf der nächsten Seite weiterläuft, wird zusammengesetzt.

## Was (noch) nicht geht

- **Abbildungen und Tafeln** aus dem Scan kommen nicht ins E-Book; eine Seite ohne Text trägt nur ihre Seitenzahl.
- Das E-Book lässt sich nicht bearbeiten und zurückholen. Weitergearbeitet wird im Fraktur-Korrektor; danach sichern
  Sie einfach neu.
