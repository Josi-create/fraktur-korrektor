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
| Correction | `F8` | word is correct → whitelist |
| Correction | `Tab` | next red word without changing anything |
| Correction | `Esc` | back to reading without changing anything |
| Reading / Correction | `F9` | batch correction (see below) |
| Reading | `U` | undo the last batch correction |
| Reading | `F` | footnotes start at the reading line (see below) |
| Reading | `W` | show the whitelist |
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

## Whitelist (W)

The whitelist holds the words you confirmed with `F8` (names, places, old spellings). `W` shows it, newest
first, with a filter. `Del`, `Space` or a click removes a word or restores it – it then turns red again in
the book.

## Reading along on the home network

If the program is started with the option `--lan`, other devices on the same network can reach it (the
address is shown in the window at start-up). There is no password protection – use it on your own home
network only. Books can only be added on the computer the program runs on.
