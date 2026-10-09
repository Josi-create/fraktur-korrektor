# Other programs compared

There is a whole range of programs that read Fraktur or help with correcting. None is the best at everything;
most of them can be combined with Fraktur-Korrektor. This page is meant to make the choice easier – it is not
advertising, and it is a snapshot: all statements come from the programs' official pages, **as of
9 October 2026**, and may change. We have not tried the other programs on books ourselves: Fraktur quality is
described, not measured – serious figures only exist per book and per scan. What only the maker says is marked
*according to …*.

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
- **You want to improve the scan**, not the text: Fraktur-Korrektor splits double pages, straightens and removes
  dark margins; for curvature and stains there is [ScanTailor](install-tools.md).
- **You already have text** (EPUB, text file, Transkribus export) and want to read it against the scan: that
  is exactly what Fraktur-Korrektor is for ([Opening a book](add-book.md)).

**What fits together:** Transkribus → *Page XML* → read in here. ABBYY or OCRmyPDF → searchable PDF → *use the
existing text* here. Tesseract, gImageReader, OCR-D, eScriptorium → hOCR or ALTO → *Take in recognised text*
here. An EPUB (for instance an earlier run of your own) → put it next to the PDF → open here. Fraktur-Korrektor
itself writes text files per page, a [PDF with a text layer](pdf-sichern.md) that any other program can read,
and an [e-book](epub-sichern.md).

## The table

How to read it: *Fraktur* means whether and how the program recognises Fraktur print; *Correcting* means how
comfortably you fix errors afterwards; *Offline* means whether your scans stay on your computer.

| Program | Price | Fraktur | Correcting | Offline / privacy | Learning curve | Export | Platform |
|---|---|---|---|---|---|---|---|
| **ABBYY FineReader PDF** (version 16) | Subscription only. Windows: Standard €99/year, €267 for 3 years or €16/month; Corporate €165/year, €446 for 3 years or €24/month. Mac: €69/year or €186 for 3 years | Language “Old German” for Textur, Fraktur and Schwabacher according to the version 16 help. ABBYY advises selecting only this one language | Verification dialog jumps from uncertain word to uncertain word, with an enlarged image detail; user dictionary (according to the manual) | Yes – runs on your own computer; internet only for activation | Low – an office program | Searchable PDF (also PDF/A), Word, Excel, text, HTML, EPUB and more | Windows 10/11, Mac (Fraktur on the Mac too, according to an ABBYY help article) |
| **Transkribus** (READ-COOP, Innsbruck) | Free: 50 credits/month; Scholar €99/year with 900 credits; 250 credits on their own €59.50; a printed page 0.5 credit, handwriting 1 credit | Very good: public models for German Fraktur with 0.5–2.2 % character errors on their own test pages (figures from the model pages) | Web editor, line in the image; for a whole book more laborious than a keyboard program | **No** – images are processed and stored on servers in Austria. A version for institutions' own servers is in early access (price on request) | Medium – account, collection, jobs, export | Page XML, text, Word, PDF on all plans; ALTO, METS, TEI, Excel paid only | Browser |
| **Tesseract** (5.5.3, July 2026) | Free, Apache licence | Usable to good with clean, straight scans and a Fraktur model (frak2021 from Mannheim University Library, `deu_latf`); sensitive to skew, curvature, phone photos – our experience, see [traffic light](pdf-import.md) | None – recognition only | Yes | High (command line); built into Fraktur-Korrektor: one click | Text, hOCR, ALTO, PAGE XML, PDF with text layer | Windows, Mac, Linux |
| **OCR4all** with LAREX (0.6.1, January 2022) | Free, MIT licence | Built for early prints; recognition with Calamari; own models can be trained | Built-in correction step for training text, with an on-screen keyboard for special characters | Yes – runs in Docker on your own computer | High – Docker, multi-step workflow, meant for projects | PAGE XML, text | Docker (Windows, Mac, Linux) – **no longer developed**, maintenance only; work continues in its component LAREX (according to the README) |
| **eScriptorium** with Kraken (26.07, September 2026) | Free, MIT (eScriptorium) and Apache (Kraken) | Models for German prints according to the guide by Mannheim University Library (`german_print`); own models can be trained | Web editor, line in the image, on-screen keyboard | Yes, if you or your institution run it yourselves (server) | High – server installation; as a user of an instance, medium | Text, PAGE XML, ALTO; TEI if the instance has switched it on | Server on Linux, on Windows via WSL (according to Mannheim University Library); Kraken alone: Linux, Mac |
| **OCR-D** (3.13.3, September 2026) | Free, Apache licence | Toolbox for libraries, meant for German prints of the 16th to 19th century (DFG-funded); quality depends on the chosen workflow and model | No interface of its own | Yes | Very high – command line, Docker, Ubuntu | PAGE XML, ALTO, METS | Linux/Docker; Windows only via WSL, Mac via Homebrew (according to the setup page) |
| **gImageReader** (3.4.3, August 2025) | Free, GPL | The same recognition as Tesseract; you install the Fraktur model yourself | Text next to the image, post-processing with spell checking | Yes | Low to medium | Text, hOCR, PDF (from hOCR) | Windows, Linux (Mac not mentioned in the README) |
| **PoCoTo** (CIS Munich) | Free, BSD licence | No recognition – post-correction of ABBYY or Tesseract results only (ABBYY XML, hOCR) | Batch correction of whole error series (research tool from the IMPACT project) | Yes (Java); the error profile for correction suggestions comes either from a web service or, for experts, from your own computer | Medium to high | Text (whole or per page), back into the files read in | Java (Windows, Mac, Linux) – **last change May 2017**, effectively unmaintained |
| **Fraktur-Korrektor** (this program) | Free, GPL | Recognises nothing itself: Tesseract built in, Transkribus via import; a traffic light rates the quality | That is its purpose: keyboard, red words, batch correction, dictionary per era | Yes | Low | Text per page, PDF with text layer, e-book (EPUB) | Windows, Mac, Linux |

