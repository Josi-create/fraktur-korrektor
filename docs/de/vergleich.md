# Andere Programme im Vergleich

*Entwurf vom 24. September 2026 – Angaben zu fremden Programmen bitte prüfen.*

Es gibt eine ganze Reihe von Programmen, die Fraktur lesen oder beim Korrigieren helfen. Keines ist für alles
das beste; die meisten lassen sich mit dem Fraktur-Korrektor verbinden. Diese Seite soll Ihnen die Wahl
erleichtern – sie ist keine Werbung, und sie ist eine Momentaufnahme: Alle Angaben stammen von den
offiziellen Seiten der Programme, **Stand 24. September 2026**, und können sich ändern. Was wir nicht selbst
nachgesehen haben, ist als *nicht geprüft* gekennzeichnet. Die Fraktur-Qualität ist nur beschrieben, nicht
gemessen – seriöse Zahlen gibt es nur je Buch und je Scan.

## Wofür welches Werkzeug passt

- **Sie haben ein gescanntes Buch und wollen es lesen und korrigieren:** Erst mit dem eingebauten
  [Tesseract](pdf-import.md) einlesen. Zeigt die Ampel Grün, sind Sie fertig. Sonst
  [Transkribus](transkribus.md) – bequem, gut bei Fraktur, aber im Internet und ab einem gewissen Umfang gegen
  Geld.
- **Sie besitzen ABBYY FineReader** oder haben ein PDF, das damit oder von einer Bibliothek schon erkannt
  wurde: Der Fraktur-Korrektor übernimmt die Textebene eines durchsuchbaren PDF in Sekunden
  ([Text übernehmen](pdf-import.md)).
- **Sie arbeiten an einer Einrichtung**, die eScriptorium oder OCR-D betreibt, oder Sie wollen eigene Modelle
  trainieren: Das sind die richtigen Werkzeuge dafür – mit Serverinstallation und Einarbeitung. Ihr Ergebnis
  (PAGE XML, ALTO, hOCR) lässt sich hier weiterlesen ([Text aus einer Bibliothek](add-book.md)).
- **Sie wollen die Vorlage verbessern**, nicht den Text: Der Fraktur-Korrektor teilt Doppelseiten und richtet
  gerade; für Wölbung und Flecken gibt es [ScanTailor](install-tools.md).
- **Sie haben schon Text** (EPUB, Textdatei, Transkribus-Export) und wollen ihn gegen den Scan lesen:
  genau dafür ist der Fraktur-Korrektor da ([Ein Buch öffnen](add-book.md)).

**Was zusammenpasst:** Transkribus → *Page XML* → hier einlesen. ABBYY oder OCRmyPDF → durchsuchbares PDF → hier
*Text übernehmen*. Tesseract, gImageReader, OCR-D, eScriptorium → hOCR oder ALTO → hier
*Erkannten Text einlesen*. Ein EPUB (etwa ein früherer eigener Durchgang) → neben das PDF legen → hier öffnen.
Der Fraktur-Korrektor selbst schreibt Textdateien je Seite und ein [PDF mit Textebene](pdf-sichern.md), das jedes
andere Programm lesen kann.

## Die Tabelle

Lesehilfe: *Fraktur* meint, ob und wie das Programm Frakturdruck erkennt; *Korrigieren* meint, wie bequem man
Fehler nachträglich ausbessert; *Offline* meint, ob Ihre Scans auf Ihrem Rechner bleiben.

