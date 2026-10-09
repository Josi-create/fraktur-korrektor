# Installing the tools

*As of 9 October 2026.*

**If you have [installed](install.md) Fraktur-Korrektor on Windows or on the Mac, everything you need is already
there:** text recognition with Tesseract (version 5.5.3) and the models for Fraktur and Antiqua come with it. You
only need this page if

- you want to clean up curved or stained scans with **ScanTailor** – that is a separate program
  (splitting double pages and straightening crooked pages Fraktur-Korrektor does itself:
  [Preparing the scans](pdf-import.md)), or
- you work on **Linux** – there Tesseract comes from the package manager –, or
- you start Fraktur-Korrektor from the source code (`python server.py`); then Tesseract is missing.

| Program | What for | Needed? |
|---|---|---|
| **Tesseract** | text recognition: [Reading in a PDF or images](pdf-import.md) | included in the finished program on Windows and macOS; install it yourself on Linux |
| **ScanTailor Advanced** | cleaning up poor scans (dewarping, removing stains and margins) | only for difficult scans; double pages and skew the program handles itself |

Fraktur-Korrektor finds both programs by itself if they are installed in the usual place. When you open a PDF,
the window shows what was found; so does the start page while the library is still empty.

## Tesseract – only on Linux and when starting from the source code

**Windows**

1. Download the installer provided by Mannheim University Library:
   <https://github.com/UB-Mannheim/tesseract/wiki> (the file is called something like
   `tesseract-ocr-w64-setup-5.5.3.20260724.exe`).
2. Double-click it and confirm the questions with *Next*. Keep the suggested folder
   (`C:\Program Files\Tesseract-OCR`).
3. Restart Fraktur-Korrektor.

**Mac**

1. If you do not have it yet, install the package manager [Homebrew](https://brew.sh/) (its home page shows
   the one command to paste into the *Terminal* app).
2. In Terminal, type: `brew install tesseract tesseract-lang`
3. Restart Fraktur-Korrektor.

`tesseract-lang` brings the Antiqua model `deu`, and the older Fraktur model `frk` as well; Fraktur-Korrektor still
downloads frak2021 in addition (see below).

**Linux:** `sudo apt install tesseract-ocr tesseract-ocr-deu` (Debian, Ubuntu, Mint) or
`sudo dnf install tesseract tesseract-langpack-deu` (Fedora), or your distribution's package.

The **Fraktur model** `frak2021` by Mannheim University Library (5 MB) is included in the finished program for
Windows and macOS. On Linux and when starting from the source code, Fraktur-Korrektor downloads it by itself the
first time you read in a book (this needs an internet connection once) and stores it in
`~/.fraktur-korrektor/tessdata`. This also applies if an older Fraktur model is already installed (`deu_latf`, `deu_frak`, `frk`,
`Fraktur`) – frak2021 recognises better. Only if the download fails does it use the older one. Which model is
currently there is shown in the window when you open a PDF (“Fraktur model: …”).

## ScanTailor Advanced

**Windows**

1. From <https://github.com/ScanTailor-Advanced/scantailor-advanced/releases> download the newest file whose
   name ends in `x64.zip` – currently `ScanTailor-Advanced-1.1.1x64.zip` of version 1.1.1 (April 2026). The newer
   versions 1.2.0 and 1.2.1 are for Linux only.
2. Unpack the ZIP file (right-click → *Extract All*), for example to `Documents\ScanTailor`. No installation
   is needed; the program is called `scantailor.exe`.
3. In Fraktur-Korrektor, open a PDF; the window then says “ScanTailor is not installed” and offers
   **Show me the program …** next to it – click it and select this `scantailor.exe`. Fraktur-Korrektor remembers it.

**Mac:** This is where it gets awkward – the project itself offers no ready-made ScanTailor for the Mac (as of
October 2026 it publishes files for Windows and Linux only).

- The Homebrew route (`brew install yb85/homebrew-tap/scantailor-advanced`, version 1.0.19) does not download a
  finished program, it **builds one on your machine**. On Macs with an Apple chip the Qt library comes ready-made;
  for Intel Macs there are no ready-made packages of Qt and its 38 parts any more – then everything is built, and
  that takes hours.
- **Recommended:** an older but finished program – *ScanTailor Advanced 1.0.18* from 2022, built by yb85:
  [Scantailor-Advanced-v1.0.18-20220508-macos12.dmg](https://github.com/yb85/scantailor-advanced-osx/releases/download/1.0.18/Scantailor-Advanced-v1.0.18-20220508-macos12.dmg)
  (29 MB, [overview](https://github.com/yb85/scantailor-advanced-osx/releases/tag/1.0.18)). It worked fine on
  macOS 26 in a test. Drag *ScanTailor (Advanced)* from the DMG window into the *Applications* folder – there
  Fraktur-Korrektor finds it by itself. Two things to note:
    - It is built for **Intel Macs**. On Macs with an Apple chip it only runs through *Rosetta*, which macOS
      offers to install the first time.
    - It is **not signed**, so macOS refuses to open it at first. To allow it: double-click the program,
      dismiss the message, then go to *Apple menu → System Settings → Privacy & Security* and click
      **Open Anyway** under *Security*, then enter your login password. That button is only there for about an
      hour after the attempt.

  (Older, and also available if needed: *ScanTailor Universal 0.2.12* from 2021,
  <https://github.com/trufanov-nok/scantailor-universal/releases/tag/0.2.12>.)

**For a single book the effort rarely pays off.** Double pages and crooked pages – the most common case – Fraktur-Korrektor
handles itself ([Preparing the scans](pdf-import.md)). If your scans are so poor beyond that that ScanTailor would be
needed, [Transkribus](transkribus.md) usually gets you there faster.

**Linux:** `.deb` package or AppImage from the page mentioned above (version 1.2.1 of May 2026), or your
distribution's package.

## If a program is not found

When you open a PDF, the window shows which programs were found (for an image folder, only Tesseract); so does
the start page while the library is still empty. Click **Show me the program …** next to the message and select
the program file (`tesseract.exe` or `scantailor.exe`, on the Mac the program *ScanTailor (Advanced)*). You can also do it by hand: the path is stored in the file
`~/.fraktur-korrektor/config.json` (on Windows: `C:\Users\<name>\.fraktur-korrektor\config.json`):

    {
      "tesseract": "D:\\Programs\\Tesseract\\tesseract.exe",
      "scantailor": "D:\\Programs\\ScanTailor\\scantailor.exe"
    }

In the same file, `"buecher"` sets the folder in which new books are created (otherwise `Fraktur-Korrektor`
in your home folder), and `"dic"` selects a different dictionary.
