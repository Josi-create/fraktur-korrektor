#!/bin/bash
# ============================================
# Fraktur-Korrektor – Schnellstart auf dem Mac (für den Betreiber und Entwickler)
#
#   ./mac_lesen.sh                      Bibliothek öffnen (Server + Browser)
#   ./mac_lesen.sh <buchordner> --lan   ein Buch öffnen, auch für andere Rechner im Netz
#   ./mac_lesen.sh --port 8766          alle Argumente von server.py gehen durch
#   ./mac_lesen.sh build                die Mac-App und das DMG bauen (lokal, kein GitHub)
#   ./mac_lesen.sh app                  die zuletzt gebaute App starten
#   ./mac_lesen.sh test                 die Tests laufen lassen
#
# Legt beim ersten Mal die Python-Umgebung .venv an und installiert das Programm darin.
# Für »build« muss Tesseract da sein (brew install tesseract); Einzelheiten stehen in build.sh.
# ============================================
set -euo pipefail
cd "$(dirname "$0")"

PY=.venv/bin/python

venv() {  # .venv anlegen und das Programm samt Entwicklungswerkzeugen hineininstallieren – nur, wenn es fehlt
    if [ ! -x "$PY" ]; then
        echo "Lege die Python-Umgebung .venv an ..."
        python3 -m venv .venv
        "$PY" -m pip install --quiet --upgrade pip
        "$PY" -m pip install --quiet -e ".[dev]"
    fi
}

case "${1:-}" in
    build)
        venv
        if ! "$PY" -c "import PyInstaller" 2>/dev/null; then
            echo "Installiere die Build-Werkzeuge (PyInstaller) in .venv ..."
            "$PY" -m pip install --quiet -e ".[build]"
        fi
        PYTHON="$PY" ./build.sh
        open dist/installer
        ;;
    app)
        if [ ! -d dist/Fraktur-Korrektor.app ]; then
            echo "Noch keine App gebaut – erst: ./mac_lesen.sh build" >&2
            exit 1
        fi
        open dist/Fraktur-Korrektor.app
        ;;
    test)
        venv
        shift
        "$PY" -m pytest -q "$@"
        ;;
    -h|--help|help)
        sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
        ;;
    *)
        venv
        exec "$PY" server.py "$@"
        ;;
esac