| Programm | Preis | Fraktur | Korrigieren | Offline / Datenschutz | Lernkurve | Export | Plattform |
|---|---|---|---|---|---|---|---|
| **ABBYY FineReader PDF** (Version 16) | Abo: Standard 99 €/Jahr, Corporate 165 €/Jahr, Mac 69 €/Jahr; auch monatlich (16 €) und 3 Jahre | Sprache „Old German“ für Textur, Fraktur und Schwabacher laut Hilfe zu Version 16; Ergebnis nicht selbst geprüft. ABBYY rät, nur diese eine Sprache zu wählen | Eingebauter Editor mit Prüfansicht (laut Website, nicht geprüft) | Läuft auf dem eigenen Rechner | Gering – ein Büroprogramm | Durchsuchbares PDF, Word, Text u. a. | Windows, Mac (Fraktur auch am Mac laut ABBYY-Hilfeartikel) |
| **Transkribus** (READ-COOP, Innsbruck) | Kostenlos 50 Credits/Monat; Scholar 99 €/Jahr; 250 Credits 59,50 €; Druckseite 0,5 Credit | Sehr gut: öffentliche Modelle für deutsche Fraktur mit 0,5–2,2 % Zeichenfehlern auf ihren Prüfseiten (Angaben der Modellseiten) | Web-Editor, Zeile im Bild; für ein ganzes Buch mühsamer als ein Tastaturprogramm | **Nein** – Bilder liegen auf Servern in Österreich | Mittel – Konto, Sammlung, Aufträge, Export | Page XML, Text, Word, PDF frei; ALTO, METS, TEI nur bezahlt | Browser |
| **Tesseract** (5.5.3, Juli 2026) | Kostenlos, Apache-Lizenz | Brauchbar bis gut bei sauberen, geraden Scans mit einem Fraktur-Modell (frak2021 der UB Mannheim, `deu_latf`); empfindlich gegen Schieflage, Wölbung, Handyfotos – unsere Erfahrung, siehe [Ampel](pdf-import.md) | Keines – reine Erkennung | Ja | Hoch (Kommandozeile); im Fraktur-Korrektor eingebaut: ein Klick | Text, hOCR, ALTO, PDF, PAGE XML | Windows, Mac, Linux |
| **OCR4all** mit LAREX (0.6.1, Januar 2026) | Kostenlos, MIT-Lizenz | Für frühe Drucke gebaut; Erkennung mit Calamari, Kraken; Qualität nicht geprüft; eigene Modelle trainierbar | Eingebauter Korrekturteil für Trainingstexte, mit Bildschirmtastatur für Sonderzeichen | Ja – läuft in Docker auf dem eigenen Rechner | Hoch – Docker, mehrstufiger Arbeitsablauf, gedacht für Projekte | PAGE XML, Text | Docker (Windows, Mac, Linux) |
| **eScriptorium** mit Kraken | Kostenlos, MIT (eScriptorium) und Apache (Kraken) | Modelle für deutsche Drucke der UB Mannheim laut deren Anleitung (`german_print`); Qualität nicht geprüft; eigene Modelle trainierbar | Web-Editor, Zeile im Bild | Ja, wenn Sie oder Ihre Einrichtung es selbst betreiben (Server) | Hoch – Serverinstallation; als Nutzer einer Instanz mittel | Text, PAGE XML, ALTO | Server unter Linux; Kraken ohne Windows |
| **OCR-D** | Kostenlos, Apache-Lizenz | Werkzeugkasten für Bibliotheken (DFG-gefördert); Qualität hängt vom gewählten Ablauf und Modell ab; nicht geprüft | Keine eigene Oberfläche | Ja | Sehr hoch – Kommandozeile, Docker, Ubuntu | PAGE XML, ALTO, METS | Linux/Docker; Windows nur über WSL, Mac über Homebrew (laut Setup-Guide) |
| **gImageReader** (3.4.3, August 2025) | Kostenlos, GPL | Dieselbe Erkennung wie Tesseract; Fraktur-Modell muss man selbst installieren | Text neben dem Bild, Rechtschreibprüfung, hOCR-Editor | Ja | Gering bis mittel | Text, hOCR, PDF | Windows, Linux (kein Mac laut README) |
| **PoCoTo** (CIS München) | Kostenlos, BSD-Lizenz | Keine Erkennung – nur Nachkorrektur | Serienkorrektur ganzer Fehlerreihen (Forschungswerkzeug aus dem Projekt IMPACT) | Ja (Java) | Mittel bis hoch | nicht geprüft | Java (Windows, Mac, Linux) – **letzte Änderung Mai 2017**, praktisch nicht mehr gepflegt |
| **Fraktur-Korrektor** (dieses Programm) | Kostenlos, GPL | Erkennt selbst nichts: Tesseract eingebaut, Transkribus per Import; Ampel schätzt die Güte | Das ist sein Zweck: Tastatur, rote Wörter, Serienkorrektur, Wörterbuch je Epoche | Ja | Gering | Text je Seite, PDF mit Textebene | Windows, Mac, Linux |

## Quellen

Alle abgerufen am 24. September 2026.

- ABBYY: Preise <https://pdf.abbyy.com/pricing/>; Gotisch/Fraktur in Version 16
  <https://help.abbyy.com/en-us/finereader/16/user_guide/gothicrecognition/>; Mac-Artikel
  <https://support.abbyy.com/hc/en-us/articles/4417503390611> (Seite verweigerte den automatischen Abruf – nur
  Titel und Suchtreffer geprüft).
- Transkribus: Pläne und Credits <https://www.transkribus.org/plans>, <https://help.transkribus.org/credit-system>;
  Modelle <https://www.transkribus.org/models/transkribus-print-multi-language-dutch-german-english-finnish-french-swedish-etc>,
  <https://www.transkribus.org/models/german-fraktur-19th-20th-century>,
  <https://www.transkribus.org/models/german-fraktur-18th-20th-century>; Export
  <https://help.transkribus.org/downloading>.
- Tesseract: <https://github.com/tesseract-ocr/tesseract/releases>; Windows-Installer und frak2021
  <https://github.com/UB-Mannheim/tesseract/wiki>.
- OCR4all: <https://www.ocr4all.org/>, <https://github.com/OCR4all/OCR4all/releases>,
  <https://www.ocr4all.org/guide/user-guide/workflow>.
- eScriptorium und Kraken: <https://gitlab.com/scripta/escriptorium>, <https://escriptorium.readthedocs.io/>,
  <https://kraken.re/>, Anleitung der UB Mannheim <https://ub-mannheim.github.io/eScriptorium_Dokumentation/>.
- OCR-D: <https://ocr-d.de/en/>, <https://ocr-d.de/en/setup>, <https://github.com/OCR-D/core>.
- gImageReader: <https://github.com/manisandro/gImageReader>.
- PoCoTo: <https://github.com/cisocrgroup/PoCoTo> (Lizenz, letzte Änderung im Commit-Verlauf).
