# Security

*Deutsche Fassung: [SECURITY.md](SECURITY.md)*

## What the program does – and does not do

Fraktur-Korrektor is a local program: a small server on your own computer, the browser is just its window. Started
normally, it listens on `127.0.0.1` only and cannot be reached from any other machine. It downloads nothing from the
internet and sends nothing away – no texts, no words for checking, no usage data. The one exception is the Fraktur
model for Tesseract, fetched from the Mannheim University Library on explicit request (the packaged programs already
include it).

All data stays in book folders on disk and in `~/.fraktur-korrektor` (settings, spell-check cache). What a book
folder contains is described in the [README](README.md#buchordner) (German); none of it is encrypted, none of it
leaves the computer.

### `--lan`

With `--lan` the program can also be reached from other computers in the local network, say from a tablet on the
sofa. Note:

- **There is no password protection.** Anyone on the same network can read and correct. `--lan` is meant for your
  own home network only – not for hotel, university or company networks, and certainly not for exposure to the
  internet (port forwarding).
- **The library can only be changed on the computer itself.** Opening folders, reading in files, the file dialog,
  discarding books, launching ScanTailor, replacing pages, setting the notes folder – everything that reads or
  writes files outside a book folder or launches programs is answered with 403 (`nur_lokal`) for requests from the
  network. From the network, only reading and correcting the already opened books is possible.
- Windows asks for a firewall exception the first time you start with `--lan`; "Private networks" is enough.

Access protection for `--lan` is on the [ROADMAP](ROADMAP.md) under "Später" (later).

### What is in your hands

- **Book folders and scans** are subject to the copyright of the respective work. The program does not check that;
  only pass on book folders, saved PDFs and bug reports containing book content if you are allowed to.
- **Packaged programs** should only be downloaded from the
  [releases page](https://github.com/Josi-create/fraktur-korrektor/releases). The Mac app is signed and notarised;
  Windows still shows the SmartScreen warning on first start (see [FAQ](docs/en/faq.md)).

## Supported versions

Security fixes are provided for the latest released version. Older versions are not maintained; please update.

## Reporting a vulnerability

If you believe you have found a vulnerability that could endanger others (for example: files can be read from the
LAN despite the block, a crafted PDF or EPUB executes code when read in, an address gives access outside the book
folder), please do **not** report it publicly as an issue, but:

1. **Preferably** via GitHub: *Security → Report a vulnerability* on the repository page (a private report to the
   maintainer). If that button is not available to you, then:
2. via the address given in the [maintainer's GitHub profile](https://github.com/Josi-create).

Please describe how to reproduce it, with which version and on which system. You will get a reply within 14 days; a
fix is released as a new version with a note in the [CHANGELOG](CHANGELOG.md). If you would like to be credited, say so.

Everything else – crashes, words wrongly marked red, messages you do not understand – belongs in the issue tracker
as an ordinary [bug report](../../issues/new/choose).
