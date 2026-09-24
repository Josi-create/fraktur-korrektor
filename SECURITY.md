# Sicherheit

*English version: [SECURITY.en.md](SECURITY.en.md)*

## Was das Programm tut – und was nicht

Der Fraktur-Korrektor ist ein lokales Programm: Ein kleiner Server auf dem eigenen Rechner, der Browser ist nur das
Fenster. Beim gewöhnlichen Start lauscht er ausschließlich auf `127.0.0.1` und ist von keinem anderen Rechner aus zu
erreichen. Er lädt nichts aus dem Internet nach und schickt nichts weg – weder Texte noch Wörter zur Prüfung noch
Nutzungsdaten. Die einzige Ausnahme ist das Fraktur-Modell für Tesseract, das auf ausdrücklichen Wunsch von der
UB Mannheim geholt wird (bei den fertigen Programmen ist es schon dabei).

Alle Daten bleiben in Buchordnern auf der Platte und in `~/.fraktur-korrektor` (Einstellungen, Zwischenspeicher der
Wortprüfung). Was ein Buchordner enthält, steht in der [README](README.md#buchordner); nichts davon ist verschlüsselt,
nichts davon verlässt den Rechner.

### `--lan`

Mit `--lan` ist das Programm auch von anderen Rechnern im lokalen Netz erreichbar, etwa vom Tablet auf dem Sofa.
Dabei gilt:

- **Es gibt keinen Passwortschutz.** Wer im selben Netz ist, kann lesen und korrigieren. `--lan` ist nur für das
  eigene Heimnetz gedacht, nicht für Hotel-, Uni- oder Firmennetze und erst recht nicht für eine Freigabe ins
  Internet (Portweiterleitung).
- **Die Bibliothek lässt sich nur am Rechner selbst verändern.** Ordner öffnen, Dateien einlesen, der Dateidialog,
  das Verwerfen von Büchern, ScanTailor starten, Seiten ersetzen, Notizordner festlegen – alles, was Dateien
  außerhalb eines Buchordners liest oder schreibt oder Programme startet, beantwortet der Server für Anfragen aus dem
  Netz mit 403 (`nur_lokal`). Aus dem Netz gehen nur Lesen und Korrigieren der bereits geöffneten Bücher.
- Windows fragt beim ersten Start mit `--lan` nach der Firewall-Freigabe; „Private Netzwerke“ genügt.

Ein Zugriffsschutz für `--lan` steht auf der [ROADMAP](ROADMAP.md) unter „Später“.

### Was Sie selbst in der Hand haben

- **Buchordner und Scans** unterliegen dem Urheberrecht des jeweiligen Werks. Das Programm prüft das nicht; geben Sie
  Buchordner, gesicherte PDFs und Fehlerberichte mit Buchinhalten nur weiter, wenn Sie das dürfen.
- **Fertige Programme** nur von der [Seite der Veröffentlichungen](https://github.com/Josi-create/fraktur-korrektor/releases)
  laden. Die Mac-App ist signiert und notarisiert; Windows zeigt beim ersten Start noch die SmartScreen-Warnung
  (siehe [Häufige Fragen](docs/de/faq.md)).

## Unterstützte Versionen

Sicherheitskorrekturen gibt es für die jeweils neueste veröffentlichte Version. Ältere Versionen werden nicht
gepflegt; bitte aktualisieren Sie.

## Eine Sicherheitslücke melden

Wenn Sie glauben, eine Lücke gefunden zu haben, die andere gefährden könnte (etwa: aus dem LAN lassen sich trotz
Sperre Dateien lesen, ein präpariertes PDF oder EPUB führt beim Einlesen Code aus, eine Adresse erlaubt den Zugriff
außerhalb des Buchordners), melden Sie sie bitte **nicht öffentlich** als Issue, sondern:

1. **Bevorzugt** über GitHub: *Security → Report a vulnerability* auf der Seite des Repositorys (private Meldung an
   die Betreuung). Steht der Knopf bei Ihnen nicht zur Verfügung, dann:
2. über die im [GitHub-Profil des Betreuers](https://github.com/Josi-create) hinterlegte Adresse.

Bitte beschreiben Sie, wie sich die Lücke nachstellen lässt, mit welcher Version und auf welchem System. Sie
bekommen innerhalb von 14 Tagen eine Antwort; eine Korrektur erscheint als neue Version mit einem Hinweis im
[CHANGELOG](CHANGELOG.md). Wenn Sie genannt werden möchten, sagen Sie es dazu.

Alles andere – Abstürze, falsch rote Wörter, Meldungen, die Sie nicht verstehen – gehört als gewöhnlicher
[Fehlerbericht](../../issues/new/choose) ins Issue-System.
