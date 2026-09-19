"""
Baut den Windows-Installer (Inno Setup) aus dist\\Fraktur-Korrektor\\.

Liest die Version aus pyproject.toml, sucht ISCC.exe und ruft
    ISCC.exe /DMyAppVersion=<version> installer.iss
auf. Ergebnis: dist\\installer\\Fraktur-Korrektor_Setup.exe - fester Name ohne
Version, damit der Link releases/latest/download/... stabil bleibt.

Aufruf (nach build.bat bzw. PyInstaller):
    venv\\Scripts\\python.exe scripts\\build_installer.py
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not match:
        sys.exit("version in pyproject.toml nicht gefunden")
    return match.group(1)


def find_iscc() -> str:
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Inno Setup 6" / "ISCC.exe",
        Path(os.environ.get("ProgramFiles(x86)", "")) / "Inno Setup 6" / "ISCC.exe",
        Path(os.environ.get("ProgramFiles", "")) / "Inno Setup 6" / "ISCC.exe",
    ]
    for c in candidates:
        if c.is_file():
            return str(c)
    on_path = shutil.which("ISCC")
    if on_path:
        return on_path
    sys.exit("ISCC.exe nicht gefunden - Inno Setup 6 installieren: https://jrsoftware.org/isdl.php")


def main() -> None:
    if not (ROOT / "dist" / "Fraktur-Korrektor" / "Fraktur-Korrektor.exe").is_file():
        sys.exit("dist\\Fraktur-Korrektor fehlt - zuerst build.bat ausfuehren")
    version = read_version()
    iscc = find_iscc()
    print(f"Inno Setup: {iscc}\nVersion:    {version}")
    result = subprocess.run([iscc, f"/DMyAppVersion={version}", str(ROOT / "installer.iss")], cwd=ROOT)
    if result.returncode != 0:
        sys.exit(result.returncode)
    print("\nInstaller: dist\\installer\\Fraktur-Korrektor_Setup.exe")


if __name__ == "__main__":
    main()
