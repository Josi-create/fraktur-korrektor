# Wörterbuch

`de_DE_OLDSPELL/` – Hunspell-Wörterbuch für die deutsche Rechtschreibung von 1901, unverändert aus der
LibreOffice-Erweiterung „German (de-DE-1901) old spelling dictionaries“, Version 2017-06-22
(<https://extensions.libreoffice.org/en/extensions/show/german-de-de-1901-old-spelling-dictionaries>).
Copyright © 1998–2017 Björn Jacke, bearbeitet von Rüdiger Brünner, veröffentlicht von Karl Zeiler.
Lizenz: GPLv2, GPLv3 oder OASIS – die Lizenztexte liegen im Ordner.

`de_DE_frami/` – Hunspell-Wörterbuch für die neue deutsche Rechtschreibung (ab 1996), unverändert aus den
LibreOffice-Wörterbüchern (<https://github.com/LibreOffice/dictionaries/tree/master/de>), Version 20161207+frami20170109.
Copyright © 1998–2016 Björn Jacke, Ergänzungen von Franz Michael Baumann. Lizenz: GPLv2 oder GPLv3 – die Lizenztexte
liegen im Ordner.

Welche Rechtschreibung für ein Buch gilt, lässt sich im Programm je Buch wählen (Taste `D`); nach dem Einlesen schlägt das
Programm sie anhand des Erscheinungsjahrs vor. Schreibungen vor 1901 (Thür, seyn, giebt) erkennt es über Regeln in
`korrlib.py`, nicht über ein Wörterbuch.

`zusatz.txt` und `fallen.txt` gehören zum Fraktur-Korrektor: zusätzlich gültige Wörter (Abkürzungen) und
Wörter, die trotz Wörterbucheintrag immer markiert werden, weil sie fast immer OCR-Fehler sind.
Ergänzungen sind willkommen.

Ein anderes Wörterbuch lässt sich mit `--dic <pfad>`, der Umgebungsvariable `FRAKTUR_DIC` oder dem Eintrag
`"dic"` in `~/.fraktur-korrektor/config.json` wählen.
