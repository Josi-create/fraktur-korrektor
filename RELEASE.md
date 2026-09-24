# Veröffentlichen: Installer bauen, signieren, Release

Diese Seite richtet sich an die Betreuung des Projekts, nicht an die Benutzer (für die:
[Programm installieren](docs/de/install.md)).

Gebaut wird von GitHub Actions: [.github/workflows/release.yml](.github/workflows/release.yml). Ein Versions-Tag
`v*` baut den Windows-Installer, das portable ZIP, je ein DMG für Apple Silicon und Intel sowie AppImage und
tar.gz für Linux und hängt alles an ein Entwurfs-Release. **Run workflow** auf der Actions-Seite baut dieselben
Dateien nur zum Prüfen; mit dem Haken **nur_linux** nur den Linux-Teil (`gh workflow run release.yml -f nur_linux=true`).

Ohne die unten beschriebenen Secrets entsteht ein **unsignierter** Mac-Build: Er funktioniert, aber macOS
verweigert beim Doppelklick den Start („kann nicht geöffnet werden, da der Entwickler nicht verifiziert werden
kann“). Erlauben lässt er sich nur über *Systemeinstellungen → Datenschutz & Sicherheit → Dennoch öffnen*; den
früher üblichen Weg über die rechte Maustaste hat Apple abgeschafft, und der Knopf erscheint nur in der Stunde
nach dem Startversuch. Für die Zielgruppe ist das zu viel verlangt – darum die Signatur.

## Einmalig: Apple-Signatur einrichten

Stand September 2026. Die Schritte 1 bis 5 macht man am Mac, Schritt 6 setzt die Secrets für **beide** Projekte
(Fraktur-Korrektor und PDF_Sortier_Meister) – das Zertifikat gilt für alle eigenen Programme.

### 1. Zertifikat „Developer ID Application“ erzeugen

Voraussetzung: Mitgliedschaft im Apple Developer Program, Rolle **Account Holder**. Es sind bis zu fünf solcher
Zertifikate möglich.

Der bequeme Weg führt über Xcode: *Xcode → Settings → Accounts →* Apple-ID auswählen *→ Manage Certificates →*
Knopf **+** unten links *→ Developer ID Application*. Xcode erzeugt den Schlüssel, lädt das Zertifikat und legt
beides in den Schlüsselbund.

Ohne Xcode geht es über <https://developer.apple.com/account/resources/certificates>: **+** → unter *Software*
den Punkt **Developer ID** → **Developer ID Application** → eine Zertifikatsanforderung (CSR) aus der
*Schlüsselbundverwaltung* hochladen (*Schlüsselbundverwaltung → Zertifikatsassistent → Zertifikat einer
Zertifizierungsinstanz anfordern*, „Auf der Festplatte sichern“) → das heruntergeladene `.cer` doppelklicken.

### 2. Nachsehen, wie die Identität heißt

    security find-identity -v -p codesigning

Die Zeile `Developer ID Application: Vorname Name (TEAMID)` ist der Wert für `MACOS_CODESIGN_IDENTITY`; in
Klammern steht die **Team-ID** (`APPLE_TEAM_ID`). Erscheint hier nur „Apple Development“ oder „Apple
Distribution“, fehlt das Developer-ID-Zertifikat noch – diese beiden taugen nicht zur Notarisierung.

### 3. Zertifikat mit privatem Schlüssel als `.p12` sichern

*Schlüsselbundverwaltung → Meine Zertifikate*, das Developer-ID-Zertifikat aufklappen, sodass der private
Schlüssel darunter sichtbar ist. **Beide Zeilen auswählen** (Zertifikat und Schlüssel), rechte Maustaste →
*2 Objekte exportieren …* → Format **Personal Information Exchange (.p12)** → ein Passwort vergeben.

Dieses Passwort wird `MACOS_CERTIFICATE_PASSWORD`. Die `.p12`-Datei außerhalb des Repositorys ablegen, zum
Beispiel im Schreibtischordner.

### 4. `.p12` in Base64 umwandeln

GitHub-Secrets nehmen nur Text auf:

    base64 -i ~/Desktop/developer-id.p12 -o ~/Desktop/developer-id.p12.b64

### 5. App-spezifisches Passwort für die Notarisierung

Die Notarisierung meldet sich mit der Apple-ID an, aber nicht mit dem gewöhnlichen Kennwort. Auf
<https://account.apple.com> anmelden → **Anmelden und Sicherheit** → **App-spezifische Passwörter** → eines
erzeugen (Zwei-Faktor-Authentifizierung ist Voraussetzung). Der angezeigte Wert wird
`APPLE_APP_SPECIFIC_PASSWORD` und ist danach nicht wieder abrufbar.

### 6. Secrets in beiden Projekten hinterlegen

`gh secret set` ohne Wert fragt nach und zeigt nichts an; der Wert des Zertifikats kommt aus der Datei. So
landen die Geheimnisse weder in der Shell-Geschichte noch in einer Datei im Repository:

    for repo in Josi-create/fraktur-korrektor Josi-create/PDF_Sortier_Meister; do
      gh secret set MACOS_CERTIFICATE_P12      --repo $repo < ~/Desktop/developer-id.p12.b64
      gh secret set MACOS_CERTIFICATE_PASSWORD --repo $repo   # Passwort aus Schritt 3
      gh secret set MACOS_CODESIGN_IDENTITY    --repo $repo   # "Developer ID Application: … (TEAMID)"
      gh secret set APPLE_ID                   --repo $repo   # die Apple-ID (E-Mail)
      gh secret set APPLE_TEAM_ID              --repo $repo   # die TEAMID aus Schritt 2
      gh secret set APPLE_APP_SPECIFIC_PASSWORD --repo $repo  # aus Schritt 5
    done
    gh secret list --repo Josi-create/fraktur-korrektor

