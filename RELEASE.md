# Veröffentlichen: Installer bauen, signieren, Release

Diese Seite richtet sich an die Betreuung des Projekts, nicht an die Benutzer (für die:
[Programm installieren](docs/de/install.md)).

Gebaut wird von GitHub Actions: [.github/workflows/release.yml](.github/workflows/release.yml). Ein Versions-Tag
`v*` baut den Windows-Installer, das portable ZIP, je ein DMG für Apple Silicon und Intel sowie AppImage und
tar.gz für Linux, lässt alle Tests laufen und veröffentlicht das Release, wenn alles grün ist – siehe
[Eine Version veröffentlichen](#eine-version-veröffentlichen). **Run workflow** auf der Actions-Seite baut dieselben
Dateien nur zum Prüfen; mit dem Haken **nur_linux** nur den Linux-Teil (`gh workflow run release.yml -f nur_linux=true`).

Ohne die unten beschriebenen Secrets entsteht ein **unsignierter** Mac-Build: Er funktioniert, aber macOS
verweigert beim Doppelklick den Start („kann nicht geöffnet werden, da der Entwickler nicht verifiziert werden
kann“). Erlauben lässt er sich nur über *Systemeinstellungen → Datenschutz & Sicherheit → Dennoch öffnen*; den
früher üblichen Weg über die rechte Maustaste hat Apple abgeschafft, und der Knopf erscheint nur in der Stunde
nach dem Startversuch. Für die Zielgruppe ist das zu viel verlangt – darum die Signatur.

Unter Windows gilt dasselbe mit SmartScreen („Der Computer wurde durch Windows geschützt“). Dort signiert die
SignPath Foundation, sobald das Secret `SIGNPATH_API_TOKEN` gesetzt ist – siehe
[Einmalig: Windows-Signatur einrichten](#einmalig-windows-signatur-einrichten-signpath-foundation).

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

Die Zeile `Developer ID Application: Vorname Name (TEAMID)` ist die gesuchte; in Klammern steht die **Team-ID**
(`APPLE_TEAM_ID`). Als `MACOS_CODESIGN_IDENTITY` taugt der Name, sicherer ist aber der 40-stellige Fingerabdruck
am Zeilenanfang: Ein eingetippter Umlaut im Namen kann anders kodiert sein als im Zertifikat, dann findet
`codesign` die Identität nicht. Erscheint hier nur „Apple Development“ oder „Apple
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
      gh secret set MACOS_CODESIGN_IDENTITY    --repo $repo   # Fingerabdruck oder "Developer ID Application: … (TEAMID)"
      gh secret set APPLE_ID                   --repo $repo   # die Apple-ID (E-Mail)
      gh secret set APPLE_TEAM_ID              --repo $repo   # die TEAMID aus Schritt 2
      gh secret set APPLE_APP_SPECIFIC_PASSWORD --repo $repo  # aus Schritt 5
    done
    gh secret list --repo Josi-create/fraktur-korrektor

### 7. Aufräumen

    rm ~/Desktop/developer-id.p12 ~/Desktop/developer-id.p12.b64

Die Zertifikatsdateien und alle sechs Werte gehören **nie** in eine Datei des Repositorys, in einen Commit oder
in eine Protokollausgabe.

## Einmalig: Windows-Signatur einrichten (SignPath Foundation)

Stand September 2026. Die [SignPath Foundation](https://signpath.org) signiert Open-Source-Projekte kostenlos, direkt
aus GitHub Actions und ohne Hardware-Schlüssel; als Herausgeber steht dann „SignPath Foundation“ in der Signatur.
Ganz verschwindet die SmartScreen-Warnung damit nicht sofort: Seit 2024 bekommt kein Zertifikat mehr von vornherein
Vertrauen, das Ansehen wächst mit den Downloads – aber über alle Versionen hinweg statt bei jeder neu.

Was der Workflow tut: Ohne das Secret baut er unsigniert wie bisher. Mit ihm schickt er je Version **zwei**
Signieranfragen – erst `Fraktur-Korrektor.exe`, dann den daraus gebauten Installer (in eine Inno-Setup-Datei kann
SignPath nicht hineinsignieren). Signiert werden nur diese beiden Dateien, denn die Foundation signiert nur, was aus
dem eigenen Quelltext entsteht; Python, Tesseract und die Bibliotheken bleiben unsigniert, ebenso der Deinstaller
`unins000.exe`, den Inno Setup erst bei der Installation anlegt (SmartScreen prüft ihn nicht, er wird nicht
heruntergeladen). Vorher prüft `scripts/check_exe.ps1` Produktname und -version in den Datei-Eigenschaften; die
Artifact Configuration lässt SignPath das Programm nur mit dem Produktnamen „Fraktur-Korrektor“ signieren. Beim
Installer prüft SignPath den Namen nicht, denn Inno Setup füllt ihn in der Setup.exe mit Leerzeichen auf feste
Breite auf, und ob SignPath beim Vergleich Leerzeichen abschneidet, ist nicht dokumentiert. Verlangt SignPath bei
der Einrichtung auch dort eine Namensprüfung, erst mit einem Probelauf (Schritt 5) ausprobieren.

Die Regeln, die SignPath auf der Projektseite verlangt (Rollen, Datenschutz, der Satz „Free code signing provided
by SignPath.io, certificate by SignPath Foundation“), stehen in der Hilfeseite
[Signatur und Datenschutz](docs/de/code-signing.md) ([englisch](docs/en/code-signing.md)); das README verlinkt sie.

### 1. Zwei-Faktor-Anmeldung bei GitHub

Pflicht für jeden mit Schreibrecht: <https://github.com/settings/security> → *Two-factor authentication*.

### 2. Antrag stellen

Formular unter <https://signpath.org/apply>:

- Repository: `https://github.com/Josi-create/fraktur-korrektor`, Lizenz GPL-3.0-or-later
- Download-Seite: `https://github.com/Josi-create/fraktur-korrektor/releases/latest`
- Code signing policy: `https://github.com/Josi-create/fraktur-korrektor/blob/main/docs/en/code-signing.md`
- Autor, Prüfer und Freigabe: Johannes Wack

Die Prüfung kann dauern; bis dahin läuft alles unsigniert weiter wie bisher.

### 3. In SignPath einrichten (nach der Zusage)

Auf <https://app.signpath.io>:

- Zwei-Faktor-Anmeldung für das SignPath-Konto einschalten.
- Unter *Trusted Build Systems* „GitHub.com“ mit dem Projekt verknüpfen (und die GitHub-App von SignPath für das
  Repository installieren, wenn SignPath darum bittet).
- *Artifact Configuration*: den Inhalt von
  [packaging/windows/signpath-artifact-configuration.xml](packaging/windows/signpath-artifact-configuration.xml)
  übernehmen und als Standard setzen.
- *Signing Policies*: Der Workflow erwartet `release-signing` (echtes Zertifikat, Freigabe von Hand) und
  `test-signing` (Testzertifikat, ohne Freigabe). Heißen sie anders, die Zeile `SIGNPATH_POLICY` im Job `windows`
  von `release.yml` anpassen.
- Einen API-Token für einen Benutzer anlegen, der bei beiden Richtlinien einreichen darf (*Submitter*); er wird nur
  einmal angezeigt. Dazu die *Organization ID* und den *Project Slug* notieren.

### 4. Variablen und Secret hinterlegen

Die Variablen zuerst – das Secret schaltet die Signatur ein:

    gh variable set SIGNPATH_ORGANIZATION_ID --repo Josi-create/fraktur-korrektor --body "<Organization ID>"
    gh variable set SIGNPATH_PROJECT_SLUG    --repo Josi-create/fraktur-korrektor --body "<Project Slug>"
    gh secret set SIGNPATH_API_TOKEN         --repo Josi-create/fraktur-korrektor   # fragt nach dem Token

Der Token gehört wie die Apple-Werte **nie** in eine Datei des Repositorys.

### 5. Probelauf

    gh workflow run release.yml

Ohne Tag signiert der Lauf mit dem Testzertifikat, ohne Freigabe. Im Job `windows` müssen *Signiertes Programm
übernehmen und prüfen* und *Signierten Installer übernehmen und prüfen* grün sein; dass Windows dem Testzertifikat
nicht traut, ist hier richtig so.

### 6. Die erste signierte Version

Wie gewohnt mit `python scripts/release.py …` (siehe unten). Der Job `windows` wartet dann **zweimal** auf eine
Freigabe; SignPath meldet jede Anfrage per E-Mail, freigegeben wird auf app.signpath.io. Vorher im Actions-Lauf
nachsehen, dass nichts rot ist. Jede Anfrage wartet höchstens 60 Minuten; danach bricht der Lauf ab, und es erscheint
kein Release. Dann den Job neu starten – lehnt SignPath die Wiederholung ab, eine neue Patch-Version veröffentlichen.

Danach unter Windows 11 prüfen: Setup herunterladen, *Eigenschaften → Digitale Signaturen* zeigt „SignPath
Foundation“; installieren, starten, deinstallieren.

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

Unter Windows macht `build.bat` dasselbe (Installer nur, wenn Inno Setup 6 installiert ist). Lokal gebaut bleibt
der Windows-Build unsigniert – signiert wird nur in GitHub Actions, siehe
[Windows-Signatur einrichten](#einmalig-windows-signatur-einrichten-signpath-foundation); SmartScreen warnt darum
beim ersten Start, siehe [docs/de/install.md](docs/de/install.md).

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

Voraussetzung: Unter `## [Unveröffentlicht]` im [CHANGELOG](CHANGELOG.md) steht, was sich geändert hat – dieser
Text wird der Text des Releases. Dann auf `main`, ohne offene Änderungen:

    python scripts/release.py 0.12.0

Das Skript setzt die Versionsnummer in `pyproject.toml` und `CITATION.cff`, macht aus dem unveröffentlichten
Abschnitt `## [0.12.0] – <heute>`, legt Commit und Tag `v0.12.0` an und schiebt beides nach Rückfrage hoch
(`--ja`: ohne Rückfrage). Alles Weitere geschieht von selbst, in rund 15 Minuten:

1. **pruefen**: Passen Tag, `pyproject.toml` und CHANGELOG zusammen? Sonst bricht der Lauf ab, bevor gebaut wird.
   Die Zusammenfassung des Laufs zeigt den künftigen Release-Text.
2. **tests** (dieselben wie bei jedem Push) und die Builds für Windows, Mac und Linux samt Rauchtest laufen
   nebeneinander. Ist die Windows-Signatur eingerichtet, wartet der Windows-Build zweimal auf die Freigabe bei
   SignPath (E-Mail).
3. **release**: Sind alle grün, erscheint das Release – nicht als Entwurf, sondern gleich veröffentlicht – mit einer
   Download-Tabelle und dem CHANGELOG-Abschnitt. Danach prüft der Auftrag, dass jeder Dauerlink unten auf die neue
   Version zeigt und sich herunterladen lässt.

Schlägt ein Schritt fehl, erscheint kein Release. Den Fehler auf `main` beheben, dann den Tag neu setzen:

    git push origin :refs/tags/v0.12.0 && git tag -d v0.12.0
    git tag -a v0.12.0 -m "Version 0.12.0" && git push origin v0.12.0

Ein Tag mit Bindestrich (`v1.0.0-rc1`) wird eine **Vorabversion**: Sie steht auf der Releases-Seite, die
Dauerlinks zeigen aber weiter auf die letzte richtige Version.

Die Dateinamen bleiben von Version zu Version gleich, darum funktionieren diese Dauerlinks – ganz oben im README
und in der Hilfe:

    https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor_Setup.exe
    https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-arm64.dmg
    https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-macos-x86_64.dmg
    https://github.com/Josi-create/fraktur-korrektor/releases/latest/download/Fraktur-Korrektor-linux-x86_64.AppImage

Wer einen Namen ändert, ändert ihn auch in `scripts/release.py` (`DOWNLOADS`) und im Schritt *Dauerlinks prüfen*;
`tests/test_release.py` passt auf, dass README, Hilfe und Workflow übereinstimmen. Das portable ZIP und das
Linux-tar.gz tragen die Versionsnummer im Namen und sind darum nur über die Releases-Seite erreichbar.
