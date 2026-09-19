; ============================================================
; Fraktur-Korrektor - Installer fuer Windows (Inno Setup 6)
;
; Kompilieren (die Version kommt aus pyproject.toml):
;   venv\Scripts\python.exe scripts\build_installer.py
; oder direkt:
;   ISCC.exe /DMyAppVersion=0.11.0 installer.iss
;
; Voraussetzung: PyInstaller lief schon, dist\Fraktur-Korrektor\ existiert
; (build.bat erledigt beides).
;
; Installiert wird ohne Administratorrechte in den Benutzerordner - so
; bekommt die Zielgruppe keine Rueckfrage der Benutzerkontensteuerung.
; ============================================================

#define MyAppName "Fraktur-Korrektor"
#ifndef MyAppVersion
  #error MyAppVersion fehlt - bitte /DMyAppVersion=x.y.z uebergeben oder scripts/build_installer.py verwenden
#endif
#define MyAppPublisher "Johannes Wack"
#define MyAppUrl "https://github.com/Josi-create/fraktur-korrektor"
#define MyAppExeName "Fraktur-Korrektor.exe"

[Setup]
AppId={{B4E9C6A2-7D31-4F58-9C0E-2A6B8D1F3E47}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppUrl}
AppSupportURL={#MyAppUrl}/issues
DefaultDirName={autopf}\Fraktur-Korrektor
DefaultGroupName=Fraktur-Korrektor
DisableProgramGroupPage=yes
OutputDir=dist\installer
; Fester Dateiname ohne Version, damit der Link
; releases/latest/download/Fraktur-Korrektor_Setup.exe immer auf die neueste
; Fassung zeigt. Die Version steht in den Datei-Eigenschaften.
OutputBaseFilename=Fraktur-Korrektor_Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupIconFile=icon.ico
LicenseFile=LICENSE

[InstallDelete]
; Beim Drueberinstallieren die Dateien der Vorversion entfernen, damit keine
; veralteten Module zurueckbleiben. Die Arbeit des Nutzers liegt in
; %USERPROFILE%\Fraktur-Korrektor bzw. .fraktur-korrektor und bleibt unberuehrt.
Type: filesandordirs; Name: "{app}\_internal"

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\Fraktur-Korrektor\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Lizenztext (GPL-3.0-or-later) gut sichtbar neben dem Programm
Source: "LICENSE"; DestDir: "{app}"; DestName: "LICENSE.txt"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
