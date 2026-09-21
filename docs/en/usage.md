# Usage

Page image on the left, text on the right. The **reading line**, highlighted in yellow, always stays at the
same height; image and text move together. Red marks words the dictionary does not know; orange marks
places where an automatic pre-correction made an uncertain replacement.

The program has three states, shown in the top bar: **Reading** (green), **Correction** (red) – a red word
is being changed – and **Edit line** (orange).

## Keys

| Mode | Key | Effect |
|---|---|---|
| Reading | `↓` `↑` (or `j` `k`), mouse wheel | next / previous line; the text flows across page breaks. Clicking a line makes it the reading line |
| Reading | `Space` | jump to the next red word → correction |
| Reading | double-click a word | correct this line, with the clicked word selected |
| Reading | `F8` | first red word of the reading line is correct → whitelist. `F8` again = the next one. With no red word in the reading line: the next one further down the page |
| Reading | `Enter` | if the reading line has a red word: go there; otherwise like `F2` |
| Reading | `F2` | edit the reading line freely (punctuation, footnote marks, anything the automatic check misses) |
| Reading | `PgDn` `PgUp`, `Home` `End`, `G` | page forward/back, top/bottom of page, go to page |
| Reading | `+` `−` `0` | zoom the page image |
| Reading | `R` | reload the page (after changes in another editor) |
| Correction | `Enter` | apply and read on (if the same line has another red word, that comes first) |
| Correction / Edit line | `F7` | insert the hyphenation mark `¬` at the cursor |
| Correction / Edit line | `Shift`+`Enter` | split the line at the cursor (see below) |
| Correction | `F8` | word is correct → whitelist |
| Correction | `Tab` | next red word without changing anything |
| Correction | `Esc` | back to reading without changing anything |
| Reading / Correction | `F9` | batch correction (see below) |
| Reading | `U` | undo the last batch correction |
| Reading | `F` | footnotes start at the reading line (see below) |
| Reading | `T` | table: turn separate lines into a table, or dissolve it again (see below) |
| Reading | `H` | heading: level 1 → 2 → 3 → none (see below) |
| Reading | `V` | join the reading line with the next line |
| Reading | `W` | show the whitelist |
| Reading | `D` | dictionary: which spelling applies to this book (see below) |
| Reading / Correction | `F4` or right-click the selection | note for Obsidian from the selected passage, otherwise from the reading line (see below) |
| Reading | `N` | set the notes folder for this book |
| anywhere | `F1` | this help |

## Hyphenated words

Words split at the end of a line are written with the mark `¬`: `Zu¬` / `kunft`. Both parts are checked
together. When correcting, both lines appear as input fields. `F7` inserts the mark.

## Batch correction (F9)

The same misreading often occurs dozens of times in a book (`ber` for “der”, `bie` for “die”). Batch
correction lists every occurrence of a word at once and replaces them after a quick look at the image
snippets.

- After correcting, say, `ber` → `der`, you see the hint “‘ber’ occurs 74 more times in the book – F9 lists
  them all”.
- In correction mode `F9` takes the current red word; you type the replacement.
- In reading mode you enter both words yourself.

Each occurrence shows page and line, the image snippet with a red frame, and the text. All occurrences are
ticked to begin with; words split across line ends are found as well.

| Key | Effect |
|---|---|
| `↓` `↑` | move through the list |
| `Space` | tick / untick |
| `A` | all on / all off |
| `Tab` | change the replacement |
| `Enter` | replace all ticked occurrences |
| `Esc` | cancel |

`U` in reading mode undoes the last batch. Lines you have changed by hand since then are left alone.

## Footnotes (F)

In the text file, footnotes follow a line `---` and always run to the end of the page. `F` sets or moves
this separator to just before the reading line. If the reading line is the first footnote line, `F` removes
the separator again.

## Splitting and joining lines

Sometimes text recognition misses a line break – two lines (or two table cells) end up in one – or it makes one too many.

- **Split:** edit the line (`F2` or `Enter`), put the cursor at the place and press `Shift`+`Enter`. Whatever you have
  already changed in the field is applied along with it.
- **Join:** in reading mode press `V` – the reading line is joined with the next one. If it ends with the hyphenation mark
  `¬`, the split word is pulled together (`Zu¬` + `kunft` → `Zukunft`).

The program also splits or merges the **image area** of the line (when splitting, proportionally at the split point). This
way every line of text keeps its place in the page image – unlike changing the number of lines in another editor. Inside a
table, the table is renumbered afterwards: shifted columns fall back into place.

## Tables (T)

Text recognition usually tears tables apart into single lines – a listing turns into

    im Jahre 1811
    16 842 Eimer,
    1812-
    12 409

Put the reading line on the first line and press `T`. Use `↓` to extend the range to the last line of the table and
`2` … `9` to choose the number of columns; the preview at the top shows at once how the lines are distributed over rows and
columns (in order, from left to right). `H` turns the first row into column headers, `Enter` applies, `Esc` cancels. `T` on
an existing table removes the markup again – the text stays.

