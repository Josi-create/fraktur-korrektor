#!/bin/bash
# ============================================
# Fraktur-Korrektor - Build fuer macOS
#
# Erstellt dist/Fraktur-Korrektor.app und daraus
# dist/installer/Fraktur-Korrektor-macos-<arch>.dmg (fester Name, damit der
# Link releases/latest/download/... stabil bleibt).
#
# Voraussetzungen:
#   pip install -e . && pip install pyinstaller pillow pyobjc-framework-Cocoa
#   brew install tesseract          (wird mitgeliefert, siehe scripts/prepare_tesseract_mac.py)
#   Xcode Command Line Tools        (otool, install_name_tool, codesign, sips)
#
# Optionale Signierung/Notarisierung ueber Umgebungsvariablen:
#   MACOS_CODESIGN_IDENTITY  -> App + DMG werden Developer-ID-signiert
#   APPLE_ID, APPLE_TEAM_ID, APPLE_APP_SPECIFIC_PASSWORD
#                            -> zusaetzlich notarisiert und gestapelt
# Ohne sie entsteht ein unsignierter Build (zum Testen: Rechtsklick -> Oeffnen).
# ============================================
set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
APP="dist/Fraktur-Korrektor.app"
ARCH="$(uname -m)"
DMG="dist/installer/Fraktur-Korrektor-macos-${ARCH}.dmg"

echo "========================================"
echo "Fraktur-Korrektor - Build (macOS ${ARCH})"
echo "========================================"

if ! "$PYTHON" -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller nicht gefunden. Installiere ..."
    "$PYTHON" -m pip install pyinstaller
fi

echo "Loesche alte Build-Dateien ..."
rm -rf build dist

if [ ! -x vendor/tesseract/tesseract ]; then
    echo "Bereite Tesseract-Laufzeit vor (vendor/tesseract) ..."
    "$PYTHON" scripts/prepare_tesseract_mac.py
fi

if [ ! -f icon.icns ]; then
    echo "Erzeuge icon.icns aus icon.png ..."
    scripts/macos/make_icns.sh
fi

echo
echo "Starte Build (onedir, .app-Bundle) ..."
"$PYTHON" -m PyInstaller fraktur_korrektor.spec --clean --noconfirm

if [ ! -d "$APP" ]; then
    echo "BUILD FEHLGESCHLAGEN - $APP fehlt." >&2
    exit 1
fi

# Selbsttest: startet die gepackte App, fragt den Server und beendet ihn wieder.
echo
echo "Selbsttest der gepackten App ..."
"$PYTHON" scripts/smoke_test.py "$APP"

if [ -n "${MACOS_CODESIGN_IDENTITY:-}" ]; then
    scripts/macos/sign_app.sh "$APP" "$MACOS_CODESIGN_IDENTITY"
    if [ -n "${APPLE_ID:-}" ]; then
        scripts/macos/notarize.sh "$APP"
    fi
else
    echo "HINWEIS: MACOS_CODESIGN_IDENTITY nicht gesetzt - Build bleibt unsigniert."
fi

echo
echo "Erstelle DMG ..."
mkdir -p dist/installer
STAGING="$(mktemp -d)"
cp -R "$APP" "$STAGING/"
ln -s /Applications "$STAGING/Applications"
hdiutil create -volname "Fraktur-Korrektor" -srcfolder "$STAGING" -format UDZO -ov "$DMG"
rm -rf "$STAGING"

if [ -n "${MACOS_CODESIGN_IDENTITY:-}" ]; then
    codesign --force --timestamp -s "$MACOS_CODESIGN_IDENTITY" "$DMG"
    if [ -n "${APPLE_ID:-}" ]; then
        scripts/macos/notarize.sh "$DMG"
    fi
fi

echo
echo "========================================"
echo "BUILD ERFOLGREICH!"
echo "========================================"
echo "App: $APP"
echo "DMG: $DMG"
