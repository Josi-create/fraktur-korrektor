# Contributing to Fraktur-Korrektor

*Deutsche Fassung: [CONTRIBUTING.md](CONTRIBUTING.md)*

Thank you for wanting to help. Fraktur-Korrektor is a small program with one clear aim: reading the OCR text of
scanned books and correcting it as you read – page image on the left, text on the right, everything from the
keyboard. It runs locally; nothing goes to the internet. The people it is built for are historians, librarians,
genealogists – people who want to read a book, not a command line. Every change is measured against that: no jargon
in the interface, error messages that say what to do next, one clear recommendation instead of a choice without advice.

## Helping without programming

Much of what makes the program better needs no code:

- **Proofreading with real books.** Open a book of your own (PDF, Transkribus export, EPUB, folder of images) and
  report where it gets in your way: a message you did not understand, a button you looked for, a word that was
  wrongly red. Reports like these are the most valuable – open an [issue](../../issues/new/choose).
- **Dictionaries.** `dict/zusatz.txt` lists words and abbreviations that should count as correct (scholarly
  apparatus, Bible references, sigla); `dict/fallen.txt` lists words that are in the dictionary but are almost always
  a misreading ("baß" for "daß"). Both are plain text files, one word per line. Please include an example of where
  the word occurred.
- **Help pages.** The help lives as Markdown in `docs/de` and `docs/en` and is shown in the program under `F1`. If an
  explanation is unclear or a question you had is missing, improve or add it. Every page exists in both languages
  under the same file name; if you can only write one language, write that one and say so in the pull request.
- **Translation.** All interface texts are in `i18n.js`, German and English side by side. Better wording is welcome,
  especially in English.

## Reporting bugs and suggesting features

Please use the [issue templates](../../issues/new/choose): bug report or suggestion. For a bug, the operating
system, the program version (shown at the bottom of the library), how the book got into the program and the exact
wording of the message all help. **Do not upload page images or text from your books** unless they are in the public
domain – copyright applies to scans too. A short excerpt in your own words is usually enough.

What the program does not do and is not meant to do is in the [ROADMAP](ROADMAP.md) (German): it does not replace
text recognition; it helps you read and correct what Tesseract or Transkribus produced.

## Setup for developers

Requirements: Python 3.10 or newer, Git. Tesseract is only needed to read in PDFs and images yourself; the tests run
without it (in CI, the run with real Tesseract happens on Linux only).

    git clone https://github.com/Josi-create/fraktur-korrektor.git
    cd fraktur-korrektor
    pip install -e .[dev]
    pytest
    python server.py

On a Mac, `./mac_lesen.sh` creates the `.venv` and starts the server; `./mac_lesen.sh test` runs the tests. How the
installers are built is described in [RELEASE.md](RELEASE.md) (German).

### Your own test environment – never against real books

The program writes into book folders (text files, log, bookmark) and into `~/.fraktur-korrektor` (settings, cache).
So when trying things out, always use:

- a **separate instance on another port** (`--port 8899`), not the one you are reading in;
- `FRAKTUR_HOME` pointing to a **throwaway folder**, so your everyday settings and library stay untouched;
- a **copy** of a book folder or the throwaway book from `tests/conftest.py`, never the book you are working on.

`tests/conftest.py` shows the pattern: it builds a small book in a temp folder, finds a free port and starts its own
server for it.

What pytest cannot see only shows up in the browser – JavaScript errors, for instance. For reproducing there are
self-test entry points: `/buch/<id>?notrans&keys=Space,F2,caret=6,Shift+Enter` replays keys,
`/bibliothek#auto=<path>` reads a file in with the recommended setting right away, `#open=<path>` opens the
dialog. Whatever cannot be checked automatically at all (file dialog, launching ScanTailor, double-clicking the app)
should be named explicitly in the pull request so someone tries it by hand.

## Layout

| File | Purpose |
|---|---|
| `server.py` | HTTP server (standard library only), class `Book`, library, background jobs, help rendering |
| `korrlib.py` | dictionaries (`Checker`, Hunspell via spylls, cache), spelling by period, tokenisation, markup (`make_table`, `heading`, `mask`) |
| `finder.py` | detects what a file or folder contains (book, PDF, EPUB, images, Transkribus export) and recommends |
| `ocr.py` | PDF/images → Tesseract or existing text layer; quality traffic light; find/launch ScanTailor |
| `scans.py` | preparing scans: splitting double pages, deskewing |
| `epub.py` | reading EPUB; text-only book; laying EPUB wording over the lines of a PDF (`transplant`) |
| `pagexml.py` | Transkribus PAGE XML, hOCR, ALTO → book folder; `classify` (running head, footnotes), column detection |
| `pdfbuch.py` | saving a book as PDF (images, invisible text layer, working state as attachment) and reading it back |
| `merge.py` | merging two working states of the same book |
| `starter.py` | launch as packaged app (icon in the Dock or system tray) |
| `reader.html`, `bibliothek.html`, `i18n.js` | interface; all texts bilingual in `i18n.js` (`t('key')`) |
| `docs/de`, `docs/en` | help: same file names in both languages, served at `/hilfe/<lang>/<page>` |
| `dict/` | bundled dictionaries (GPL) with licence texts, `zusatz.txt`, `fallen.txt` |
| `tests/` | pytest; every test gets a throwaway book and its own server |
| `tools/` | older command-line tools (autokorr, build_text …) |

