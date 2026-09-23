# Reading in a PDF or images

If you have a book as a scanned PDF or as a folder of page photos, Fraktur-Korrektor can recognise the text
itself. It uses the free program **Tesseract**, which runs on your own computer – nothing is sent to the
internet. Tesseract comes with the finished program; only if you start from the source code do you install it
yourself: [Installing the tools](install-tools.md).

**To try it out**, take a public-domain edition of Goethe's *Faust* (Fraktur, 470 pages, 17 MB):
<https://archive.org/download/fausteinetragd00goetuoft/fausteinetragd00goetuoft.pdf>. It already carries a text layer, which makes it a good way to compare both routes (see below).

## How to do it

1. In the library, click **Open …** and show the PDF (**Choose file …**) or the folder with the page images
   (**Choose folder …**). The program works out by itself what it is – see [Opening a book](add-book.md).
2. The window shows whether Tesseract and the Fraktur model are available. Both come with the finished
   program; the model is provided by Mannheim University Library.
3. Enter a title and choose the **typeface**: Fraktur (blackletter) or Antiqua (roman type).
4. **Start text recognition.** A bar shows the progress; expect a few seconds per page. *Stop* cancels at
   any time.

## Searchable PDFs: using the existing text

Many PDFs are already “searchable”: another program (ABBYY FineReader, OCRmyPDF, the scanner itself) has recognised
the text and placed it invisibly behind the page image. Fraktur-Korrektor notices this and asks:

- **Use this text** – takes only seconds, even for several hundred pages. The page images are taken from the PDF
  unchanged. Tesseract is not needed for this.
- **Recognise the text afresh** – sensible if the existing text is poor, for example because a Fraktur book was
  recognised by a program made for roman type.

If in doubt, use the text first and look at the traffic light. If it is not green, read the book in again and have
it recognised afresh.

If the PDF comes from a library and contains no text, have a look at the library’s site: the recognised text
is often available there separately from the PDF (hOCR or ALTO) and can be laid over the book afterwards –
see [Text from a library](add-book.md).

## The traffic light

After recognition the program estimates how good the result is. It uses two values: how confident Tesseract
was about the words, and how many of the words are in the dictionary. (For text taken from the PDF only the
dictionary counts – a PDF does not store how confident the recognition was.)

| Light | Meaning | What to do |
|---|---|---|
| 🟢 green | Good recognition, roughly as good as Transkribus. | Just read and correct. |
| 🟡 yellow | Usable, but with many misreadings. | Fine for a few pages. For a whole book, [Transkribus](transkribus.md) is worth it. |
| 🔴 red | Poor recognition. | Do not correct this by hand – improve the scan first (*Prepare scans*, see below) or use [Transkribus](transkribus.md). |

The coloured dot also appears in the library in front of the book title. The values for every single page
are stored in the file `qualitaet.json` in the book folder.

You can replace a book with a better version at any time: simply read it in again (a second folder is
created) and remove the old entry from the library.

## Double pages and crooked pages: preparing the scans

Text recognition is only as good as the image. Anyone photographing a book in a reading room usually ends up
with **two book pages on one picture**, and the pages are **crooked**. The program handles both itself before
it recognises the text:

1. Via **Open …** point at the PDF or the folder of photos. The program looks at a few pages. If two pages sit
   side by side or the pages are crooked, the recommendation **Prepare scans …** appears.
2. Click it. You see the first double page with a **red line**. Is it in the middle of the gutter? If not, drag
   it there with the mouse or move it with the arrow keys `←` `→` (with `Shift` in bigger steps). The line
   applies to all pages; on each one the program looks for the gutter again nearby and adjusts the line. Two
   check boxes say what is to happen: **Split double pages at the line** and **Straighten crooked pages** – the
   measured angle is shown after it.
3. **Apply.** A bar shows the progress; expect about a second per page. The prepared pages go into a folder of
   their own, `aufbereitet`, inside the book folder; your original stays untouched. Every double page becomes
   two pages, the left one first. Only pages more than 0.3° off are rotated.
4. Afterwards the new folder is already selected: click **Start text recognition**. The program remembers that
   the pages were prepared (tag *prepared* in the library).

If the book is **already in your library** – say, because you had the double pages recognised as they were
at first –, the book has a button **Prepare scans**. It prepares the book’s page images and then offers to
have the text recognised afresh; a new book is created, the present one stays.

**Easier still: do not photograph double pages at all.** A few tips: every page on its own, filling the picture;
keep the book flat (with your free hand or a weight on the edge); camera parallel to the page; even light
without the shadow of your own hand. Then the program has nothing to split and little to rotate.

## Curved pages, stains, dark margins: ScanTailor

What the program cannot do: flatten curved pages, remove stains and dark margins, even out uneven lighting. If
it reports that **the line ends are much worse than the rest**, the page curves towards the gutter. For that
there is the free program **ScanTailor Advanced** ([Installation](install-tools.md) – awkward on the Mac). It
splits double pages and deskews too, just with more manual work.

If the book is **already in your library**, it has a button **Prepare for ScanTailor** – the input and output
folder are then settled, and ScanTailor starts right away. For a PDF that has not been read in yet:

1. Choose the PDF via **Open …** and click **Prepare with ScanTailor first …** in the window.
   The program saves every PDF page as an image (ScanTailor cannot open PDFs) and starts ScanTailor.
2. In ScanTailor: **New Project**. As input directory, give the folder ending in `scantailor`. You do not
   have to type it: Fraktur-Korrektor puts the path on the clipboard (click the field and paste) and also
   opens the folder in a file window, from where you can drag it in. Keep the suggested output directory `out`.
3. Work through the six stages on the left from top to bottom. Usually it is enough to click the arrow ▶
   at the bottom of each stage (“process all pages”) and to leaf through the result:
   *Fix Orientation* → *Split Pages* → *Deskew* → *Select Content* → *Margins* → *Output*. In the *Output*
   stage, for Fraktur: 600 dpi, mode *Black and White*; for curved pages switch on *Dewarping* there.
4. Back in Fraktur-Korrektor, click **Back** and **Examine** – the folder `…/scantailor/out` is already entered –
   and then **Start text recognition**. If you closed the window in between, find the folder through
   **Open …** → **Choose folder …**; it is called `out` and sits inside the book folder under `scantailor`.
   The program labels it *output of ScanTailor*.

   Important: only if you read in **this** result do you carry on with the separated pages. Read the PDF in
   again and all the effort was for nothing.

   If you would rather have [Transkribus](transkribus.md) read the text, upload the files from
   `…/scantailor/out` or `…/aufbereitet` there – Transkribus does not split double pages.

## Limitations

- Multi-column layouts (newspapers, encyclopaedias) are not read column by column.
