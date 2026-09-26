<#
Prueft eine exe des Windows-Builds vor und nach der Code-Signatur (release.yml, Job windows):
  - Produktname und -version in den Datei-Eigenschaften. Die Artifact Configuration fuer SignPath signiert das
    Programm nur mit diesem Produktnamen - lieber hier scheitern als erst dort. Inno Setup fuellt die Texte der
    Setup.exe mit Leerzeichen auf feste Breite auf; verglichen wird darum ohne sie, gezeigt in [Klammern].
  - mit -Richtlinie ausserdem die Authenticode-Signatur: vorhanden, bei release-signing auch gueltig. Die
    Testsignatur (test-signing) hat ein Zertifikat, dem Windows nicht vertraut.

    scripts\check_exe.ps1 dist\Fraktur-Korrektor\Fraktur-Korrektor.exe
    scripts\check_exe.ps1 dist\installer\Fraktur-Korrektor_Setup.exe -Richtlinie release-signing

Nur ASCII in dieser Datei: Windows PowerShell 5 liest sie sonst mit der falschen Kodierung.
#>
param(
    [Parameter(Mandatory = $true)] [string] $Datei,
    [string] $Richtlinie = ''
)
$ErrorActionPreference = 'Stop'

$version = (Select-String -Path (Join-Path $PSScriptRoot '..\pyproject.toml') -Pattern '^version\s*=\s*"([^"]+)"').Matches[0].Groups[1].Value
$info = (Get-Item $Datei).VersionInfo
$name = "$($info.ProductName)".Trim()
$produktversion = "$($info.ProductVersion)".Trim()
Write-Host "$Datei"
Write-Host "  Produkt:  [$($info.ProductName)] [$($info.ProductVersion)], Datei-Version [$($info.FileVersion)]"
if ($name -ne 'Fraktur-Korrektor') { throw "Produktname '$name' statt 'Fraktur-Korrektor'" }
if ($produktversion -ne $version) { throw "Produktversion '$produktversion' statt '$version' (pyproject.toml)" }

if ($Richtlinie) {
    $sig = Get-AuthenticodeSignature $Datei
    if (-not $sig.SignerCertificate) { throw "$Datei ist nicht signiert" }
    Write-Host "  Signatur: $($sig.Status), $($sig.SignerCertificate.Subject)"
    if ($Richtlinie -eq 'release-signing' -and $sig.Status -ne 'Valid') { throw "Signatur ungueltig: $($sig.StatusMessage)" }
}
