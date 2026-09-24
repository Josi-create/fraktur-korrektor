# Highlights from the Kindle

If you read on a Kindle and highlight as you go, you can take the highlights into [Obsidian](https://obsidian.md) as
notes – just like the notes made with `F4` while reading in Fraktur-Korrektor (see [Usage](usage.md)). Following
Niklas Luhmann’s card index: one highlight per note, each with its source.

## How it works

1. Connect the Kindle to the computer with the USB cable.
2. In the library, below the list of books, click **Kindle highlights to Obsidian …**. If the Kindle appears as a
   drive, the program has already found the file; otherwise choose it with **Choose file …** (where it comes from
   is explained in the next section).
3. Choose the **book**. The ones read most recently are at the top, each with the number of highlights and notes of
   your own.
4. Check the **folder in your Obsidian vault** the notes on this book go into. The program suggests one: if a book
   with the same title is in your library and already has a notes folder, that one – so the notes from the Kindle
   and from Fraktur-Korrektor sit together. Otherwise a new folder named after the book, next to the notes folder of
   the book you opened last. A new last folder is created.
5. **Create notes.** The window says how many there are and shows the folder if you like.

You can also point to the file with **Open …**: the program recognises it and takes you to the same window.

## The file My Clippings.txt

The Kindle writes all highlights, notes and bookmarks into a single file: `My Clippings.txt` in the `documents`
folder.

- **Older Kindles** appear on the computer as a drive, like a USB stick. The program then finds the file by itself.
- **Kindles from 2024 on** (such as the 12th-generation Paperwhite, the Colorsoft and the Scribe) connect as a media
  device. In **Windows** the Kindle appears in Explorer as a device: open the `documents` folder there, drag
  `My Clippings.txt` to the desktop and choose that copy. On a **Mac** you need an extra program, for instance
  Amazon’s *Send to Kindle* app for Mac; its menu *Tools* → *USB File Manager* opens the files on the Kindle (as of
  September 2026).
- Highlights made in the **Kindle app** on a phone or tablet are not in this file, only those made on the device.

## What the notes contain

Every highlight becomes a note, numbered consecutively like the notes from `F4`, for example `12 Page 57.md`:

    **Note**

    Cf. Stumpp, p. 40

    ---

    > The colonists moved east. The way was long.

    Page 57, Location 180–183, [[0 Source|The Journey to Russia]]

- **Page and location.** The page is only there if the e-book carries the page numbers of the printed edition;
  many do not. The location is the Kindle’s own count and finds the place in the e-book again.
- **Your own notes** from the Kindle go on top as the remark above the quotation they belong to. A note without a
  highlight becomes a note without a quotation.
- **Extended highlights.** If you drag a highlight longer on the Kindle, it adds a new entry and leaves the old one
  in place. The program takes only the longer version.
- **The clipping limit.** Some publishers limit how much of a book can be highlighted. Once the limit is reached,
  the Kindle stores only a notice instead of the text. The program says how many highlights are affected.
- **The source note.** With the first note the program creates the file `0 Source.md` in the folder, with title,
  author and the entry *Kindle edition*. Enter the citation there as Zotero gives it – every note links to it with a
  click. A source note that is already there stays as it is.

## After reading on

Simply read the file in again. Highlights that are already notes in the folder are skipped – the program recognises
them by the quotation and the place (page, location). New notes get the next numbers. If you later wrote a note on
the Kindle to a highlight that was already taken over, it is added as a note of its own with the same place; the
existing note is left unchanged. If you changed the quotation or the source line in a note by hand, the program no
longer recognises it and creates the highlight again.

The program changes nothing on the Kindle and never overwrites a note.
