# Help

Fraktur-Korrektor is a reading and proofreading tool for text that OCR software has extracted from scanned
books – especially German books printed in Fraktur (blackletter). The page image is on the left, the
recognised text on the right. Words the program does not know are marked red. You simply read the book
and fix what you notice along the way. The result is a clean text.

The program runs entirely on your own computer. Nothing is sent to the internet; the browser merely serves
as its window.

## Three steps

1. **Text recognition** – the page images are turned into text. There are two routes:
   - *built in, one click:* [Reading in a PDF or images](pdf-import.md) with the free program Tesseract;
     everything stays on your computer. Afterwards a traffic light shows how good the result is.
   - *for difficult scans:* [Transkribus](transkribus.md), an internet service that usually recognises
     Fraktur better.

   Do you photograph the books yourself, in an archive perhaps? [Photographing books yourself](fotografieren.md)
   says what matters – a good picture saves all the after-work.
2. **Open** – a single button: you show the program a file or a folder, and it works out by itself whether it is
   a PDF, an EPUB, page images, a Transkribus export or a book you have already worked on: [Opening a book](add-book.md).
3. **Read and correct** – [Usage](usage.md). Everything works from the keyboard; the most important keys
   are always shown at the bottom of the window, below the image and the text.
4. **Take it along** – [Saving a book as PDF](pdf-sichern.md): one file with page images, searchable text and all
   your work, readable in any PDF reader and a book again on another computer. For reading on an e-reader, tablet or
   phone: [Saving a book as e-book](epub-sichern.md), with a table of contents, the page numbers of the printed edition
   and footnotes as links.

## Notes for Obsidian

If you take excerpts while reading, `F4` creates notes for Obsidian, each with page and source
([Usage](usage.md)). The same works for the highlights you made on your Kindle:
[Highlights from the Kindle](kindle.md).

## Other programs

What ABBYY FineReader, Transkribus, Tesseract, OCR4all, eScriptorium, OCR-D, gImageReader and PoCoTo can do,
what they cost and how they combine with this program: [Other programs compared](vergleich.md).

## If something does not work

[FAQ and troubleshooting](faq.md): firewall question, port in use, warnings at the first start, lost image
alignment, red words everywhere – the most common messages with the next step to take.

## Good to know

- **Every correction is saved immediately**, straight into the text files of the book folder. There is no
  “Save”. In addition, the program records each change in `korrekturen.log`.
- **Your reading position** is remembered for each book.
- **Backup:** copy the whole book folder from time to time – it contains all your work.
- **The first time** a book is opened, every word is checked against the dictionary. This can take up to a
  minute; afterwards it is fast.
- **The dictionary adapts to the book:** the program estimates the year of publication and accordingly accepts the
  spelling of 1901–1996 (“daß”), the reformed one (“dass”) or spellings from before 1901 (“Thür”, “giebt”). The `D` key
  changes this per book – see [Usage](usage.md). `F8` makes the program remember a single word as correct.
