$ErrorActionPreference = 'Stop'

function Test-DockerCli {
    try {
        & docker version | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Start-DockerDesktopIfPossible {
    $candidates = @(
        "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe",
        "$env:ProgramFiles(x86)\Docker\Docker\Docker Desktop.exe"
    )

    foreach ($p in $candidates) {
        if (Test-Path $p) {
            try {
                Start-Process -FilePath $p | Out-Null
                return $true
            } catch {
            }
        }
    }

    return $false
}

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectDir

if (-not (Test-DockerCli)) {
    Start-DockerDesktopIfPossible | Out-Null
    Write-Host "Docker ist nicht bereit. Bitte Docker Desktop starten und dann erneut versuchen." -ForegroundColor Yellow
    exit 1
}

try {
    & docker compose version | Out-Null
    & docker compose up -d | Out-Null
} catch {
    try {
        & docker-compose version | Out-Null
        & docker-compose up -d | Out-Null
    } catch {
        Write-Host "Docker Compose wurde nicht gefunden. Bitte Docker Desktop installieren." -ForegroundColor Red
        exit 1
    }
}

Start-Sleep -Seconds 2
Start-Process "http://localhost:3000" | Out-Null