The program does not invent a format of its own for this; it writes the same markup into the text that an EPUB uses
(XHTML):

    <table><tr><td>im Jahre 1811</td>
    <td>16 842 Eimer,</td></tr>
    <tr><td>1812-</td>
    <td>12 409</td></tr></table>

Every line stays a line – one cell per line – so that the alignment with the page image is kept. You never get to see these
control characters in the program: on the right the finished **table appears as a table**, with borders and columns, and the
input field, too, shows only the content of the cell. The reading cursor moves cell by cell, and the matching place in the
page image is highlighted on the left. The word check skips the markup. You correct the content of the cells like any
other text (delete superfluous dashes as in `1812-` with `F2`).

**Shifted columns:** if two cells are in one line (`1812- 12 409`) because text recognition missed the line break, all
columns from there on shift by one. Split the line at that place (`F2`, position the cursor, `Shift`+`Enter`) – before or
after creating the table; an existing table is renumbered by the program afterwards.

Limitation: the cells have to be in reading order (row by row). If text recognition read a table column by column, it cannot
be marked up this way.

## Headings (H)

`H` marks the reading line as a heading: level 1 the first time (`<h1>…</h1>`), the next level with each further press,
ordinary text again after level 3. Headings are shown larger and bold, without visible control characters. A later EPUB export can build chapters and the table
of contents from them.

If you like, you can also enter further markup by hand with `F2`; the program knows `<em>`, `<strong>`, `<i>`, `<b>`,
`<sup>`, `<sub>`, `<p>`, `<blockquote>` and `<br/>`, does not treat them as words, and shows font markup (italic, bold,
superscript, subscript) as such.

## Whitelist (W)

The whitelist holds the words you confirmed with `F8` (names, places, old spellings). `W` shows it, newest
first, with a filter. `Del`, `Space` or a click removes a word or restores it – it then turns red again in
the book.

## Dictionary (D)

Whatever the dictionary does not know turns red – so the dictionary has to suit the book. `D` (or “Dictionary” in the top
bar) shows three tick boxes; the choice applies to this book only and is saved:

| Tick box | Examples | What for |
|---|---|---|
| Accept spellings from before 1901 | Thür, Noth, seyn, giebt, civilisiren | 19th-century prints – and newer works that quote old sources verbatim |
| German spelling 1901 to 1996 | daß, Schiffahrt, rauh | most Fraktur prints, everything up to the spelling reform |
| Reformed spelling (from 1996) | dass, Schifffahrt, rau | newer books, scripts, papers |

When a book is read in, the program estimates the **year of publication** from the title pages and imprint and ticks the
boxes accordingly: before 1902 the first two, up to 1997 the middle one, from 1998 the lower two (the changeover took
years, and newer works quote older texts). After every change the window shows how many red words the book had before and
has now – so you see at once what fits. Genuine misreadings (`ber`, `bie`, `Bolk`) stay red in every setting.

Independently of this, the following always count as correct: common abbreviations (Vgl, Bd, Ebd, Hg, Bible references
such as Offb, Joh), sigla in capitals that occur more than once (BWKG, LKA), and longer words that occur at least three
times in the book (mostly names). A name that is still red is confirmed once with `F8` – this then applies to every
occurrence.

## Notes for Obsidian (F4)

If you take excerpts while reading, every passage can become a note in [Obsidian](https://obsidian.md) – modelled on
Niklas Luhmann's Zettelkasten: one thought per note, each with its source.

1. Once per book: press `N` (or “Notes” in the top bar) and enter the folder in your Obsidian vault where the notes on
   this book belong, e.g. `…/Vault/Research/Leibbrandt 1928`. The “Choose folder …” button opens the file dialog; a
   missing last folder is created. The choice is stored in `buch.json`.
2. While reading, select a passage with the mouse – across several lines if you like – and press `F4`, or right-click the
   selection. Without a selection the reading line becomes the note, so it works without a mouse at all.

The program creates a file in that folder, numbered consecutively, for example `07 Page 57.md`:

    **Note**



    ---

    > Die Kolonisten zogen nach Rußland und der Weg war weit.

    Page 57, [[0 Source|Leibbrandt 1928]]

At the top room for your own remark, below the rule the quotation (words hyphenated at line ends are joined) and the
page – the printed page number from the running head, otherwise the PDF page – and a link to the book's source note. The
program creates that file, `0 Source.md`, as a template with the first note; enter there where the book comes from
(university library, interlibrary loan …) and the citation as Zotero gives it. This way every note is one click away
from its full source. The quotation is also placed on the clipboard.

If Obsidian is installed, it opens the new note immediately and, on Windows, comes to the front (the folder has to be inside a vault Obsidian knows).
Without Obsidian the file simply stays in the folder – it is plain Markdown.

## Reading along on the home network

If the program is started with the option `--lan`, other devices on the same network can reach it (the
address is shown in the window at start-up). There is no password protection – use it on your own home
network only. Books can only be added on the computer the program runs on.