## Sources

All retrieved on 9 October 2026.

- ABBYY: prices <https://pdf.abbyy.com/pricing/>; system requirements and formats
  <https://pdf.abbyy.com/specifications/>; Gothic/Fraktur in version 16
  <https://help.abbyy.com/en-us/finereader/16/user_guide/gothicrecognition/>; verification dialog (version 15 manual)
  <https://help.abbyy.com/en-us/finereader/15/user_guide/checkingtext/>; Mac article
  <https://support.abbyy.com/hc/en-us/articles/4417503390611> (the page refused automated retrieval – only
  title and search snippet checked).
- Transkribus: plans and credits <https://www.transkribus.org/plans>, <https://help.transkribus.org/credit-system>;
  data storage <https://help.transkribus.org/is-my-data-safe>, own servers <https://www.transkribus.org/on-prem>;
  models <https://www.transkribus.org/models/transkribus-print-multi-language-dutch-german-english-finnish-french-swedish-etc>,
  <https://www.transkribus.org/models/german-fraktur-19th-20th-century>,
  <https://www.transkribus.org/models/german-fraktur-18th-20th-century>; export
  <https://help.transkribus.org/downloading>.
- Tesseract: <https://github.com/tesseract-ocr/tesseract/releases>; Windows installer and frak2021
  <https://github.com/UB-Mannheim/tesseract/wiki>.
- OCR4all: <https://www.ocr4all.org/>, <https://github.com/OCR4all/OCR4all> (maintenance-mode notice),
  <https://github.com/OCR4all/OCR4all/releases>, <https://www.ocr4all.org/guide/user-guide/workflow>.
- eScriptorium and Kraken: <https://gitlab.com/scripta/escriptorium> (versions), export
  <https://escriptorium.readthedocs.io/en/latest/export/>, Kraken <https://kraken.re/main/getting_started.html>,
  guide by Mannheim University Library <https://ub-mannheim.github.io/eScriptorium_Dokumentation/>.
- OCR-D: <https://ocr-d.de/en/>, <https://ocr-d.de/en/about>, <https://ocr-d.de/en/setup>,
  <https://github.com/OCR-D/core>.
- gImageReader: <https://github.com/manisandro/gImageReader>.
- PoCoTo: <https://github.com/cisocrgroup/PoCoTo> (licence, last change in the commit history), manual
  <https://github.com/cisocrgroup/Resources/blob/master/manuals/pocoto-manual.md>, download
  <https://www.cis.lmu.de/ocrworkshop/data/pocoto/>.
