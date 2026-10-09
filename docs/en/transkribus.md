# Working with Transkribus

*The statements about Transkribus – prices, buttons, models – were checked on transkribus.org and
help.transkribus.org on 9 October 2026. Transkribus changes its interface and prices now and then; if something
looks different, what you see there is what counts.*

[Transkribus](https://www.transkribus.org/) is a service of the European cooperative READ-COOP for text
recognition in historical documents. For Fraktur prints it usually gives much better results than Tesseract
– especially with mediocre scans. Fraktur-Korrektor is built for exactly this division of labour:
**Transkribus recognises, Fraktur-Korrektor makes proofreading comfortable.**

## What you should know

- Transkribus works **on the internet**: your page images are uploaded to the servers of READ-COOP in Austria.
  According to READ-COOP you remain the owner of your documents and can delete them at any time
  ([Is my data safe?](https://help.transkribus.org/is-my-data-safe)). Still, think twice before uploading
  copyrighted or confidential material.
- You need an **account**; the free one is enough for trying it out. Recognition costs *credits*: 50 per month
  are free, and a printed page costs half a credit (finding the lines is included) – enough for about 100 pages
  a month, not for a whole book. For a book you buy additional credits or spread the work over several
  months. Figures and limits: [What it costs](#what-it-costs).
- The web application (in the browser) is sufficient for everything described here. There is nothing to
  install.
- **Two-column layouts** (newspapers, encyclopaedias): the layout analysis of Transkribus usually creates a
  separate text region per column; the program then reads column by column – first the left one from top to
  bottom, then the right one. If the columns come out interleaved, check the regions of the page in Transkribus
  (one region per column, no line running across both columns) and export again.

## What it costs

Transkribus charges in *credits*. The figures here come from <https://www.transkribus.org/plans> and
<https://help.transkribus.org/credit-system> (as of 9 October 2026); all prices include 20 % Austrian VAT.
Check them before buying – they change.

| Plan | Credits | Price |
|---|---|---|
| **Free** | 50 per month | free |
| **Scholar** | 900 per year | €99 per year (or €19.99 per month) |
| **Team** (up to 5 people) | 1,500 per year | €449 per year (or €69 per month) |
| Buying credits separately | 250 | €59.50, no subscription; they never expire |

What a job costs, per page:

| Job | Credits |
|---|---|
| Text recognition, **printed**, lines included – your case | 0.5 |
| Text recognition, handwritten, lines included | 1 |
| Finding the lines only (layout, step 4 – usually not needed) | 0.25 |
| Table or form field recognition | 1 |

Uploading, downloading and correcting cost nothing.

Example: a book of 400 pages needs 400 × 0.5 = 200 credits. With the free account that is four months of 50
credits each – or buy 250 credits once (€59.50), with some left over. Before every job Transkribus shows the cost
and only starts on your click (step 5), so a slip costs nothing.

**Limits of the free account** (according to the pricing and help pages, as of 9 October 2026):

- The *Super Model* “Text Titan II” is only available from the Scholar plan upwards. For Fraktur prints the
  free models from step 5 are sufficient.
- Export as **Page XML** – the only one Fraktur-Korrektor needs – is included in every plan, as are images,
  text, Word and PDF. ALTO, METS and TEI are reserved for the paid plans.
- Storage: 20 GB.
- According to the pricing page, the free monthly credits are valid for the respective billing period; it does
  not say whether leftovers carry over to the next month. Credits bought separately never expire.

## Step by step

Transkribus is in English, so the buttons below are quoted as they appear there (as of October 2026).
Allow half an hour for your first run.

### 1. Create an account and log in

On [transkribus.org](https://www.transkribus.org/) click **“Get Started”** at the top right, fill in the form and
confirm your email address. After that you sign in at any time with **“Log In”**. You land in the web app;
everything else happens there.

### 2. Create a collection

A *collection* is a drawer for your books; nothing works without one.

1. Click **“Collections”** in the menu on the left.
2. Click **“+ New Collection”** on the right.
3. Type a name, for example the book title, and click **“+ Create”**.

### 3. Upload the page images

1. Click the collection you just created so that it opens.
2. Click **“Upload”** at the top right.
3. Drag the files in, or pick them with **“Browse”**. **Which files?** Always upload the images you want to
   read in the end – Transkribus does not split double pages and does not straighten anything.
   - If you had Fraktur-Korrektor **prepare** the scans (double pages split, straightened): the files from the
     folder **`…/aufbereitet`** inside the book folder. After **ScanTailor**: the files from its output folder
     **`…/scantailor/out`**. Those are the separated, straightened single pages (Transkribus accepts TIFF).
   - If you have already **read that result** into Fraktur-Korrektor: the images from the **`img`** folder of
     that book – the same content, just numbered. **No need to go looking for it:** in the library, click the
     button **Prepare for Transkribus** below the book. The program names the folder, puts
     it on the clipboard and opens it in a file window, ready to drag in. This is also the route that matches
     the pages back most reliably later on.
   - If the scan was fine to begin with: the images from `img`, or the **PDF** itself; Transkribus splits it
     into pages.

   Worth checking: are there as many files as the book has pages? With separated double pages there must be
   twice as many as there are sheets in the scan.
4. Enter a name under **“Title”**.
5. Click **“Submit”**. You can follow the progress in the menu on the left under **“Processes & Activity”**;
   with many pages this takes a while.

<!-- Bildschirmfoto: transkribus-hochladen.png – the upload dialog of a collection with a few page images dragged in, the “Title” field filled in and the “Submit” button -->

According to the Transkribus help, JPG, PNG and TIFF are allowed (up to 20 MB per image, up to 3000 files at
once) as well as PDF (up to 512 MB per file). Around 300 dpi is recommended, which is exactly what
Fraktur-Korrektor produces; according to Transkribus, more does not help.

### 4. Only for difficult layouts: let it find the lines first (layout)

Text recognition in step 5 finds the lines by itself; for an ordinary book you can skip this step. It is worth
it for **two columns, tables or intricate layouts**: you can look at the result and correct it in Transkribus
before the text is recognised.

1. In the document, tick the box at the top left that **selects all pages**.
2. Click **“Process with AI”**.
3. Under *Process Type* at the top choose **“Layout Analysis”** instead of “Text Recognition”. As the model,
   the Transkribus help recommends *Mixed Line Orientation*, *Universal Lines* or *Horizontal Line Orientation*.
   Cost: 0.25 credits per page. Then **“Start recognition”**.

Then leaf through a page: every line of text should have a line drawn over it. If the lines are crooked or
missing, a better image (ScanTailor) usually helps more than a different setting.

### 5. Let it recognise the text

1. In the document, tick the box at the top left that **selects all pages**, and click **“Process with AI”**.

   <!-- Bildschirmfoto: transkribus-auswahl.png – an opened document with the “select all pages” box ticked at the top left and the “Process with AI” button next to it -->

2. **“Text Recognition”** is already selected. Search for a model in the search field – by its name, or for
   “Fraktur”:

   | Model | for what | Error rate according to the model page |
   |---|---|---|
   | **Transkribus Print M1** | all printing, Fraktur and Antiqua, 14 languages – the safe choice | 2.2 % of characters |
   | **ONB_Newseye_GT_M1+** | German Fraktur, late 18th to mid 20th century; newspapers of the Austrian National Library | 1.1 % |
   | **NZZ Gold Standard M1+** | German Fraktur 1780–1940; front pages of the Neue Zürcher Zeitung | 0.5 % |

   The error rates come from the model pages on transkribus.org (as of 9 October 2026) and refer to each
   model's own test pages, not to your book – the smaller number is not automatically the better model for you.
   When in doubt, *Transkribus Print M1*. For a book from 1850 to 1940 it is worth comparing two or three pages.
   The *Super Model* of the paid plans (**Text Titan II**, since June 2026, print and handwriting in twelve
   languages) is normally not needed for clean Fraktur print.

   <!-- Bildschirmfoto: transkribus-modellwahl.png – the side panel after “Process with AI”: Process Type “Text Recognition”, “Fraktur” in the search field with the list of hits, below it the credits needed and available and the “Start recognition” button -->

3. Transkribus shows **how many credits** the job costs (0.5 per page) and how many you have left. Only then
   click **“Start recognition”**.

**After that you may switch your computer off.** Recognition runs on READ-COOP's servers in Austria, not on
your machine; your computer is not needed for it. Only during the upload (step 3) does it have to stay on until
the upload has finished.

Depending on the queue, recognition takes minutes to up to a day. For a whole book, start the job in the
evening and look again the next morning: you find the status in the menu on the left under **“AI Lab”**
(“RUNNING” means it is being processed, “CREATED” that it is still waiting), and the finished result in the
document itself.

### 6. Download the result

1. In the collection, select the document (or all pages).
2. Click the **“Action”** button at the top, then **“Export”**.
3. Choose the format **“Page XML”** – not PDF, not Word. It holds the lines together with their position on
   the image, and that is what Fraktur-Korrektor needs to follow the text line by line next to the page image.
   The plain **text export** can be read as well, but it only holds the wording: the lines can then no longer
   be shown in the image.

   **Include the images?** If the book is already in Fraktur-Korrektor you do not need them – the page images
   are there already. If it is a new book, also choose **“Images”**: then everything is in one file and you do
   not have to look for images when reading it in.
4. Click **“Start export”**.

   <!-- Bildschirmfoto: transkribus-export.png – the export dialog with “Page XML” (and “Images”) ticked and the “Start export” button -->

5. You get an email with a link (valid for two weeks). Without email: in the menu on the left under
   **“Processes & Activity”** → **“Up- & Downloads”**, click the three dots at the far right of the finished
   export and choose **“Download”**.

   <!-- Bildschirmfoto: transkribus-download.png – “Processes & Activity” → “Up- & Downloads” with a finished export and the three-dot menu opened, showing “Download” -->

You receive a **ZIP file**. There is no need to unpack it.

### 7. Back to Fraktur-Korrektor

**If the book is already in your library** – because you read it in with Tesseract first – the text belongs
there, not in a new book: in the library click **Take in recognised text** below the book and pick the ZIP
file. Your page images stay where they are; nothing to search for, nothing
created twice. Afterwards the program tells you how many pages it replaced and how it matched them.

**If it is a new book:** Library → **Open …** → **Choose file …** → the ZIP file. The program recognises the
export by itself. If the images are missing from it, it suggests an image folder with exactly as many images as
the export has pages – or you add the images later with **Add page images**.
Details: [Opening a book](add-book.md).

## Afterwards

During import the program separates running heads and footnotes and marks unknown words red. Typical
Fraktur confusions (`ber` for “der”, `bie` for “die”, `Bolk` for “Volk”) are fixed fastest with **batch
correction** (`F9`) – see [Usage](usage.md).

## Tesseract or Transkribus?

| | Tesseract (built in) | Transkribus |
|---|---|---|
| Cost | free | 50 credits per month free (about 100 pages), a whole book costs money or months |
| Privacy | everything stays on your computer | images are uploaded |
| Effort | one click | account, upload, waiting, export |
| Quality with a clean scan | good | very good |
| Quality with a mediocre scan (phone photos, curved pages) | often weak | usually still good |

Rule of thumb: read the book in with Tesseract first. If the traffic light is green, you are done. With
yellow or red, the route via Transkribus is worth it for a whole book.
