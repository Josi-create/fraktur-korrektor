# FAQ and troubleshooting

These are the messages and situations that raise questions most often – each with the next step to take.
Anything not covered here is explained on the other help pages; they are linked in each answer.

## Starting and installing

**Windows says “Windows protected your PC”.**
This is the usual warning for programs that few people have downloaded yet, not a sign that something is wrong.
Click *More info* and then *Run anyway* – see [Installing the program](install.md).

**The Mac says the program cannot be opened because the developer cannot be verified.**
With the release version from the downloads page this message should not appear. If it does (for example with a
version you built yourself): close the message, then *Apple menu → System Settings → Privacy & Security*, and under
*Security* click **Open Anyway**. The button is only shown for an hour after the attempt. ScanTailor needs the same
route, see [Installing the tools](install-tools.md).

**Windows asks for a firewall permission.**
With a normal start Windows does not ask, because the program can then only be reached from your own computer. The
question comes up only when you started it with the `--lan` option for other devices on your home network. Allow
access for *private networks*, otherwise the other devices will not reach the program. Nothing goes to the internet
in either case – see [Reading on a tablet](usage.md).

**“Port 8765 is in use: another program is using it.”**
The program needs an address on your computer, and another program already has it. First check whether
Fraktur-Korrektor is not already running (icon in the notification area of the taskbar or in the Dock): a second
double-click does not start it again but merely brings the window back. If it is a different program, quit it – or
start Fraktur-Korrektor with `--port <number>`, e.g. `--port 8766`; the address in the browser is then
`http://localhost:8766`.

**No window opens.**
Open your browser and enter <http://localhost:8765>. The program is running – the browser is merely its window.
If it could not start, it shows a message box with the reason instead.

**I closed the browser window – is the program still running?**
Yes. Quit it via the icon in the notification area of the taskbar (Windows) or in the Dock or menu bar (Mac); see
[Installing the program](install.md). Double-clicking the program brings the window back at any time.

**“The dictionary is missing – the program’s ‘dict’ folder is incomplete.”**
The dictionaries are part of the program; without them it cannot check words. Install the program again. When
starting from the source code: restore the `dict/` folder, or point to your own Hunspell dictionary with
`--dic <path>` (without the `.dic`/`.aff` extensions).

## Opening and reading in

**“The file or folder was not found.”**
The path no longer fits – the file was moved or renamed, or a USB stick or network drive is not connected. Pick the
file again with the *Choose file …* button.

**The library shows “folder not found” next to a book.**
The book folder is no longer where the program knows it. If it is on a stick or network drive, connect it. If you moved
it: remove the entry with the ✕ and add the folder at its new place with **Open …** – the files and your work are
untouched.

**“This folder contains no page files (001.txt, 002.txt, …).”**
The folder is not a book folder of the program. Use **Open …** on the PDF, the images or the Transkribus export
instead; the program recognises what it is and creates a book from it – see [Opening a book](add-book.md).

**“The photos are in the iPhone format HEIC …”**
The iPhone usually saves photos as HEIC, and Fraktur-Korrektor cannot read that. Transfer the photos to the
computer by cable – with its default setting the iPhone converts them to JPEG on the way – or switch the iPhone
before photographing next time: *Settings* → *Camera* → *Formats* → *Most Compatible*. More under
[Photographing books yourself](fotografieren.md).

**“Neither PAGE XML, hOCR, ALTO nor text was found in there.”**
The export contains nothing the program can read. From Transkribus, download the result as **PAGE XML** (only then will
the lines sit next to the image later) – see [Working with Transkribus](transkribus.md).

**“Tesseract is not installed.”**
The release version includes text recognition. The message appears when starting from the source code or when the
program cannot find Tesseract: click *Show me the program …* next to the message and choose the program file, or install
Tesseract – see [Installing the tools](install-tools.md). Books that already bring text (searchable PDFs, EPUB,
Transkribus) can be opened without Tesseract.

**“The Fraktur model could not be downloaded.”**
The release version includes the model. When starting from the source code, the program downloads it once (5 MB) the
first time it reads in a book and stores it in your user folder; this needs an internet connection once. Connect and
try again – afterwards it works offline.

**“PDF files need the Python package PyMuPDF.”**
Only when starting from the source code: run `pip install pymupdf`. Folders of page images work without it.

**“More than 999 pages – please split the book.”**
A book has at most 999 pages in the program. Split the PDF in two (any PDF program can do that) and read both in as
separate books.

**The traffic light is red.**
The recognised text is so poor that correcting by hand is not worthwhile. Usually the scans are to blame: double
pages, crooked or curved pages. Have the scans prepared and the text recognised again, or use Transkribus – the
recommendation below the traffic light says what fits your case. See [Reading in a PDF or images](pdf-import.md).

**Two book pages are on one image, or the pages are crooked.**
**Prepare scans** next to the book in the library splits double pages and straightens crooked pages, with a preview of
the dividing line. Afterwards have the result recognised as a new book – see
[Reading in a PDF or images](pdf-import.md).

**The page images are missing, there is only text.**
Click **Add page images** next to the book and point to the image folder, the PDF or another book that already has the
images – see [Opening a book](add-book.md).

**“This only works on the computer the program runs on.”**
You are reading along from another device on the home network. Opening, reading in or preparing books is only possible
on the computer where the program was started. Reading and correcting works everywhere.

**“This PDF does not seem to belong to this text.”**
You chose a PDF for an EPUB or text-only book whose wording hardly matches the text – probably another book or another
edition. Nothing was created. Choose the right PDF, or create the EPUB without page images – see
[Opening a book](add-book.md).

**“This PDF was not saved by Fraktur-Korrektor.”**
The PDF holds no work in progress. Read it in with **Open …** like any other PDF.

