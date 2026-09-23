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
- **Work continued in both places** – new corrections here as well as there: then the recommendation is **Merge**.
  The program replays the changes from the PDF onto the existing book, line by line – corrections, split and joined
  lines, footnote rules –, unites the word lists and takes the bookmark that lies further on. Your corrections made
  here remain. Page images are taken only for pages that have none here. Here too, the present version is backed up
  first. At the end the program says how many changes it took over and how many lines need your attention.

  **Reviewing lines:** where the same line was corrected differently in both places, the program does not decide by
  itself. The version from here stays, the line is outlined in orange in the reading view, and the header says how
  many such lines there are. The `Z` key jumps to the next one and shows both versions: `1` keeps this one, `2` takes
  the one from the other computer, `Esc` postpones the decision. If a line was split or joined there but has since
  been corrected differently here, the program shows what happened there and you do it yourself with the usual keys
  if needed.

  Merged are the changes the program itself recorded (the correction log). Changes made directly in the text files
  with another editor are unknown to it: an update replaces them with the state from the PDF (they then survive only
  in the backup); a merge keeps those made here but does not bring along those from the other computer.

## Good to know

- The PDF is about as large as the book folder – the page images account for the lion's share.
- The invisible text is placed **per line**: when searching, the reader jumps to the right line, but a selection
  dragged with the mouse will not hit every word exactly.
- A book without page images (from an EPUB, say) gets pages with visible text.
- After merging, the correction log also contains the entries from the other computer. If you then save as PDF again
  and read it in there, a simple update suffices there – so a book can travel back and forth as often as you like.
