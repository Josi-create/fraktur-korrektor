# Opening a book

The program starts with the **library**. It lists every book you have opened before, the most recent one
first. Clicking a book opens it where you left off.

## One button for everything: “Open …”

You do not need to know in which form your book exists. Click **Open …** and show the program a **file** or a
**folder**. It looks at what is inside and suggests how to go on:

| Found | What happens then |
|---|---|
| 📖 **Book** – a folder you have already worked on with Fraktur-Korrektor | is opened immediately |
| 📄 **PDF** | If it is already searchable, its text is taken over within seconds; otherwise Tesseract recognises the text. See [Reading in a PDF or images](pdf-import.md) |
| 📗 **EPUB** | If a **PDF of the same name** lies next to it, the scan appears on the left and the EPUB text on the right. Without a PDF the book is opened without page images |
| 🖼️ **Page images** – a folder with JPG, PNG or TIF | Tesseract recognises the text |
| 🗂️ **Export from Transkribus** – ZIP file or unpacked folder | is imported. See [Working with Transkribus](transkribus.md) |

If you choose a whole folder, the program often finds several things – for example a PDF, an EPUB and a book you
have already been correcting. It then shows all finds with page count and date. The first one is the
**recommendation**:

- A book that already contains **corrections** always comes first (“your work is in here”) – so that you do not
  start from scratch by accident.
- After that comes whatever is furthest along: a Transkribus export before an EPUB, an EPUB before a PDF, a PDF
  before loose images.
- If another find is **newer** than the recommendation, it says so.

You can click a different find at any time. If the case is clear, the program does not ask at all.

## EPUB and PDF together

Have you already turned a book into an EPUB and want to read it against the scan once more? Put the EPUB and the
PDF with the same name into the same folder – additions such as “(durchsuchbar)”, “(kompakt)” or “_OCR” do not
matter:

    Fatma - Immanuel Walker.epub
    Fatma - Immanuel Walker (durchsuchbar).pdf

The program takes page images and lines from the PDF and puts the **wording of the EPUB** into these lines.
Hyphenation at line ends is kept. Running heads and footnotes that are placed elsewhere in the EPUB, or not at
all, keep the text from the PDF. At the end you are told what percentage of the lines carry the EPUB text. If
there are several matching PDFs, the searchable one with the better image quality is used.

The EPUB itself is not changed; your corrections go into the text files of the new book folder.

## Export from Transkribus

During import the program detects running heads (page numbers) and separates footnotes from the main text.
Where it gets this wrong, fix it while reading with the `F` key (see [Usage](usage.md)). If the export contains
no page images, the program looks in the chosen folder for an image folder with exactly as many images as the
export has pages, and suggests it.

Nothing is ever overwritten: if the title already exists, a second folder with the suffix “(2)” is created.

## Continue working on a book

A book is rarely finished in one go: first you read in a PDF, then you tidy up the pages with ScanTailor, then
you have the text recognised by Transkribus. **You do not have to start over every time.**

In the library, move to the book’s row and click the three dots **⋯** on the right. Four ways are open to you:

| | What for |
|---|---|
| **Take in the text from Transkribus** | The text from Transkribus takes the place of the present one. Your page images, your word list and your bookmark stay where they are. |
| **Add page images** | For books that are text only – a Transkribus export without images, say. |
| **Prepare for Transkribus** | The program names the folder you upload, puts it on the clipboard and opens it in a file window. |
| **Prepare for ScanTailor** | Starts ScanTailor and names the input and output folder. |

That way you never need to remember where a book’s images are – the program knows.

### How the pages find each other

When a text comes back from Transkribus, every page has to find its image again. If even one page is missing
from the export, matching them blindly in order would put every text from there on next to the wrong image.
So the program tries, in this order:

1. **By file name.** When reading a book in, the program notes what each page’s image was originally called
   (`quellen.json`). The Transkribus export carries the same names – that matches unambiguously.
2. **By wording.** Without names, the program compares the words: the same page of the book stays
   recognisable, even if one text recognition was worse than the other. Safe hits are the anchors; pages
   without text (plates) follow from the distance between them.
3. **In order** – only if both sides have the same number of pages.

If none of these works out, the program stops and tells you, rather than putting text next to the wrong
images. Then use **Open …** to create a separate book from the export.

### If the book already contains corrections

The program warns you: the new text from Transkribus does not contain your work. You may take it into this
book anyway, or create a new one next to it – the page images come along. Either way the present version is
backed up first, as `vorher-<date>.zip` in the book folder.

## What is inside a book folder

New books are created in `Fraktur-Korrektor` in your home folder.

| File | Content |
|---|---|
| `001.txt`, `002.txt`, … | the text, one file per page: optional `# running head`, main text, `---`, footnotes |
| `img/001.jpg` … | the page images (JPG or PNG) |
| `lines.json` | where each line of text sits in the page image |
| `whitelist.txt` | words you confirmed as correct with `F8` |
| `lesezeichen.json` | your reading position |
| `korrekturen.log` | log of all changes |
| `qualitaet.json` | after reading in: the traffic-light values per page |
| `quellen.json` | what each page’s image was originally called – so a later Transkribus export can be matched |
| `vorher-….zip` | backup of the text version that a Transkribus text replaced |

You may edit the text files with another editor, even while the program is running. Just do not change the
number of lines of a page, or the alignment with the image is lost.

## Removing a book from the list

The ✕ on the right only removes the entry from the library. The files are left untouched.
