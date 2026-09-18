# Reading in a PDF or images

If you have a book as a scanned PDF or as a folder of page photos, Fraktur-Korrektor can recognise the text
itself. It uses the free program **Tesseract**, which runs on your own computer – nothing is sent to the
internet. Tesseract has to be installed once: [Installing the tools](install-tools.md).

## How to do it

1. In the library, click **Read in PDF or images (text recognition) …**
2. The top of the window shows whether Tesseract and the Fraktur model are available. The program downloads
   the model (5 MB, from Mannheim University Library) by itself the first time.
3. **Choose PDF …** or – for single images (JPG, PNG, TIF) – **Choose folder …**
4. Enter a title and choose the **typeface**: Fraktur (blackletter) or Antiqua (roman type).
5. **Start text recognition.** A bar shows the progress; expect a few seconds per page. *Stop* cancels at
   any time.

## The traffic light

After recognition the program estimates how good the result is. It uses two values: how confident Tesseract
was about the words, and how many of the words are in the dictionary.

| Light | Meaning | What to do |
|---|---|---|
| 🟢 green | Good recognition, roughly as good as Transkribus. | Just read and correct. |
| 🟡 yellow | Usable, but with many misreadings. | Fine for a few pages. For a whole book, [Transkribus](transkribus.md) is worth it. |
| 🔴 red | Poor recognition. | Do not correct this by hand – improve the scan first (ScanTailor) or use [Transkribus](transkribus.md). |

The coloured dot also appears in the library in front of the book title. The values for every single page
are stored in the file `qualitaet.json` in the book folder.

You can replace a book with a better version at any time: simply read it in again (a second folder is
created) and remove the old entry from the library.

## Cleaning up poor scans with ScanTailor

Text recognition is only as good as the image. Typical problems: two book pages on one photo, skewed or
curved pages, dark margins, fingers in the picture. If the program reports that **the line ends are much
worse than the rest**, the page curves towards the gutter.

The free program **ScanTailor Advanced** fixes all of this: it splits double pages, straightens them,
flattens curvature and crops margins. ([Installation](install-tools.md))

1. In the window *Read in PDF or images*, choose the PDF and click **Prepare with ScanTailor first …**
   The program saves every PDF page as an image (ScanTailor cannot open PDFs) and starts ScanTailor.
2. In ScanTailor: **New Project**. As input directory choose the folder that Fraktur-Korrektor displays (it
   ends in `scantailor`). Keep the suggested output directory `out`.
3. Work through the six stages on the left from top to bottom. Usually it is enough to click the arrow ▶
   at the bottom of each stage (“process all pages”) and to leaf through the result:
   *Fix Orientation* → *Split Pages* → *Deskew* → *Select Content* → *Margins* → *Output*. In the *Output*
   stage, for Fraktur: 600 dpi, mode *Black and White*; for curved pages switch on *Dewarping* there.
4. Back in Fraktur-Korrektor, the folder `…/scantailor/out` is already entered as the source. Click
   **Start text recognition**.

## Limitations

- Multi-column layouts (newspapers, encyclopaedias) are not read column by column.
- A text layer already present in the PDF is not used; the program recognises the text afresh.
- The bundled dictionary covers German spelling from 1901 to 1996. For newer books (“dass”) and for prints
  before 1901 (“Thür”, “giebt”) the dictionary rate is therefore lower than the recognition deserves.
