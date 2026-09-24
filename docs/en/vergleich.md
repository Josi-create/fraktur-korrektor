# Other programs compared

*Draft of 24 September 2026 – please check the statements about third-party programs.*

There is a whole range of programs that read Fraktur or help with correcting. None is the best at everything;
most of them can be combined with Fraktur-Korrektor. This page is meant to make the choice easier – it is not
advertising, and it is a snapshot: all statements come from the programs' official pages, **as of
24 September 2026**, and may change. What we did not look up ourselves is marked *not checked*. Fraktur quality
is described, not measured – serious figures only exist per book and per scan.

## Which tool for what

- **You have a scanned book and want to read and correct it:** read it in with the built-in
  [Tesseract](pdf-import.md) first. If the traffic light is green, you are done. Otherwise
  [Transkribus](transkribus.md) – convenient, good at Fraktur, but online and, beyond a certain volume, paid.
- **You own ABBYY FineReader**, or you have a PDF that was already recognised with it or by a library:
  Fraktur-Korrektor takes over the text layer of a searchable PDF in seconds
  ([using the existing text](pdf-import.md)).
- **You work at an institution** that runs eScriptorium or OCR-D, or you want to train your own models: those
  are the right tools for that – with a server installation and a learning period. Their result (PAGE XML,
  ALTO, hOCR) can be read on here ([text from a library](add-book.md)).
- **You want to improve the scan**, not the text: Fraktur-Korrektor splits double pages and straightens; for
  curvature and stains there is [ScanTailor](install-tools.md).
- **You already have text** (EPUB, text file, Transkribus export) and want to read it against the scan: that
  is exactly what Fraktur-Korrektor is for ([Opening a book](add-book.md)).

**What fits together:** Transkribus → *Page XML* → read in here. ABBYY or OCRmyPDF → searchable PDF → *use the
existing text* here. Tesseract, gImageReader, OCR-D, eScriptorium → hOCR or ALTO → *Take in recognised text*
here. An EPUB (for instance an earlier run of your own) → put it next to the PDF → open here. Fraktur-Korrektor
itself writes text files per page and a [PDF with a text layer](pdf-sichern.md) that any other program can read.

## The table

How to read it: *Fraktur* means whether and how the program recognises Fraktur print; *Correcting* means how
comfortably you fix errors afterwards; *Offline* means whether your scans stay on your computer.

