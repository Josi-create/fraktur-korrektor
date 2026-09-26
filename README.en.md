# Fraktur-Korrektor

[![Download – latest version](https://img.shields.io/github/v/release/Josi-create/fraktur-korrektor?label=Download&style=for-the-badge&color=2e7d32)](https://github.com/Josi-create/fraktur-korrektor/releases/latest)

**Download the latest version:**
[Windows](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor_Setup.exe) ·
[Mac with Apple chip](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-arm64.dmg) ·
[Mac with Intel chip](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-x86_64.dmg) ·
[Linux](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-linux-x86_64.AppImage) –
[how to install](docs/en/install.md)

*Deutsche Fassung: [README.md](README.md)*

**Read, correct and quote old books – on your own computer.**

You have a book printed in Fraktur (German blackletter) as a scan, a PDF or photos taken in an archive, and you want to
work with it: read it, search it, quote from it. Fraktur-Korrektor turns the page images into text and shows both side
by side – the page as printed on the left, the recognised text on the right. Words the program does not know are
marked red. You simply read the book and fix what the text recognition (OCR) got wrong along the way. The result is a
clean, searchable text.

<!-- Screenshot: page image on the left, text on the right, a red word with suggestions (#20) -->

If you take notes as you read, one key turns a marked passage into a note for [Obsidian](https://obsidian.md): the
quotation with the printed page number and a link to the source. A slip box in the manner of Niklas Luhmann's
Zettelkasten grows as you read – the program supplies the excerpts; linking and thinking them through happens in
Obsidian.

Your books and notes never leave your computer. The program is free software (GPL), costs nothing and runs on
Windows, macOS and Linux. It is built for German-language books: the dictionaries cover German spelling from before
1901 to today.

## What it does

- **Reads in what you have.** PDF, scans or photos, EPUB, an export from Transkribus – you show the program the file
  and it works out what it is ([Opening a book](docs/en/add-book.md)). Text recognition with a model for Fraktur is
  built in; afterwards a traffic light shows how well it went and what would help
  ([Reading in a PDF or images](docs/en/pdf-import.md)).
- **Reading and correcting in one pass.** Page image and text move together, red words come with suggestions. The
  dictionary follows the year of publication: »Thür« is correct in a book from 1880. Everything works from the
  keyboard, and every correction is saved at once ([Usage](docs/en/usage.md)).
- **Taking notes.** Notes for Obsidian with quotation, page and line – also from the highlights you made on a Kindle
  ([Highlights from the Kindle](docs/en/kindle.md)).
- **Taking it with you.** Save the book as a PDF: page images, searchable text, table of contents and all your work –
  readable in any PDF viewer, and a book again on another computer ([Saving a book as PDF](docs/en/pdf-sichern.md)).

## Who is it for?

- **Historians** working with printed sources in Fraktur.
- **Genealogists** with village chronicles, local histories and old newspapers from German-speaking regions – text set
  in two columns is read column by column.
- **Anyone who takes reading notes** and keeps them in Obsidian.

This is what a note looks like (the program writes it in the language of its interface):

    **Note**

    (your thought on it)

    ---

    > Die Kolonisten zogen nach Rußland und der Weg war weit.

    Page 57, Line 3–4, [[0 Source|Leibbrandt 1928]]

## Installing

Ready-made programs with everything you need to read in, prepare the scans and correct – including text recognition
and the Fraktur model; nothing else needs installing (Linux: Tesseract from the package manager). Only for
particularly difficult originals – pages curving into the binding, stains, uneven light – can the free program
ScanTailor be added ([Installing the tools](docs/en/install-tools.md)):

| | |
|---|---|
| Windows | [Fraktur-Korrektor_Setup.exe](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor_Setup.exe) |
| Mac, Apple Silicon | [Fraktur-Korrektor-macos-arm64.dmg](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-arm64.dmg) |
| Mac, Intel | [Fraktur-Korrektor-macos-x86_64.dmg](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-x86_64.dmg) |
| Linux (x86_64) | [Fraktur-Korrektor-linux-x86_64.AppImage](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-linux-x86_64.AppImage) |

Step by step, including how to quit and update: [Installing the program](docs/en/install.md). All builds, including
a portable ZIP, are on the [releases page](https://github.com/Josi-create/fraktur-korrektor/releases/latest). To run
the program from source: [CONTRIBUTING.en.md](CONTRIBUTING.en.md#setup-for-developers).

## Help

Everything works from the keyboard; the most important keys are always shown at the bottom, below the image and the text; `F1` opens the help.
The interface is available in English and German (switch at the top right).

- [Help](docs/en/index.md) · [Opening a book](docs/en/add-book.md) · [Reading in a PDF or images](docs/en/pdf-import.md) ·
  [Photographing books yourself](docs/en/fotografieren.md) · [Working with Transkribus](docs/en/transkribus.md) ·
  [Usage](docs/en/usage.md) · [Installing the program](docs/en/install.md) ·
  [Installing the tools](docs/en/install-tools.md) · [FAQ](docs/en/faq.md)
- The same pages as a website: <https://josi-create.github.io/fraktur-korrektor/>

## Contributing

Please report bugs and make suggestions through the [issue templates](../../issues/new/choose) – without page images
or text from the book (copyright). How to help, also without programming (dictionaries, help texts, translation,
test reading), how to run the program from source and what must not break in the code is described in
[CONTRIBUTING.en.md](CONTRIBUTING.en.md); what is planned, in the [ROADMAP](ROADMAP.md) (German). Everyone is
expected to follow the [code of conduct](CODE_OF_CONDUCT.en.md); please report security issues as described in
[SECURITY.en.md](SECURITY.en.md), not as a public issue. Citing: [CITATION.cff](CITATION.cff).

## Support

The program is written in spare time. If you like, buy me a coffee: <https://buymeacoffee.com/josicreate> ☕
Bug reports, wishes and contributions are just as welcome (see above).

## Licence

[GPL-3.0-or-later](LICENSE). The bundled dictionaries have their own licence notes, see [dict/](dict/README.md). PDF
files are handled with PyMuPDF (AGPL-3.0, compatible with the GPL-3.0). The help texts are licensed under
CC BY-SA 4.0.
