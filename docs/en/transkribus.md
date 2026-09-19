# Working with Transkribus

[Transkribus](https://www.transkribus.org/) is a service of the European cooperative READ-COOP for text
recognition in historical documents. For Fraktur prints it usually gives much better results than Tesseract
– especially with mediocre scans. Fraktur-Korrektor is built for exactly this division of labour:
**Transkribus recognises, Fraktur-Korrektor makes proofreading comfortable.**

## What you should know

- Transkribus works **on the internet**: your page images are uploaded to the servers of READ-COOP
  (Innsbruck). Keep this in mind for copyrighted or confidential material.
- You need an **account**; the free one is enough for trying it out. Recognition costs *credits*. The free
  account includes 50 credits per month (as of September 2026) – enough for a chapter, not for a whole book.
  For a book you buy additional credits or spread the work over several months.
  Current prices: <https://www.transkribus.org/plans>.
- The web application (in the browser) is sufficient for everything described here.

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
3. Drag the files in, or pick them with **“Browse”**. **Which files?**
   - If you have already read the book into Fraktur-Korrektor (after ScanTailor, say), take **all images from
     the `img` folder** of your book folder. The program shows you that folder with **Show folder …** after
     reading in, and puts the path on the clipboard.
   - Otherwise the **PDF** of your scan is enough; Transkribus splits it into pages itself.
4. Enter a name under **“Title”**.
5. Click **“Submit”**. A bar shows the progress; with many pages this takes a while.

Allowed are JPG, PNG and TIFF (up to 20 MB each, up to 3000 files) and PDF (up to 512 MB). Around 300 dpi is
recommended, which is exactly what Fraktur-Korrektor produces.

<!-- room for a screenshot of the upload dialog -->

### 4. Let it find the lines (layout)

This step is easily missed but matters: it draws the baselines along which the text is read later. It does not
reliably run as part of text recognition.

1. In the document, tick the box at the top left that **selects all pages**.
2. Click **“Process with AI”**.
3. Choose **“Layout Recognition”** at the top and start the job.

Then leaf through a page: every line of text should have a line drawn over it. If the lines are crooked or
missing, a better image (ScanTailor) usually helps more than a different setting.

### 5. Let it recognise the text

1. Again **select all pages** and click **“Process with AI”**.
2. The **“Text Recognition”** panel is already open. Search for a model:

   | Model | for what |
   |---|---|
   | **Transkribus Print M1** | all printing, Fraktur and Antiqua – the safe choice |
   | **ONB_Newseye_GT_M1+** | German Fraktur, late 18th to mid 20th century |
   | **NZZ Gold Standard M1+** | German Fraktur, 18th to 20th century |

   When in doubt, *Transkribus Print M1*. For a book from 1850 to 1940 it is worth comparing two or three pages.
3. Transkribus shows **how many credits** the job costs and how many you have left. Only then
4. click **“Start recognition”**.

You can follow the progress under **“AI Lab”**; depending on the queue it takes minutes to hours.

<!-- room for a screenshot of the model list -->

### 6. Download the result

1. In the collection, select the document (or all pages).
2. Click the **“Action”** button at the top, then **“Export”**.
3. Choose the format **“Page XML”** – not PDF, not Word. It holds the lines together with their position on
   the image, and that is what Fraktur-Korrektor needs.
4. Click **“Start export”**.
5. You get an email with a link (valid for two weeks). Without email: on the left under
   **“Uploads & downloads”**, click the three dots next to the finished export and choose **“Download”**.

You receive a **ZIP file**. You do not need to export the images as well if the book is already in
Fraktur-Korrektor – when opening, the program suggests your existing image folder.

### 7. Back to Fraktur-Korrektor

Library → **Open …** → **Choose file …** → the ZIP file. There is no need to unpack it; the program recognises
the export and asks for matching page images if needed. Details: [Opening a book](add-book.md).

## Afterwards

During import the program separates running heads and footnotes and marks unknown words red. Typical
Fraktur confusions (`ber` for “der”, `bie` for “die”, `Bolk` for “Volk”) are fixed fastest with **batch
correction** (`F9`) – see [Usage](usage.md).

## Tesseract or Transkribus?

| | Tesseract (built in) | Transkribus |
|---|---|---|
| Cost | free | 50 credits per month free, a whole book costs money |
| Privacy | everything stays on your computer | images are uploaded |
| Effort | one click | account, upload, waiting, export |
| Quality with a clean scan | good | very good |
| Quality with a mediocre scan (phone photos, curved pages) | often weak | usually still good |

Rule of thumb: read the book in with Tesseract first. If the traffic light is green, you are done. With
yellow or red, the route via Transkribus is worth it for a whole book.
