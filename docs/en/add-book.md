# Adding a book

The program starts with the **library**. It lists every book you have opened before, the most recent one
first. Clicking a book opens it where you left off.

## Importing an export from Transkribus

1. Export your document in Transkribus. Make sure **PAGE XML** is ticked (under “Transkribus Document”).
   If you also tick **export images**, Fraktur-Korrektor takes the page images along. You receive a ZIP file.
2. In the library, click **Import Transkribus export …**
3. Choose the ZIP file (**Choose ZIP file …**). There is no need to unpack it.
4. Give the book a title – or leave the field empty to use the title from Transkribus.
5. Only if the export contains no images: enter the folder that holds the page images (PNG or JPG, in page
   order).
6. **Import.** The program creates a new book folder and then offers **Open book**.

During import the program detects running heads (page numbers) and separates footnotes from the main text.
Where it gets this wrong, fix it while reading with the `F` key (see [Usage](usage.md)).

An import never overwrites an existing book. If the title already exists, a second folder with the suffix
“(2)” is created.

## Opening an existing book folder

**Open book folder …** shows your operating system's folder dialog. Choose the folder that contains the
page files `001.txt`, `002.txt`, …

## What is inside a book folder

| File | Content |
|---|---|
| `001.txt`, `002.txt`, … | the text, one file per page: optional `# running head`, main text, `---`, footnotes |
| `img/001.png` … | the page images (PNG or JPG) |
| `lines.json` | where each line of text sits in the page image |
| `whitelist.txt` | words you confirmed as correct with `F8` |
| `lesezeichen.json` | your reading position |
| `korrekturen.log` | log of all changes |

You may edit the text files with another editor, even while the program is running. Just do not change the
number of lines of a page, or the alignment with the image is lost.

## Removing a book from the list

The ✕ on the right only removes the entry from the library. The files are left untouched.
