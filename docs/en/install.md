# Installing the program

Fraktur-Korrektor is a finished program: download it, double-click, start working. There is **nothing else to
install** – text recognition (Tesseract) and the dictionaries come with it.

All versions are on the [releases page](https://github.com/Josi-create/fraktur-korrektor/releases/latest).

## Windows

1. **Download:**
   [Fraktur-Korrektor_Setup.exe](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor_Setup.exe)
2. Double-click the downloaded file.
3. The first time, Windows will say **“Windows protected your PC”**. This does not mean anything is wrong: the
   message appears for every program that few people have downloaded so far. Click **More info**, then
   **Run anyway**.

   <!-- room for a screenshot of the SmartScreen dialog -->
4. Follow the wizard; the defaults are fine. The program is installed into your user folder, so Windows does not
   ask for an administrator password.
5. Done. Fraktur-Korrektor is now in the **Start menu** and on the desktop.

There is also a version without an installer: unpack `Fraktur-Korrektor-v….-win64.zip` and double-click
`Fraktur-Korrektor.exe` inside. Handy for a USB stick.

## Mac

1. **Which Mac do you have?** Apple menu → *About This Mac*. If “Chip” says **Apple M**, you need the `arm64`
   version; if it says **Intel**, take `x86_64`.
2. **Download:**
   [for Apple Silicon (M1–M4)](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-arm64.dmg)
   · [for Intel](https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-x86_64.dmg)
3. Double-click the downloaded `.dmg`. A window opens showing the program icon and the *Applications* folder.
   **Drag the icon onto the Applications folder.**

   <!-- room for a screenshot of the DMG window -->
4. Close the window and eject the `.dmg` (click the eject symbol in the Finder sidebar).
5. In *Applications*, double-click **Fraktur-Korrektor**.

The Mac needs macOS 15 (Sequoia) or newer.

## The first start

A browser window opens showing the library – the browser is the program’s window. Use **Open …** to point the
program at your first book; see [Opening a book](add-book.md).

The program runs on your computer only and sends nothing to the internet.

**Quitting:** on the Mac use the Dock icon (right-click → *Quit*) or the small book symbol in the menu bar at the
top; on Windows use the icon in the notification area of the taskbar (bottom right, possibly behind the `^`
arrow). Closing the browser window is not enough – the program keeps running.

**No window opened?** Open your browser and go to <http://localhost:8765>.

## Updating

Download the new version and install it the same way; on the Mac drag it into *Applications* again and confirm
replacing it. Your books and settings are untouched.

## Where are my things?

| What | Where |
|---|---|
| books you have read in | folder `Fraktur-Korrektor` in your home folder |
| settings, list of books | folder `.fraktur-korrektor` in your home folder (hidden) |
| the program itself | Windows: `Program Files\Fraktur-Korrektor` · Mac: `Applications/Fraktur-Korrektor.app` |

Back up the `Fraktur-Korrektor` folder now and then – all your work is in there.

## Removing it again

**Windows:** *Settings → Apps → Installed apps → Fraktur-Korrektor → Uninstall*.
**Mac:** drag `Fraktur-Korrektor.app` from *Applications* to the bin.

Your books stay where they are; delete the two folders above by hand if you want to get rid of those as well.
