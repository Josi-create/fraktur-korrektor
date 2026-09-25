# Saving a book as e-book

The PDF shows your book the way it was printed: page by page, as an image. For **reading on an e-reader, a tablet or a
phone**, an e-book is better suited. Its text flows and adapts to any screen size and font size. Fraktur-Korrektor
writes a file in the widespread **EPUB** format for this, containing the text you have corrected.

## What the e-book contains

| | |
|---|---|
| **Your corrected text** | as flowing text in paragraphs. Words hyphenated at the end of a line or across the page break are put back together. Running head, header line and the page number at the bottom are not part of the text and are left out. |
| **Table of contents** | made from the headings you marked with `H`: clickable in the reading app, plus a **Contents** page right after the title page, with the printed page number of every chapter. Every top-level chapter starts on a new page. |
| **Page numbers of the printed edition** | At every page break the page number of the printed edition appears small and grey, e.g. **[127]**. So you can cite the printed book from the e-book too. Reading apps that support it also jump straight to a page, for example Thorium Reader with *Go to page*. |
| **Footnotes** | The raised footnote mark in the text becomes a link. Many reading apps show the footnote in a small pop-up when you tap it, others below the text. |
| **Title page and cover** | a title page with title, author and year of publication. The first scanned page becomes the cover image that reading apps show in the book list. |

Verse, dialogue, lists of names and indexes keep their lines: where nearly every line starts with a capital letter and
hardly any reaches the margin, every printed line stays a line. Tables you marked with `T` appear as tables.

## How to save

1. In the **library**, click **Save as e-book** next to the book, or **Save …** at the top of the reading view and then
   **Save as e-book**.
2. The dialog first shows what goes into the e-book: how many headings, paragraphs and footnotes, and on how many pages
   a printed page number was found. If something is missing, it says which key fixes it (see below).
3. **Author:** shown in the reading app's book list, which is sorted by it. The program remembers the name for next
   time. The title is the book's name in the library; you can change it there with *Rename*.
4. **Also save the PDF next to it** is preselected. Then the folder holds two files with the same name: the e-book for
   reading and the [saved PDF](pdf-sichern.md) with page images and all your work.
5. **Write the e-book.** Even for a thick book this takes only seconds (a little longer with the PDF).

The file is named after the book and goes next to the book folder unless you choose another folder. An e-book saved
earlier from this same book is replaced; a foreign file of the same name is left alone, and e-book and PDF are then
called "… (2)".

## Reading the e-book

- **Mac, iPhone, iPad:** in the *Books* app; on a Mac, double-clicking the file is enough.
- **Windows, Mac, Linux:** the free program [Thorium Reader](https://www.edrlab.org/software/thorium-reader/) reads
  e-books and shows the printed page numbers under *Go to page*. [Calibre](https://calibre-ebook.com/) opens them as
  well.
- **E-readers** such as Tolino or Kobo: copy the file onto the device with a USB cable.
- **Kindle:** via Amazon's [Send to Kindle](https://www.amazon.com/sendtokindle) service, which accepts EPUB files
  (as of September 2026).

## E-book and PDF together

If you later open the e-book in Fraktur-Korrektor and the saved PDF of the same book lies next to it, the program
recommends the **PDF**. Only the PDF holds page images, line positions and your work; from it the book comes back
exactly as you left it. The e-book alone would open as a book without page images.

So you can pass on both files together or take them to another computer: read in the e-book, keep working with the PDF.

## Making a good e-book

An e-book is only as well structured as the book it is made from. The dialog says what is missing:

| Note in the dialog | What is missing | What helps |
|---|---|---|
| No headings yet | Without them the e-book has no table of contents and no chapters. | Mark chapter beginnings with `H` while reading, see [Using the program](usage.md). The overview `I` shows all headings with page numbers. |
| No paragraphs set | The program then separates paragraphs by one rule only: after a short line that ends in a punctuation mark. | Set paragraph beginnings with `A`. Usually the program has already recognised them from the indentation when the book was first opened. |
| Footnotes without a reference mark in the text | Text recognition swallowed the raised mark or read it as `*`, `°` or a number glued to the word. These footnotes stand below the paragraph in the e-book, without a link. | While reading, the program marks presumed reference marks in blue; `Space` jumps there, `Enter` raises the number. Once raised, it becomes a link. |
| No printed page numbers recognised | Text recognition read no page number at the top or the bottom. | Add the page number in the header line (`F2` on the top line). Single pages without a number, such as chapter beginnings, are filled in from the neighbouring pages. |

Linked are reference marks that are raised (`<sup>12</sup>`), that follow the word as "12)" as in older books, a star
at the word, and numbers glued to the word for which there is a footnote with that number on the same page. A footnote
that continues at the bottom of the next page is put back together.

## What does not work (yet)

- **Illustrations and plates** from the scan do not go into the e-book; a page without text only carries its page
  number.
- The e-book cannot be edited and brought back. You keep working in Fraktur-Korrektor and simply save again afterwards.
