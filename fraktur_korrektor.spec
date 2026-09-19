# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller-Spec fuer den Fraktur-Korrektor (Windows und macOS).

Einstiegspunkt ist starter.py (Server im Hintergrund, Browser als Fenster, Symbol zum Beenden), nicht
server.py - von der Kommandozeile bleibt server.py unveraendert benutzbar. onedir, weil onefile bei jedem
Start erst entpacken muesste.

Mitgeliefert werden die Woerterbuecher (dict/), die Hilfeseiten (docs/), die Oberflaeche (*.html, i18n.js),
pyproject.toml fuer die Versionsnummer und - wenn scripts/prepare_tesseract*.py gelaufen ist - Tesseract
mit den Modellen frak2021 und deu. Damit muss niemand mehr etwas nachinstallieren.

Aufruf: pyinstaller fraktur_korrektor.spec --clean --noconfirm
"""

import re
import sys
from pathlib import Path

IS_MAC = sys.platform == "darwin"
ROOT = Path(SPECPATH)
NAME = "Fraktur-Korrektor"
ICON = ROOT / ("icon.icns" if IS_MAC else "icon.ico")
VERSION = re.search(r'^version\s*=\s*"([^"]+)"',
                    (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.M).group(1)

datas = [(str(ROOT / n), ".") for n in
         ("reader.html", "bibliothek.html", "i18n.js", "pyproject.toml", "LICENSE", "icon.png")]
datas += [(str(ROOT / "dict"), "dict"), (str(ROOT / "docs"), "docs")]

# Tesseract: die Mach-O- bzw. PE-Dateien als "binaries", damit sie im .app-Bundle in Contents/Frameworks
# landen - ausfuehrbarer Code unter Contents/Resources laesst die Notarisierung scheitern.
binaries = []
TESSERACT = ROOT / "vendor" / "tesseract"
if (TESSERACT / ("tesseract" if IS_MAC else "tesseract.exe")).exists():
    binaries += [(str(p), "tesseract") for p in sorted(TESSERACT.iterdir()) if p.is_file()]
    datas.append((str(TESSERACT / "tessdata"), "tesseract/tessdata"))
else:
    print("HINWEIS: vendor/tesseract fehlt - Build ohne mitgelieferte Texterkennung "
          "(scripts/prepare_tesseract_mac.py bzw. prepare_tesseract.py ausfuehren).")

hiddenimports = [
    # in help_html() erst bei Bedarf importiert
    "markdown.extensions.tables", "markdown.extensions.fenced_code", "markdown.extensions.toc",
]
if IS_MAC:
    hiddenimports += ["AppKit", "PyObjCTools.AppHelper"]   # Dock- und Menueleistensymbol
else:
    hiddenimports += ["pystray", "PIL.Image", "tkinter"]   # Symbol im Infobereich, Dateidialoge

a = Analysis(
    [str(ROOT / "starter.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "PyQt6", "matplotlib", "numpy", "IPython", "jupyter"] + (["tkinter"] if IS_MAC else []),
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # UPX zerstoert auf dem Mac die Signatur und bringt hier wenig
    console=False,      # kein Konsolenfenster; Meldungen kommen als Hinweisfenster (starter.alert)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,   # signiert wird nach dem Build (scripts/macos/sign_app.sh)
    entitlements_file=None,
    icon=str(ICON) if ICON.exists() else None,
)

coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name=NAME)

if IS_MAC:
    app = BUNDLE(
        coll,
        name=NAME + ".app",
        icon=str(ICON) if ICON.exists() else None,
        bundle_identifier="de.josi-create.fraktur-korrektor",
        version=VERSION,
        info_plist={
            "CFBundleName": NAME,
            "CFBundleDisplayName": NAME,
            "CFBundleShortVersionString": VERSION,
            "NSHighResolutionCapable": True,
            "LSApplicationCategoryType": "public.app-category.productivity",
        },
    )