### 7. Aufräumen

    rm ~/Desktop/developer-id.p12 ~/Desktop/developer-id.p12.b64

Die Zertifikatsdateien und alle sechs Werte gehören **nie** in eine Datei des Repositorys, in einen Commit oder
in eine Protokollausgabe.

## Lokal bauen

    pip install -e ".[build]"
    brew install tesseract        # nur als Quelle; die Modelle lädt scripts/models.py
    ./build.sh                    # dist/Fraktur-Korrektor.app und dist/installer/…-macos-<arch>.dmg

Mit gesetzten Umgebungsvariablen signiert und notarisiert `build.sh` gleich mit:

    export MACOS_CODESIGN_IDENTITY="Developer ID Application: Vorname Name (TEAMID)"
    export APPLE_ID="…@…" APPLE_TEAM_ID="TEAMID" APPLE_APP_SPECIFIC_PASSWORD="…"
    ./build.sh

Die Notarisierung dauert meist wenige Minuten (`xcrun notarytool … --wait`). Ergebnis prüfen:

    spctl --assess --type execute -vvv dist/Fraktur-Korrektor.app     # soll "accepted, source=Notarized Developer ID" sagen
    xcrun stapler validate dist/Fraktur-Korrektor.app

Unter Windows macht `build.bat` dasselbe (Installer nur, wenn Inno Setup 6 installiert ist). Der Windows-Build
bleibt unsigniert; SmartScreen warnt darum beim ersten Start, siehe [docs/de/install.md](docs/de/install.md).

### Linux

Stand September 2026. Unter Linux wird Tesseract **nicht** mitgeliefert – jede Distribution hat es im
Paketmanager, und ein mitgebrachtes Tesseract müsste zu deren Bibliotheken passen. Das Programm findet das
installierte (`/usr/bin/tesseract`) und lädt das Frakturmodell selbst nach. Auf dem Build-Rechner ist Tesseract
nur für den Rauchtest nötig.

    sudo apt install tesseract-ocr tesseract-ocr-deu
    pip install -e ".[build]"
    pyinstaller fraktur_korrektor.spec --clean --noconfirm
    python scripts/smoke_test.py dist/Fraktur-Korrektor/Fraktur-Korrektor
    scripts/build_appimage.sh                                   # dist/installer/…-linux-x86_64.AppImage und …-linux-x86_64.tar.gz
    python scripts/smoke_test.py dist/installer/Fraktur-Korrektor-linux-x86_64.AppImage

`build_appimage.sh` legt aus `dist/Fraktur-Korrektor`, `packaging/linux/AppRun` und
`packaging/linux/fraktur-korrektor.desktop` ein AppDir an und packt es mit
[appimagetool](https://github.com/AppImage/appimagetool/releases) (Version im Skript festgenagelt; läuft dort mit
`--appimage-extract-and-run`, braucht also kein FUSE). Das AppImage bekommt die statische Laufzeit aus
`AppImage/type2-runtime`, die auf dem Zielrechner kein `libfuse2` mehr braucht. Der Workflow baut auf
`ubuntu-22.04`, absichtlich die älteste angebotene Version: Das Programm läuft nur auf Systemen mit mindestens der
glibc des Build-Rechners. Der Starter zeigt unter Linux ein kleines tkinter-Fenster mit *Im Browser öffnen* und
*Beenden* (`starter.linux_ui`); ohne Display fällt er auf die Konsole zurück.

## Die Hilfe als Website

Die Seiten unter `docs/de` und `docs/en` – im Programm die Hilfe unter `/hilfe/…` – stehen als Website unter
<https://josi-create.github.io/fraktur-korrektor/>. Gebaut wird sie mit derselben Vorlage wie im Programm
(`server.help_html`), es gibt keine zweite Quelle. Bei jedem Push auf `main` baut `.github/workflows/pages.yml` die
Seiten und veröffentlicht sie, sobald GitHub Pages in den Einstellungen des Repositorys eingeschaltet ist (Quelle
»GitHub Actions«); vorher wird der Veröffentlichen-Auftrag übersprungen. Lokal ansehen:

    python tools/build_site.py          # schreibt site/ (steht in .gitignore)
    start site\index.html               # Windows; Mac: open site/index.html

## Eine Version veröffentlichen

1. `version` in `pyproject.toml` hochsetzen, `CHANGELOG.md` abschließen, committen.
2. Tag setzen und schieben:

       git tag -a v0.12.0 -m "Version 0.12.0"
       git push origin v0.12.0

3. Der Arbeitsablauf **Installer bauen** läuft (rund 20 Minuten) und legt ein **Entwurfs-Release** mit allen
   Dateien an.
4. Den Entwurf auf der Releases-Seite prüfen, Text ergänzen, veröffentlichen.

Die Dateinamen bleiben von Version zu Version gleich, darum funktionieren diese Dauerlinks in der Doku:

    https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor_Setup.exe
    https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-arm64.dmg
    https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-x86_64.dmg
    https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-linux-x86_64.AppImage

Das portable ZIP und das Linux-tar.gz tragen die Versionsnummer im Namen und sind darum nur über die
Releases-Seite erreichbar.
