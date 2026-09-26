# Code signing and privacy

This page explains who signs the Windows version of Fraktur-Korrektor, which rules apply, and what the program
sends over the network. It is also the code signing policy that SignPath Foundation requires for its free signing.

## What the signature means

A digital signature is a seal on the program file: Windows can tell from it who the file comes from and that nobody
has changed it since it was signed. The Windows version is signed by **SignPath Foundation**, a non-profit that
signs open-source programs free of charge. That is why Windows names “SignPath Foundation” as the publisher in its
messages and in the file properties – this is as it should be.

> Free code signing provided by [SignPath.io](https://signpath.io), certificate by
> [SignPath Foundation](https://signpath.org).

Windows itself shows whether a downloaded file is signed: right-click the file → *Properties* → *Digital
Signatures* tab. The Mac version is signed with its own certificate from Apple and notarised; the Linux version is
not signed.

## Signing rules

- **What is signed:** only the two files built from this project’s source code – the program
  `Fraktur-Korrektor.exe` and the installer `Fraktur-Korrektor_Setup.exe`. Components that come from other
  open-source projects (Python, Tesseract, PyMuPDF and further libraries) are shipped as their publishers provide
  them.
- **How it is built:** only by GitHub Actions from the public
  [source code](https://github.com/Josi-create/fraktur-korrektor), from a version tag. The process is described
  in [release.yml](https://github.com/Josi-create/fraktur-korrektor/blob/main/.github/workflows/release.yml).
  Files built on a personal computer are not signed.
- **Approval:** every signing of a release is approved manually.
- **Sign-in:** everyone involved uses multi-factor authentication for GitHub and SignPath.

| Role | Task | Who |
|---|---|---|
| Committers | may change the source code without further review | [Johannes Wack](https://github.com/Josi-create) |
| Reviewers | review every contribution from outside (pull request) before it is merged | [Johannes Wack](https://github.com/Josi-create) |
| Approvers | decide whether a release is signed | [Johannes Wack](https://github.com/Josi-create) |

## Privacy

This program will not transfer any information to other networked systems unless specifically requested by the
user or the person installing or operating it. It runs on your computer; books, texts, corrections and settings stay
there. There are no usage statistics, no update checks and no online spell checking. Other devices on your home
network can only reach it if you switch this on yourself (for example for [reading on a tablet](usage.md)).

One exception: on Linux and when run from source, the program downloads the Fraktur model for Tesseract from the
Mannheim University Library the first time you use text recognition. Only this model file is fetched; nothing about
you or your books is transmitted. The Windows and Mac versions already include the model.

Links you click – to the online help, to GitHub, to the donation page – are opened by your browser like any other
page. More on security: [SECURITY.en.md](https://github.com/Josi-create/fraktur-korrektor/blob/main/SECURITY.en.md).
