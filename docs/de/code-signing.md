# Signatur und Datenschutz

Diese Seite erklärt, wer die Windows-Fassung des Fraktur-Korrektors signiert, nach welchen Regeln das geschieht und
was das Programm über das Netz überträgt. Sie ist zugleich die Richtlinie („Code signing policy“), die die SignPath
Foundation für ihre kostenlose Signatur verlangt.

## Was die Signatur bedeutet

Eine digitale Signatur ist ein Siegel auf der Programmdatei: Windows erkennt daran, von wem die Datei stammt und dass
sie seit dem Signieren niemand verändert hat. Die Windows-Fassung signiert die **SignPath Foundation**, eine
gemeinnützige Einrichtung, die Open-Source-Programme kostenlos signiert. Darum nennt Windows in seinen Meldungen und
in den Datei-Eigenschaften „SignPath Foundation“ als Herausgeber – das ist richtig so.

> Kostenlose Code-Signatur durch [SignPath.io](https://signpath.io), Zertifikat der
> [SignPath Foundation](https://signpath.org).
>
> *Free code signing provided by [SignPath.io](https://signpath.io), certificate by
> [SignPath Foundation](https://signpath.org).*

Ob eine heruntergeladene Datei signiert ist, zeigt Windows selbst: rechte Maustaste auf die Datei → *Eigenschaften* →
Reiter *Digitale Signaturen*. Die Mac-Fassung ist mit einem eigenen Zertifikat bei Apple signiert und notarisiert; die
Linux-Fassung ist nicht signiert.

## Regeln für das Signieren

- **Was signiert wird:** nur die beiden Dateien, die aus dem Quelltext dieses Projekts entstehen – das Programm
  `Fraktur-Korrektor.exe` und der Installer `Fraktur-Korrektor_Setup.exe`. Was aus anderen Open-Source-Projekten
  mitgeliefert wird (Python, Tesseract, PyMuPDF und weitere Bibliotheken), bleibt so, wie deren Herausgeber es
  ausliefern.
- **Wie gebaut wird:** nur von GitHub Actions aus dem öffentlichen
  [Quelltext](https://github.com/Josi-create/fraktur-korrektor), und zwar aus einer Versionsmarke (Tag). Der
  Ablauf steht in
  [release.yml](https://github.com/Josi-create/fraktur-korrektor/blob/main/.github/workflows/release.yml). Auf
  einem eigenen Rechner gebaute Dateien werden nicht signiert.
- **Freigabe:** Jede Signatur einer Version wird von Hand freigegeben.
- **Anmeldung:** Wer mitwirkt, meldet sich bei GitHub und bei SignPath mit zwei Faktoren an.

| Rolle | Aufgabe | Wer |
|---|---|---|
| Autoren | dürfen den Quelltext ohne weitere Prüfung ändern | [Johannes Wack](https://github.com/Josi-create) |
| Prüfer | sehen jeden Beitrag von außen (Pull Request) vor der Übernahme durch | [Johannes Wack](https://github.com/Josi-create) |
| Freigabe | entscheidet, ob eine Version signiert wird | [Johannes Wack](https://github.com/Josi-create) |

## Datenschutz

Dieses Programm überträgt keine Informationen an andere Rechner im Netz, außer Sie verlangen es ausdrücklich. Es
läuft auf Ihrem Rechner; Bücher, Texte, Korrekturen und Einstellungen bleiben dort. Es gibt keine Nutzungsstatistik,
keine Abfrage nach Updates und keine Wortprüfung im Netz. Von anderen Geräten im Heimnetz aus ist es nur erreichbar,
wenn Sie das eigens einschalten (etwa zum [Lesen auf dem Tablet](usage.md)).

Eine Ausnahme: Unter Linux und beim Start aus dem Quelltext lädt das Programm beim ersten Einlesen mit Texterkennung
das Frakturmodell für Tesseract von der Universitätsbibliothek Mannheim herunter. Abgerufen wird dabei nur diese
Modelldatei; über Sie oder Ihre Bücher wird nichts übertragen. Die Fassungen für Windows und Mac bringen das Modell
schon mit.

Links, die Sie anklicken – zur Hilfe im Netz, zu GitHub, zur Spendenseite –, öffnet Ihr Browser wie jede andere
Seite. Mehr zur Sicherheit: [SECURITY.md](https://github.com/Josi-create/fraktur-korrektor/blob/main/SECURITY.md).
