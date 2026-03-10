# Migration Script - Alte Dateien sichern und neue aktivieren
# Theodor Litt Login-System

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Theodor Litt - Migration zu SSH-basiertem System" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""

# Arbeitsverzeichnis
$projectRoot = "d:\Neuer Ordner"
$homepageData = Join-Path $projectRoot "homepage-data"
$backupDir = Join-Path $projectRoot "_backup_old_files"
$backupTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = Join-Path $backupDir $backupTimestamp

# Erstelle Backup-Verzeichnis
Write-Host "[1/4] Erstelle Backup-Verzeichnis..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $backupPath | Out-Null
Write-Host "      -> Backup-Pfad: $backupPath" -ForegroundColor Gray

# Sichere alte Dateien
Write-Host ""
Write-Host "[2/4] Sichere alte Dateien..." -ForegroundColor Cyan

$filesToBackup = @(
    "homepage-data\app.py",
    "homepage-data\templates\base.html",
    "homepage-data\templates\login.html",
    "homepage-data\templates\register.html",
    "homepage-data\templates\user_dashboard.html",
    "init-db.sql",
    "migrate_users.py"
)

foreach ($file in $filesToBackup) {
    $sourcePath = Join-Path $projectRoot $file
    if (Test-Path $sourcePath) {
        $destPath = Join-Path $backupPath $file
        $destDir = Split-Path $destPath -Parent
        New-Item -ItemType Directory -Force -Path $destDir | Out-Null
        Copy-Item $sourcePath $destPath -Force
        Write-Host "      ✓ Gesichert: $file" -ForegroundColor Green
    } else {
        Write-Host "      ⊗ Nicht gefunden: $file" -ForegroundColor Yellow
    }
}

# Aktiviere neue Dateien
Write-Host ""
Write-Host "[3/4] Aktiviere neue Dateien..." -ForegroundColor Cyan

# Templates umbenennen
$templateMigrations = @{
    "base_new.html" = "base.html"
    "login_new.html" = "login.html"
    "register_new.html" = "register.html"
    "user_dashboard_new.html" = "user_dashboard.html"
}

$templatesDir = Join-Path $homepageData "templates"
foreach ($oldName in $templateMigrations.Keys) {
    $newName = $templateMigrations[$oldName]
    $oldPath = Join-Path $templatesDir $oldName
    $newPath = Join-Path $templatesDir $newName
    
    if (Test-Path $oldPath) {
        Move-Item $oldPath $newPath -Force
        Write-Host "      ✓ Template: $oldName -> $newName" -ForegroundColor Green
    }
}

# App-Datei ist bereits im Dockerfile referenziert (app_new_ssh.py -> app.py)
Write-Host "      ✓ App: app_new_ssh.py (wird im Docker-Build zu app.py)" -ForegroundColor Green

# Alte Dateien entfernen (optional)
Write-Host ""
Write-Host "[4/4] Entferne nicht mehr benötigte Dateien..." -ForegroundColor Cyan

$filesToRemove = @(
    "init-db.sql",
    "migrate_users.py"
)

foreach ($file in $filesToRemove) {
    $filePath = Join-Path $projectRoot $file
    if (Test-Path $filePath) {
        Remove-Item $filePath -Force
        Write-Host "      ✓ Entfernt: $file" -ForegroundColor Green
    }
}

# Prüfe ob Daten-Ordner existiert
$datenDir = Join-Path $projectRoot "Daten"
if (Test-Path $datenDir) {
    Write-Host ""
    Write-Host "WARNUNG: Ordner 'Daten' existiert noch!" -ForegroundColor Yellow
    Write-Host "         Dieser wird nicht mehr verwendet." -ForegroundColor Yellow
    $response = Read-Host "         Möchten Sie ihn ins Backup verschieben? (j/n)"
    if ($response -eq "j" -or $response -eq "J") {
        $datenBackup = Join-Path $backupPath "Daten"
        Move-Item $datenDir $datenBackup -Force
        Write-Host "      ✓ 'Daten' Ordner ins Backup verschoben" -ForegroundColor Green
    }
}

# Zusammenfassung
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host "Migration abgeschlossen!" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 59) -ForegroundColor Cyan
Write-Host ""
Write-Host "Nächste Schritte:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Server-Setup:" -ForegroundColor White
Write-Host "   ssh dataserver@100.66.170.64" -ForegroundColor Gray
Write-Host "   mkdir -p /srv/schuler-daten" -ForegroundColor Gray
Write-Host "   nano /srv/schuler-daten/admin_credentials.yml" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Beispiel admin_credentials.yml:" -ForegroundColor White
Write-Host "   Siehe: admin_credentials.yml.example" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Docker-Container neu bauen:" -ForegroundColor White
Write-Host "   docker-compose down" -ForegroundColor Gray
Write-Host "   docker-compose up --build -d" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Webseite öffnen:" -ForegroundColor White
Write-Host "   http://localhost:3000" -ForegroundColor Gray
Write-Host ""
Write-Host "Backup gespeichert in:" -ForegroundColor Cyan
Write-Host "   $backupPath" -ForegroundColor Gray
Write-Host ""
Write-Host "Vollständige Anleitung in:" -ForegroundColor Cyan
Write-Host "   SETUP.md" -ForegroundColor Gray
Write-Host ""
