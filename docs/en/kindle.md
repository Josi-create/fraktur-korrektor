# Highlights from the Kindle

If you read on a Kindle and highlight as you go, you can take the highlights into [Obsidian](https://obsidian.md) as
notes – just like the notes made with `F4` while reading in Fraktur-Korrektor (see [Usage](usage.md)). Following
Niklas Luhmann’s card index: one highlight per note, each with its source.

## Which books work?

**All books without copy protection** – mainly the ones you put on the Kindle yourself: sent with *Send to Kindle*
or copied with the cable, for instance an e-book you saved with Fraktur-Korrektor (see
[Saving a book as e-book](epub-sichern.md)). Your highlights in them always become notes.

**Purchased books** from the Kindle Store are copy-protected. Newer Kindles store only the place in the book for a
highlight, not the text (see below), and the program cannot get at the encrypted text. From purchased books it
therefore takes only what the Kindle still wrote into the file `My Clippings.txt` – usually everything up to a day in
summer 2026. The window names the purchased books with newer highlights. You find their text in Amazon’s notebook in
the browser: [Highlights from purchased books](kindle-notizbuch.md).

## How it works

1. Connect the Kindle to the computer with the USB cable and **unlock** it (tap or swipe the screen) – while the
   lock screen is showing, the computer cannot see its files. If the Kindle shows a message about the USB
   connection, do **not** tap the button that ends the connection there: otherwise the computer no longer sees it.
2. In the library, below the list of books, click **Kindle highlights to Obsidian …**. In Windows the program finds
   the Kindle by itself and reads its highlights; this takes a few seconds. Otherwise choose the file
   `My Clippings.txt` with **Choose file …** (where it comes from is explained below).
3. Choose the **book**. The ones read most recently are at the top, each with the number of highlights and notes of
   your own and the day of the latest. Books in which you only set bookmarks are named below the list: the Kindle
   stores no text with a bookmark, so it gives no note.
4. Check the **folder in your Obsidian vault** the notes on this book go into. The program suggests one: if a book
   with the same title is in your library and already has a notes folder, that one – so the notes from the Kindle
   and from Fraktur-Korrektor sit together. Otherwise a new folder named after the book, next to the notes folder of
   the book you opened last. A new last folder is created.
5. **Create notes.** The window says how many there are and shows the folder if you like.

You can also point to the file with **Open …**: the program recognises it and takes you to the same window.

## If the Kindle does not show up

- Is the Kindle **unlocked**? Tap the screen and click **Search again** in the window.
- Did you tap the button on the Kindle that ends the USB connection? Then unplug the USB cable and plug it in again.
- If that does not help, plug the cable into another USB socket of the computer.
- Use **another USB cable**. Some cables only charge and carry no data – the Kindle then charges, but the computer
  does not see it.

## Where the Kindle keeps the highlights

Until summer 2026 the Kindle wrote all highlights, notes and bookmarks into a single file: `My Clippings.txt` in the
`documents` folder. Since an update of the Kindle software (version 5.19, summer 2026) nothing new is added there.
New highlights are kept in a database in a hidden folder of the Kindle, and only as the place in the book; the
program reads the text from the book itself. The window does both, you need not do anything for it – it takes what it
finds in both sources, and every highlight only once.

- **In Windows** the program reads both from the connected Kindle. It copies the file, the database and the books
  that have highlights into a folder of its own; it changes nothing on the Kindle.
- **Older Kindles** appear on the computer as a drive, like a USB stick. There, too, the program finds everything by
  itself.
- **On a Mac**, Kindles from 2024 on (such as the 12th-generation Paperwhite, the Colorsoft and the Scribe) do not
  appear in the Finder. With Amazon’s *Send to Kindle* app for Mac, the menu *Tools* → *USB File Manager* opens the
  files on the Kindle (as of September 2026); copy `My Clippings.txt` from the `documents` folder there and choose
  that copy. The new highlights from the database do not reach a Mac yet.
- Highlights made in the **Kindle app** on a phone or tablet are neither in the file nor in the device’s database.
- **A copy goes out of date.** If you copied `My Clippings.txt` by hand, the window names the day of the latest
  entry. If a book is missing, connect the Kindle and open the window again.

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

Simply open the window again. Highlights that are already notes in the folder are skipped – the program recognises
them by the quotation and the place (page, location). New notes get the next numbers. If you later wrote a note on
the Kindle to a highlight that was already taken over, it is added as a note of its own with the same place; the
existing note is left unchanged. If you changed the quotation or the source line in a note by hand, the program no
longer recognises it and creates the highlight again.

The program changes nothing on the Kindle and never overwrites a note.