A **book folder** contains `NNN.txt` (one file per page: optional `# running head`, body text, `---`, footnotes),
`lines.json` (line geometry), `img/NNN.jpg|png`, plus `whitelist.txt`, `lesezeichen.json`, `korrekturen.log`,
`buch.json` (identifier, year of publication, applicable spelling) and `qualitaet.json`. Settings live in
`~/.fraktur-korrektor` (override with `FRAKTUR_HOME`), new books in `~/Fraktur-Korrektor`.

## What must not break

These rules are not style; they are load-bearing walls. A pull request that breaks one of them will not be merged,
however good it is otherwise.

1. **Line count = image mapping.** The text lines of a page are mapped in order to the lines in `lines.json`
   (`Book.geo_seq`). Whoever changes the number of lines must update `lines.json` along with it – as `split_line`
   and `join_lines` do. That is also why markup is line by line: a table cell is one line.
2. **Markup is XHTML as in EPUB** (`<table><tr><td>`, `<h2>`, `<em>` …), no format of our own. The spell check
   skips it (`korrlib.mask`); character positions always refer to the real line. The reader renders it, never shows it.
3. **Every change checks that the line still looks as it did in the browser** (send `old`, else 409): the text
   files may be edited in an editor at the same time. Every change is written to `korrekturen.log`.
4. **Never overwrite.** Imports create "(2)" when a name already exists; only what the program created itself and
   that holds no work yet may be discarded (`discard`). Whatever gets replaced is saved first as `vorher-<date>.zip`.
5. **The library is only changed locally.** Opening, importing, the file dialog – everything that reads or writes
   files outside the book – is blocked for requests from the LAN (`H.local`). New endpoints of that kind belong
   behind the same check.
6. **`main` is always usable** and file formats stay backwards compatible: existing book folders must keep working
   with every new version, as must `python server.py <bookfolder> --lan`.
7. **Nothing goes to the internet.** The program downloads nothing and sends nothing away – not even words for
   checking. The only exception is fetching the Fraktur model for Tesseract on explicit request.
8. **Every book has its own address** `/buch/<id>/…` so several books and tabs can be open side by side.

## Style

- **Code like the existing code:** terse, German identifiers and comments that explain the *why*, not the what. No
  new dependencies without good reason; the server gets by with the standard library.
- `server.py`, `reader.html` and `README.md` have **CRLF line endings** – keep them, or the diff becomes unreadable.
- In `reader.html` and `bibliothek.html`, **never declare a local variable `t`**: it would shadow the translation
  function `t()` (a test checks for this).
- **Every interface text goes into `i18n.js` in German and English**; every help page into both language folders
  under the same name. Tests check completeness.
- **Error messages name the next step** and avoid jargon. The user need not know what a "Transkribus export" is –
  the program recognises it.
- **Verify external facts** (download addresses, package names, Apple procedures) instead of writing them from
  memory, and date them where they may go stale.
- **Book data, scans and texts do not belong in the repository** – not even as test data (copyright). The tests build
  their own book.
- **New logic gets tests**; `pytest` must stay green on Windows, macOS and Linux (CI checks all three).
- Every visible change gets an entry in [CHANGELOG.md](CHANGELOG.md) under *Unveröffentlicht* (unreleased). The
  changelog is kept in German; an English entry is fine, it will be translated.

## Pull requests

1. Open a short issue first, or say in an existing one that you are taking it on – that avoids duplicate work,
   especially for interface changes.
2. Fork and branch; small, self-contained changes. Commit messages in German or English, in the form "what changes
   and why", with `Closes #…` when an issue is resolved.
3. Tick the [checklist in the pull request template](.github/PULL_REQUEST_TEMPLATE.md): tests green, both
   languages, changelog, no book data.
4. By contributing you agree that your contribution is published under [GPL-3.0-or-later](LICENSE) (help texts under
   CC BY-SA 4.0).

The [Code of Conduct](CODE_OF_CONDUCT.en.md) applies to everyone. Questions are welcome – preferably in the
[Discussions](https://github.com/Josi-create/fraktur-korrektor/discussions), or when in doubt just open an issue.
