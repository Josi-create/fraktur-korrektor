# Installing the tools

**If you have [installed](install.md) Fraktur-Korrektor, everything you need is already there:** text
recognition with Tesseract and the models for Fraktur and Antiqua come with it. You only need this page if

- you want to clean up difficult scans with **ScanTailor** – that is a separate program, or
- you start Fraktur-Korrektor from the source code (`python server.py`); then Tesseract is missing.

| Program | What for | Needed? |
|---|---|---|
| **Tesseract** | text recognition: [Reading in a PDF or images](pdf-import.md) | included in the finished program |
| **ScanTailor Advanced** | cleaning up poor scans (splitting double pages, deskewing, dewarping) | only for difficult scans |

Fraktur-Korrektor finds both programs by itself if they are installed in the usual place. When you open a PDF,
the window shows what was found.

## Tesseract – only when starting from the source code

**Windows**

1. Download the installer provided by Mannheim University Library:
   <https://github.com/UB-Mannheim/tesseract/wiki> (the file is called something like
   `tesseract-ocr-w64-setup-….exe`).
2. Double-click it and confirm the questions with *Next*. Keep the suggested folder
   (`C:\Program Files\Tesseract-OCR`).
3. Restart Fraktur-Korrektor.

**Mac**

1. If you do not have it yet, install the package manager [Homebrew](https://brew.sh/) (its home page shows
   the one command to paste into the *Terminal* app).
2. In Terminal, type: `brew install tesseract tesseract-lang`
3. Restart Fraktur-Korrektor.

**Linux:** `sudo apt install tesseract-ocr tesseract-ocr-deu` (Debian/Ubuntu) or your distribution's package.

The **Fraktur model** `frak2021` by Mannheim University Library (5 MB) is included in the finished program.
When starting from the source code, Fraktur-Korrektor downloads it by itself the first time you read in a book
and stores it in `~/.fraktur-korrektor/tessdata`. If Fraktur models are already installed (`deu_latf`,
`deu_frak`, `frk`, `Fraktur`), it uses those.

## ScanTailor Advanced

**Windows**

1. From <https://github.com/ScanTailor-Advanced/scantailor-advanced/releases> download the newest file whose
   name ends in `x64.zip` (newer versions without a ZIP file are for Linux only).
2. Unpack the ZIP file (right-click → *Extract All*), for example to `Documents\ScanTailor`. No installation
   is needed; the program is called `scantailor.exe`.
3. In Fraktur-Korrektor, open a PDF; the window then offers **Show me the program …** – click it and select
   this `scantailor.exe`. Fraktur-Korrektor remembers it.

**Mac:** This is where it gets awkward – there is no ready-made ScanTailor for the Mac (as of September 2026
the project publishes files for Windows and Linux only).

- The Homebrew route (`brew install yb85/homebrew-tap/scantailor-advanced`) does not download a finished
  program, it **builds one on your machine**, including the Qt library and its 38 parts. That takes hours. On
  Intel Macs running macOS 26 this applies to every Homebrew package, because ready-made ones are no longer
  provided for them.
- As a stopgap there is an older ready-made program: *ScanTailor Advanced 1.0.18* from 2022, built by yb85,
  <https://github.com/yb85/scantailor-advanced-osx/releases/tag/1.0.18> (file
  `Scantailor-Advanced-v1.0.18-20220508-macos12.dmg`, 29 MB, for Intel Macs). In a test it still started on
  macOS 26, but it is unmaintained and **not signed at all**. macOS therefore refuses to open it the first
  time. To allow it: double-click the program, dismiss the message, then go to *Apple menu → System Settings
  → Privacy & Security* and click **Open Anyway** under *Security*. That button only appears during the hour
  after the attempt.

  (Older, and also available if needed: *ScanTailor Universal 0.2.12* from 2021,
  <https://github.com/trufanov-nok/scantailor-universal/releases/tag/0.2.12>.)

**For a single book the effort rarely pays off.** If your scans are so poor that ScanTailor would be needed,
[Transkribus](transkribus.md) usually gets you there faster.

**Linux:** `.deb` package or AppImage from the page mentioned above, or your distribution's package.

## If a program is not found

When you open a PDF or an image folder, the window shows which programs were found. Click **Show me the program …**
next to the message and select the
program file (`tesseract.exe` or `scantailor.exe`). You can also do it by hand: the path is stored in the file
`~/.fraktur-korrektor/config.json` (on Windows: `C:\Users\<name>\.fraktur-korrektor\config.json`):

    {
      "tesseract": "D:\\Programs\\Tesseract\\tesseract.exe",
      "scantailor": "D:\\Programs\\ScanTailor\\scantailor.exe"
    }

In the same file, `"buecher"` sets the folder in which new books are created (otherwise `Fraktur-Korrektor`
in your home folder), and `"dic"` selects a different dictionary.
