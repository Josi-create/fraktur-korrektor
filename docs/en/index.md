# Help

Fraktur-Korrektor is a reading and proofreading tool for text that OCR software has extracted from scanned
books – especially German books printed in Fraktur (blackletter). The page image is on the left, the
recognised text on the right. Words the program does not know are marked red. You simply read the book
and fix what you notice along the way. The result is a clean text.

The program runs entirely on your own computer. Nothing is sent to the internet; the browser merely serves
as its window.

## Three steps

1. **Text recognition** – the book is read by OCR software such as
   [Transkribus](https://www.transkribus.org/). This happens outside this program.
2. **Add the book** – bring the result into the library: [Adding a book](add-book.md).
3. **Read and correct** – [Usage](usage.md). Everything works from the keyboard; the most important keys
   are always shown at the top right.

## Good to know

- **Every correction is saved immediately**, straight into the text files of the book folder. There is no
  “Save”. In addition, the program records each change in `korrekturen.log`.
- **Your reading position** is remembered for each book.
- **Backup:** copy the whole book folder from time to time – it contains all your work.
- **The first time** a book is opened, every word is checked against the dictionary. This can take up to a
  minute; afterwards it is fast.
- The bundled dictionary covers German spelling from 1901 to 1996 (“daß”, “Schiffahrt”). Older spellings
  such as “Thür” or “giebt” show up red; `F8` makes the program remember a word as correct.
