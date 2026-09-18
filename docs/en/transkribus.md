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

1. **Create an account** at [transkribus.org](https://www.transkribus.org/) and sign in.
2. **Create a collection** and **upload the document** into it: the PDF of your scan is easiest.
   Transkribus splits it into pages.
   Tip: clean up poor scans with ScanTailor first – see [Reading in a PDF or images](pdf-import.md).
3. **Start text recognition.** Choose a model for printed text. For German Fraktur the public model
   **“Transkribus Print M1”** has proved itself; it reads Fraktur and Antiqua. Layout recognition (finding
   the lines) runs along automatically.
4. Wait until the job has finished (minutes to hours depending on load; you get a notification).
5. **Export:** select the document → *Export*. The important format is **PAGE XML** (under “Transkribus
   Document”). Also tick the export of **images**, then Fraktur-Korrektor gets the page images right away.
   You receive a link to a **ZIP file**.
6. In Fraktur-Korrektor: library → **Import Transkribus export …** → choose the ZIP file → **Import**.
   Details: [Adding a book](add-book.md).

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