| Program | Price | Fraktur | Correcting | Offline / privacy | Learning curve | Export | Platform |
|---|---|---|---|---|---|---|---|
| **ABBYY FineReader PDF** (version 16) | Subscription: Standard €99/year, Corporate €165/year, Mac €69/year; also monthly (€16) and 3-year terms | Language “Old German” for Textur, Fraktur and Schwabacher according to the version 16 help; result not checked by us. ABBYY advises selecting only this one language | Built-in editor with verification view (according to the website, not checked) | Runs on your own computer | Low – an office program | Searchable PDF, Word, text and more | Windows, Mac (Fraktur on the Mac too, according to an ABBYY help article) |
| **Transkribus** (READ-COOP, Innsbruck) | Free: 50 credits/month; Scholar €99/year; 250 credits €59.50; a printed page 0.5 credit | Very good: public models for German Fraktur with 0.5–2.2 % character errors on their own test pages (figures from the model pages) | Web editor, line in the image; for a whole book more laborious than a keyboard program | **No** – images are stored on servers in Austria | Medium – account, collection, jobs, export | Page XML, text, Word, PDF free; ALTO, METS, TEI paid only | Browser |
| **Tesseract** (5.5.3, July 2026) | Free, Apache licence | Usable to good with clean, straight scans and a Fraktur model (frak2021 from Mannheim University Library, `deu_latf`); sensitive to skew, curvature, phone photos – our experience, see [traffic light](pdf-import.md) | None – recognition only | Yes | High (command line); built into Fraktur-Korrektor: one click | Text, hOCR, ALTO, PDF, PAGE XML | Windows, Mac, Linux |
| **OCR4all** with LAREX (0.6.1, January 2026) | Free, MIT licence | Built for early prints; recognition with Calamari, Kraken; quality not checked; own models can be trained | Built-in correction step for training text, with an on-screen keyboard for special characters | Yes – runs in Docker on your own computer | High – Docker, multi-step workflow, meant for projects | PAGE XML, text | Docker (Windows, Mac, Linux) |
| **eScriptorium** with Kraken | Free, MIT (eScriptorium) and Apache (Kraken) | Models for German prints from Mannheim University Library according to their guide (`german_print`); quality not checked; own models can be trained | Web editor, line in the image | Yes, if you or your institution run it yourselves (server) | High – server installation; as a user of an instance, medium | Text, PAGE XML, ALTO | Server on Linux; Kraken without Windows |
| **OCR-D** | Free, Apache licence | Toolbox for libraries (DFG-funded); quality depends on the chosen workflow and model; not checked | No interface of its own | Yes | Very high – command line, Docker, Ubuntu | PAGE XML, ALTO, METS | Linux/Docker; Windows only via WSL, Mac via Homebrew (according to the setup guide) |
| **gImageReader** (3.4.3, August 2025) | Free, GPL | The same recognition as Tesseract; you install the Fraktur model yourself | Text next to the image, spell checking, hOCR editor | Yes | Low to medium | Text, hOCR, PDF | Windows, Linux (no Mac according to the README) |
| **PoCoTo** (CIS Munich) | Free, BSD licence | No recognition – post-correction only | Batch correction of whole error series (research tool from the IMPACT project) | Yes (Java) | Medium to high | not checked | Java (Windows, Mac, Linux) – **last change May 2017**, effectively unmaintained |
| **Fraktur-Korrektor** (this program) | Free, GPL | Recognises nothing itself: Tesseract built in, Transkribus via import; a traffic light rates the quality | That is its purpose: keyboard, red words, batch correction, dictionary per era | Yes | Low | Text per page, PDF with text layer | Windows, Mac, Linux |

## Sources

All retrieved on 24 September 2026.

- ABBYY: prices <https://pdf.abbyy.com/pricing/>; Gothic/Fraktur in version 16
  <https://help.abbyy.com/en-us/finereader/16/user_guide/gothicrecognition/>; Mac article
  <https://support.abbyy.com/hc/en-us/articles/4417503390611> (the page refused automated retrieval – only
  title and search snippet checked).
- Transkribus: plans and credits <https://www.transkribus.org/plans>, <https://help.transkribus.org/credit-system>;
  models <https://www.transkribus.org/models/transkribus-print-multi-language-dutch-german-english-finnish-french-swedish-etc>,
  <https://www.transkribus.org/models/german-fraktur-19th-20th-century>,
  <https://www.transkribus.org/models/german-fraktur-18th-20th-century>; export
  <https://help.transkribus.org/downloading>.
- Tesseract: <https://github.com/tesseract-ocr/tesseract/releases>; Windows installer and frak2021
  <https://github.com/UB-Mannheim/tesseract/wiki>.
- OCR4all: <https://www.ocr4all.org/>, <https://github.com/OCR4all/OCR4all/releases>,
  <https://www.ocr4all.org/guide/user-guide/workflow>.
- eScriptorium and Kraken: <https://gitlab.com/scripta/escriptorium>, <https://escriptorium.readthedocs.io/>,
  <https://kraken.re/>, guide by Mannheim University Library <https://ub-mannheim.github.io/eScriptorium_Dokumentation/>.
- OCR-D: <https://ocr-d.de/en/>, <https://ocr-d.de/en/setup>, <https://github.com/OCR-D/core>.
- gImageReader: <https://github.com/manisandro/gImageReader>.
- PoCoTo: <https://github.com/cisocrgroup/PoCoTo> (licence, last change in the commit history).
