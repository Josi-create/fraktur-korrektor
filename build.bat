@echo off
REM ============================================
REM Fraktur-Korrektor - Build fuer Windows (Pendant zu build.sh)
REM
REM Ergebnis: dist\Fraktur-Korrektor\Fraktur-Korrektor.exe und, wenn
REM Inno Setup 6 installiert ist, dist\installer\Fraktur-Korrektor_Setup.exe
REM
REM Voraussetzungen:
REM   pip install -e .[build]
REM   Tesseract (UB Mannheim) installiert - wird mitgeliefert, siehe
REM   scripts\prepare_tesseract.py
REM ============================================

echo.
echo ========================================
echo Fraktur-Korrektor - Build
echo ========================================
echo.

python -c "import PyInstaller" 2>NUL
if errorlevel 1 (
    echo PyInstaller nicht gefunden. Installiere...
    pip install pyinstaller
)

echo Loesche alte Build-Dateien...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Tesseract-Laufzeit samt Modellen bereitstellen (vendor\tesseract)
if not exist "vendor\tesseract\tesseract.exe" (
    echo Bereite Tesseract-Laufzeit vor...
    python scripts\prepare_tesseract.py
    if errorlevel 1 goto :fail
)

echo.
echo Starte Build (onedir)...
pyinstaller fraktur_korrektor.spec --clean --noconfirm
if errorlevel 1 goto :fail

if not exist "dist\Fraktur-Korrektor\Fraktur-Korrektor.exe" goto :fail

echo.
echo Selbsttest der gepackten App...
python scripts\smoke_test.py "dist\Fraktur-Korrektor\Fraktur-Korrektor.exe"
if errorlevel 1 goto :fail

echo.
echo Installer bauen (benoetigt Inno Setup 6)...
python scripts\build_installer.py
if errorlevel 1 (
    echo Installer uebersprungen - siehe Meldung oben.
)

echo.
echo ========================================
echo BUILD ERFOLGREICH!
echo ========================================
echo   dist\Fraktur-Korrektor\Fraktur-Korrektor.exe
echo.
goto :eof

:fail
echo.
echo ========================================
echo BUILD FEHLGESCHLAGEN!
echo ========================================
exit /b 1
