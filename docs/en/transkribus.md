# Working with Transkribus

*Draft of 24 September 2026 – please check the statements about third-party programs.*

[Transkribus](https://www.transkribus.org/) is a service of the European cooperative READ-COOP for text
recognition in historical documents. For Fraktur prints it usually gives much better results than Tesseract
– especially with mediocre scans. Fraktur-Korrektor is built for exactly this division of labour:
**Transkribus recognises, Fraktur-Korrektor makes proofreading comfortable.**

## What you should know

- Transkribus works **on the internet**: your page images are uploaded to the servers of READ-COOP
  (Innsbruck). Keep this in mind for copyrighted or confidential material.
- You need an **account**; the free one is enough for trying it out. Recognition costs *credits*: 50 per month
  are free, and a printed page costs half a credit – enough for about 60 pages a month including line
  detection, not for a whole book. For a book you buy additional credits or spread the work over several
  months. Figures and limits: [What it costs](#what-it-costs).
- The web application (in the browser) is sufficient for everything described here.
- **Two-column layouts** (newspapers, encyclopaedias): the layout analysis of Transkribus usually creates a
  separate text region per column; the program then reads column by column – first the left one from top to
  bottom, then the right one. If the columns come out interleaved, check the regions of the page in Transkribus
  (one region per column, no line running across both columns) and export again.

## What it costs

Transkribus charges in *credits*. The figures here come from <https://www.transkribus.org/plans> and
<https://help.transkribus.org/credit-system> (as of 24 September 2026); all prices include 20 % Austrian VAT.
Check them before buying – they change.

| Plan | Credits | Price |
|---|---|---|
| **Free** | 50 per month | free |
| **Scholar** | 900 per year | €99 per year (or €19.99 per month) |
| **Team** (up to 5 people) | 1,500 per year | €449 per year |
| Buying credits separately | 250 | €59.50, no subscription; they do not expire |

What a job costs, per page:

| Job | Credits |
|---|---|
| Text recognition, **printed** – your case | 0.5 |
| Text recognition, handwritten | 1 |
| Finding the lines (layout, step 4) | 0.25 |
| Table or form field recognition | 1 |

Example: a book of 400 pages needs 400 × 0.75 = 300 credits for lines and text. With the free account that is
six months of 50 credits each – or buy 250 credits once (€59.50) and take the rest from the monthly allowance.
Before every job Transkribus shows the cost and only starts on your click (step 5), so a slip costs nothing.

**Limits of the free account** (according to the pricing page, as of 24 September 2026):

- The *Super Models* (such as “Text Titan II”) are only available in the paid plans. For Fraktur prints the
  free models from step 5 are sufficient.
- Export as **Page XML** – the only one Fraktur-Korrektor needs – is included in the free account, as are
  text, Word and PDF. ALTO, METS and TEI are reserved for the paid plans.
- Storage: 20 GB. We have not checked whether unused monthly credits expire.

## Step by step

Transkribus is in English, so the buttons below are quoted as they appear there (as of September 2026).
Allow half an hour for your first run.

### 1. Create an account and log in

On [transkribus.org](https://www.transkribus.org/) click **“Sign up”** at the top right, confirm your email
address, then **“Log in”**. You land in the web app; everything else happens there.

<!-- room for a screenshot of the start page -->

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
5. Click **“Submit”**. A bar shows the progress; with many pages this takes a while.

<!-- Draft: the size limits below come from the web app and were not re-checked on 24 Sept 2026;
     help.transkribus.org lists only JPEG/JPG and PDF as formats. -->
Allowed are JPG, PNG and TIFF (up to 20 MB each, up to 3000 files) and PDF (up to 512 MB). Around 300 dpi is
recommended, which is exactly what Fraktur-Korrektor produces.

<!-- room for a screenshot of the upload dialog -->

### 4. Let it find the lines (layout)

This step is easily missed but matters: it draws the baselines along which the text is read later. It does not
reliably run as part of text recognition.

1. In the document, tick the box at the top left that **selects all pages**.
2. Click **“Process with AI”**.
3. Under *Process Type* at the top choose **“Layout Analysis”** (older versions: “Layout Recognition”). As
   the model, the Transkribus help recommends *Mixed Line Orientation* or *Universal Lines* – both suit books.
   Cost: 0.25 credits per page. Then **“Start recognition”**.

Then leaf through a page: every line of text should have a line drawn over it. If the lines are crooked or
missing, a better image (ScanTailor) usually helps more than a different setting.

### 5. Let it recognise the text

1. Again **select all pages** and click **“Process with AI”**.
2. The **“Text Recognition”** panel is already open. Search for a model:

   | Model | for what | Error rate according to the model page |
   |---|---|---|
   | **Transkribus Print M1** | all printing, Fraktur and Antiqua, 14 languages – the safe choice | 2.2 % of characters |
   | **ONB_Newseye_GT_M1+** | German Fraktur, late 18th to mid 20th century; newspapers of the Austrian National Library | 1.1 % |
   | **NZZ Gold Standard M1+** | German Fraktur 1780–1940; front pages of the Neue Zürcher Zeitung | 0.5 % |

   The error rates come from the model pages on transkribus.org (as of 24 September 2026) and refer to each
   model's own test pages, not to your book – the smaller number is not automatically the better model for you.
   When in doubt, *Transkribus Print M1*. For a book from 1850 to 1940 it is worth comparing two or three pages.
   The *Super Models* of the paid plans (**Text Titan II**, since June 2026, print and handwriting in twelve
   languages) are normally not needed for clean Fraktur print.
3. Transkribus shows **how many credits** the job costs (0.5 per page) and how many you have left. Only then
   click **“Start recognition”**.

**After that you may switch your computer off.** Recognition runs on READ-COOP's servers in Innsbruck, not
on your machine; your computer is not needed for it. Only during the upload (step 3) does it have to stay on
until the bar has finished.

Depending on the queue, recognition takes minutes to hours. For a whole book, start the job in the evening
and look again the next morning: you find the status under **“AI Lab”**, and the finished result in the
document itself.

<!-- room for a screenshot of the model list -->

### 6. Download the result

1. In the collection, select the document (or all pages).
2. Click the **“Action”** button at the top, then **“Export”**.
3. Choose the format **“Page XML”** – not PDF, not Word. It holds the lines together with their position on
   the image, and that is what Fraktur-Korrektor needs to follow the text line by line next to the page image.
   The plain **text export** can be read as well, but it only holds the wording: the lines can then no longer
   be shown in the image.
4. Click **“Start export”**.
5. You get an email with a link (valid for two weeks). Without email: under **“Processes & Activity”** →
   **“Up- & Downloads”**, click the three dots at the far right of the finished export and choose **“Download”**.

You receive a **ZIP file**. You do not need to export the images as well if the book is already in
Fraktur-Korrektor – when opening, the program suggests your existing image folder.

### 7. Back to Fraktur-Korrektor

**If the book is already in your library** – because you read it in with Tesseract first – the text belongs
there, not in a new book: in the library click **Take in Transkribus text** below the book and pick the ZIP
file. Your page images stay where they are; nothing to search for, nothing
created twice. Afterwards the program tells you how many pages it replaced and how it matched them.

**If it is a new book:** Library → **Open …** → **Choose file …** → the ZIP file. There is no need to unpack
it; the program recognises the export and asks for matching page images if needed.
Details: [Opening a book](add-book.md).

## Afterwards

During import the program separates running heads and footnotes and marks unknown words red. Typical
Fraktur confusions (`ber` for “der”, `bie` for “die”, `Bolk` for “Volk”) are fixed fastest with **batch
correction** (`F9`) – see [Usage](usage.md).

## Tesseract or Transkribus?

| | Tesseract (built in) | Transkribus |
|---|---|---|
| Cost | free | 50 credits per month free (about 60 pages), a whole book costs money or months |
| Privacy | everything stays on your computer | images are uploaded |
| Effort | one click | account, upload, waiting, export |
| Quality with a clean scan | good | very good |
| Quality with a mediocre scan (phone photos, curved pages) | often weak | usually still good |

Rule of thumb: read the book in with Tesseract first. If the traffic light is green, you are done. With
yellow or red, the route via Transkribus is worth it for a whole book.
