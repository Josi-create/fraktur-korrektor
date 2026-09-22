# Saving a book as PDF

A Fraktur-Korrektor book is a folder full of files: page images, one text file per page, your word list, the
bookmark, the log of your corrections. To **take a book along** – to the laptop, to a colleague, into a backup –
the program packs all of it into **a single PDF file**.

## What the PDF contains

| | |
|---|---|
| **Page images** | Every book page is a PDF page, the image unchanged – nothing is recalculated or shrunk. |
| **The text** | lies invisibly on top of the image, line by line in the right place. In any PDF reader you can **search**, **copy text** or have the book **read aloud** – with your corrections. |
| **Your work** | travels as the attachment `fraktur-korrektor.zip` inside the PDF: the texts of all pages, the position of the lines in the image, word list, bookmark, correction log, year of publication and spelling. Acrobat and Firefox show the attachment in the sidebar; other readers simply ignore it. |

So the PDF can be read with any program that handles PDF – and Fraktur-Korrektor turns it back into a book in
which you carry on exactly where you left off.

## How to save

1. In the **library**, click **Save as PDF** next to the book – or the link of the same name at the top of the
   reading view.
2. The PDF goes into the folder that also holds the book folder. If it should go straight to a USB stick or a
   cloud folder, pick another folder there.
3. **Write the PDF.** For a book of 300 pages this takes a few seconds. Afterwards the program shows where the file
   is and opens the folder if you wish.

The PDF is named after the book. If you save the same book to the same place again later, the old PDF is replaced
– it came from the same book, after all. A foreign file of the same name is never overwritten; the new PDF is then
called “… (2).pdf”.

## How to read it in on another computer

1. Start Fraktur-Korrektor, **Open …**, pick the PDF.
2. The program recognises the attachment and shows “saved book (PDF)” with date and number of corrections.
3. **Take in the book** creates the book in the books folder – with page images, text, word list and bookmark –
   and adds it to the library.

If a book of that name already exists there, a second one is created with the suffix “(2)”; nothing is
overwritten.

## Working on two computers: updating the book

The usual routine: started on the PC, saved as PDF, read in on the laptop and continued there, saved again – and
back on the PC you want to carry on in the **existing** book, not in a copy “(2)”.

When you open the PDF, the program recognises that the same book is already in the library (every book carries a
fixed identifier that travels in the PDF) and checks whether anything has happened here since it was saved:

- **Nothing happened** – everything in the local correction log is also in the PDF: then the recommendation is
  **Update the existing book**. The book receives text, page images, word list, bookmark and log from the PDF;
  the present version is backed up first (`vorher-<date>.zip`, brought back via **Earlier version**). If you would
  rather have a second book, choose that next to it.
- **Work continued in both places** – new corrections here as well as there: the program cannot merge those yet. It
  says how many changes are on each side and creates the PDF as a second book; nothing is lost. Best carry on in one
  place at a time, save there, and read the PDF in on the other computer before changing anything there.

## Good to know

- The PDF is about as large as the book folder – the page images account for the lion's share.
- The invisible text is placed **per line**: when searching, the reader jumps to the right line, but a selection
  dragged with the mouse will not hit every word exactly.
- A book without page images (from an EPUB, say) gets pages with visible text.
- **Merging** two states that both contain new corrections does not exist yet – see above.