**“This book already contains corrections – it will not be replaced.”**
*Recognise text afresh* replaces the book that was just read in – but only as long as the program read it in itself
and no work is in it yet. Once you have corrected something or confirmed a word, the book stays. Read the PDF in as a
new book with **Open …** instead; remove the old one from the list with the ✕ if you like and delete its folder by
hand.

## Reading and correcting

**The top bar says “(no image alignment for this page)”.**
The program knows for every line where it sits in the page image (file `lines.json` in the book folder). This
alignment goes in order: first text line – first image line, second – second. If the number of text lines no longer
matches the number of image lines, the program cannot align them safely and prefers not to: the text remains readable
and correctable, but the image no longer follows line by line. Causes:

- You edited the text file in another editor and inserted, deleted or wrapped lines. Restore the old number of lines
  there (the header `# …` and the footnote line `---` do not count). Better split or join lines inside the program with
  `Shift`+`Enter` and `V` – then it keeps the image in step.
- The text came from a text export without line positions (see [Opening a book](add-book.md)). Download the export
  from Transkribus as **PAGE XML** and read it in again with *Take in recognised text*.
- An import changed the page: **Earlier version** in the library brings back the text and line positions from before.

If only one page is affected, **Replace page …** in the top bar also helps: the page is recognised afresh and gets new
line positions – but your corrections on that page are lost (the previous version is kept in the backup). See
[Usage](usage.md).

**“The file was changed outside the program – the page will be reloaded.”**
The page’s text file looks different from what your browser shows – usually because it was edited at the same time in
an editor or on a second device. The program then overwrites nothing and reloads the page. Repeat your correction. You
may edit the text files in an editor at any time; press `R` in the program afterwards to reload the page.

**Almost everything is red.**
Then the dictionary does not fit the book. Press `D` and accept the spelling the book was printed in (before 1901:
“Thür”, “giebt”; 1901–1996: “daß”; later: “dass”). The window shows how many red words there are before and after.
Confirm names and places once with `F8` – that then applies to the whole book. See [Usage](usage.md).

**The page number in the header is red.**
It does not fit the neighbouring pages – OCR likes to read “16” as “46” in Fraktur. The hint gives the number that
should be there; `Space` and `Enter` correct it like a word.

**The page numbers are at the bottom of the page – do I have to enter them in the header?**
No. If a book carries its page numbers at the bottom throughout, the program finds them there by itself – even with
some noise from the page edge next to them – and uses them for notes and the table of contents. Pages without a number
(chapter openings, plates) get the number implied by the neighbouring pages.

**Lines have an orange frame, and there is a count at the top.**
After merging two working copies, these lines were corrected differently on the two computers. `Z` jumps to the next
one, `1` keeps the version here, `2` takes the other – see [Saving a book as PDF](pdf-sichern.md).

**Opening takes long the first time.**
The first time, the program checks every word of the book against the dictionary; this can take up to a minute.
Afterwards the results are stored and it is fast.

**I got a batch correction wrong.**
`U` in reading mode takes back the last batch; lines you have changed by hand since then are kept. Every single change
is also recorded in `korrekturen.log` in the book folder.

## Text recognition and dictionaries

**Tesseract or Transkribus?**
Tesseract is built in, free and runs on your computer; Transkribus is an internet service that usually recognises
Fraktur better but pays off mainly for difficult scans. The trade-off is discussed under
[Working with Transkribus](transkribus.md).

**The book is in roman type, not Fraktur.**
You choose the typeface when reading in; for roman type the program uses a different model. A book that mixes both
typefaces is best read in with the one that predominates.

**A word is correct but red.**
`F8` remembers it for the whole book (whitelist, shown with `W`). Common abbreviations, sigla that occur several times
and longer words that appear at least three times in the book are accepted anyway – see [Usage](usage.md).

**Can I use my own dictionary?**
Yes, for the spelling of 1901–1996: a Hunspell dictionary (`.dic` and `.aff`) via `--dic <path>` or the entry `"dic"`
in the file `config.json` in the `.fraktur-korrektor` folder of your user folder – see
[Installing the tools](install-tools.md).

## Working together and saving

**How do I back up my work?**
Every correction is saved immediately. Copy the whole book folder from time to time (where it lives is explained under
[Installing the program](install.md)), or save the book as a PDF – one file with images, text and work in progress:
[Saving a book as PDF](pdf-sichern.md).

**I want to work on two computers.**
Save as PDF, read it in on the other computer with **Open …**, continue there, save again. Back on the first computer
the program recognises the book and recommends *Update* or – if both sides were corrected – *Merge*. See
[Saving a book as PDF](pdf-sichern.md).

**“This book cannot be updated from the PDF.”**
Work has continued here since it was saved, or it is a different book. Choose *Merge* if the program offers it;
otherwise create the PDF as a new book.

**Can someone else read along from their own device? Does it work on an iPad?**
Yes, on the same home network: start the program with the `--lan` option; the address for the other devices is shown
at start-up. There is no password protection, so use it only on your own network. Adding books is only possible on
the computer itself. On a tablet you work with your finger – see [Reading on a tablet](usage.md).

**On the iPad nothing happens on “Note”, or Safari reports an invalid address.**
The note is meant to be created in Obsidian on the iPad, but Obsidian is not installed there or does not know the
vault by that name. Tap **☰ → Notes**: enter the name of the vault on the iPad, or untick *Create notes in Obsidian on
this device* – the note is then created on the computer.

**May I edit the text files in another program?**
Yes, at any time; the program re-reads changed files by itself (`R` reloads the page). Two things to keep in mind:
every line must stay one line, otherwise the image alignment is lost (see above), and such changes are not in the
correction log – so they do not travel along when two working copies are merged.
