---
description: Windows Installer bauen (Inno Setup)
---

## Voraussetzungen

- Docker Desktop (muss der Nutzer selbst installieren)
- Inno Setup (ISCC.exe) auf dem Build-PC

## Inhalt

- `DockerLab.iss` erstellt den Installer
- `start-DockerLab.ps1` startet alle Services und öffnet den Browser

## Build

1. Inno Setup installieren
2. In diesem Ordner ausführen:

```powershell
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" .\DockerLab.iss
```

## Ergebnis

- `DockerLab-Setup.exe` erscheint in `installer-windows/`

## Nutzung (Schüler)

1. Docker Desktop installieren
2. `DockerLab-Setup.exe` installieren
3. Desktop-Icon oder Startmenü: **DockerLab**
