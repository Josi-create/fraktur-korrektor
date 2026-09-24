#!/bin/bash
# ============================================
# Fraktur-Korrektor - Linux: AppImage und tar.gz aus dem PyInstaller-Ordner
#
# Erwartet dist/Fraktur-Korrektor/ (pyinstaller fraktur_korrektor.spec) und schreibt
#   dist/installer/Fraktur-Korrektor-linux-x86_64.AppImage      (fester Name fuer releases/latest/download/...)
#   dist/installer/Fraktur-Korrektor-v<version>-linux-x86_64.tar.gz   (Rueckfall ohne FUSE: entpacken, starten)
#
# Tesseract wird unter Linux nicht mitgeliefert: Es kommt aus dem Paketmanager
# (sudo apt install tesseract-ocr tesseract-ocr-deu), das Fraktur-Modell laedt das Programm selbst nach.
#
# appimagetool wird als AppImage geladen und mit --appimage-extract-and-run gestartet, damit auf dem
# Build-Rechner kein FUSE noetig ist. Version festgenagelt (Stand September 2026: 1.9.1); neuere unter
# https://github.com/AppImage/appimagetool/releases. Es haengt die statische Laufzeit aus
# AppImage/type2-runtime an - die braucht auf dem Zielrechner kein libfuse2 mehr.
# ============================================
set -euo pipefail
cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3}"
NAME="Fraktur-Korrektor"
ARCH="${ARCH:-x86_64}"
APPIMAGETOOL_URL="${APPIMAGETOOL_URL:-https://github.com/AppImage/appimagetool/releases/download/1.9.1/appimagetool-${ARCH}.AppImage}"
SRC="dist/$NAME"
APPDIR="build/AppDir"
OUT="dist/installer"
VERSION="$(sed -n 's/^version *= *"\([^"]*\)".*/\1/p' pyproject.toml)"

if [ ! -x "$SRC/$NAME" ]; then
    echo "$SRC/$NAME fehlt - erst: pyinstaller fraktur_korrektor.spec --clean --noconfirm" >&2
    exit 1
fi

echo "== AppDir zusammenstellen (Version $VERSION, $ARCH)"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/share/applications" "$APPDIR/usr/share/icons/hicolor/256x256/apps" "$OUT"
cp -a "$SRC/." "$APPDIR/usr/bin/"
install -m 755 packaging/linux/AppRun "$APPDIR/AppRun"
install -m 644 packaging/linux/fraktur-korrektor.desktop "$APPDIR/fraktur-korrektor.desktop"
cp "$APPDIR/fraktur-korrektor.desktop" "$APPDIR/usr/share/applications/"
# Symbol: 256 px reicht dem Schreibtisch; das grosse icon.png bleibt im Bundle fuer das Fenster des Starters.
"$PYTHON" - <<'PY'
from PIL import Image
im = Image.open("icon.png").convert("RGBA").resize((256, 256), Image.LANCZOS)
im.save("build/AppDir/fraktur-korrektor.png")
im.save("build/AppDir/usr/share/icons/hicolor/256x256/apps/fraktur-korrektor.png")
PY
cp "$APPDIR/fraktur-korrektor.png" "$APPDIR/.DirIcon"

echo "== tar.gz"
cp LICENSE "$SRC/LICENSE.txt"
tar -C dist -czf "$OUT/$NAME-v$VERSION-linux-$ARCH.tar.gz" "$NAME"

echo "== appimagetool laden"
TOOL="build/appimagetool-$ARCH.AppImage"
if [ ! -x "$TOOL" ]; then
    curl -fsSL -o "$TOOL" "$APPIMAGETOOL_URL"
    chmod +x "$TOOL"
fi

echo "== AppImage packen"
# -n: keine AppStream-Pruefung (wir liefern keine Metadaten-Datei mit)
ARCH="$ARCH" "$TOOL" --appimage-extract-and-run -n "$APPDIR" "$OUT/$NAME-linux-$ARCH.AppImage"
chmod +x "$OUT/$NAME-linux-$ARCH.AppImage"

echo
echo "Fertig:"
ls -l "$OUT"
