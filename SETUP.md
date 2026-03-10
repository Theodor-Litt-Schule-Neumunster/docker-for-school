# Theodor Litt - SSH-basiertes Login-System
## Setup-Anleitung

### 1. Voraussetzungen

- Docker & Docker Compose installiert
- SSH-Zugriff auf den Remote-Server (100.66.170.64)
- SSH-Key-Authentifizierung eingerichtet

### 2. Server-seitige Einrichtung

Auf dem **SSH-Server** (100.66.170.64):

```bash
# 1. Verzeichnis erstellen
sudo mkdir -p /srv/schuler-daten
sudo chown dataserver:dataserver /srv/schuler-daten

# 2. Admin-Credentials-Datei erstellen
nano /srv/schuler-daten/admin_credentials.yml
```

Inhalt der `admin_credentials.yml`:

```yaml
admins:
  - username: "admin"
    password: "IhrSicheresAdminPasswort123!"
    email: "admin@theodor-litt.de"
    description: "Haupt-Administrator"
```

**WICHTIG:** Datei absichern!
```bash
chmod 600 /srv/schuler-daten/admin_credentials.yml
```

### 3. Lokale Einrichtung (Windows)

**Option A:** `.env` Datei erstellen (empfohlen)

```bash
# Im Projektverzeichnis
notepad .env
```

Inhalt der `.env`:
```env
SSH_REMOTE_HOST=100.66.170.64
SSH_REMOTE_USER=dataserver
SSH_REMOTE_PATH=/srv/schuler-daten
SECRET_KEY=IhrGeheimesSecretKeyHier
```

**Option B:** Mit Standard-Werten (bereits in docker-compose.yml)

### 4. SSH-Key-Setup (falls noch nicht vorhanden)

```powershell
# SSH-Key generieren (falls nicht vorhanden)
ssh-keygen -t rsa -b 4096 -f $env:USERPROFILE\.ssh\id_rsa

# Public Key auf Server kopieren
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh dataserver@100.66.170.64 "cat >> ~/.ssh/authorized_keys"

# Test SSH-Verbindung
ssh dataserver@100.66.170.64 "ls -la /srv/schuler-daten"
```

### 5. Docker-Container starten

```powershell
# Container bauen und starten
docker-compose up --build -d

# Logs anzeigen
docker-compose logs -f

# Status prüfen
docker-compose ps
```

### 6. Zugriff auf die Webseite

- URL: http://localhost:3000
- Registrierung: Nur mit Admin-Credentials möglich
- Login: Nach erfolgreicher Registrierung

### 7. Ordnerstruktur

**Lokal (auf Ihrem Computer):**
```
d:\Neuer Ordner\
├── docker-compose.yml
├── admin_credentials.yml.example  (NUR Beispiel, nicht verwendet)
├── SETUP.md
└── homepage-data/
    ├── app_new_ssh.py            (wird zu app.py im Container)
    ├── Dockerfile.homepage
    ├── requirements.txt
    └── templates/
        ├── base_new.html
        ├── login_new.html
        ├── register_new.html
        └── user_dashboard_new.html
```

**Auf dem SSH-Server (100.66.170.64):**
```
/srv/schuler-daten/
├── admin_credentials.yml    (Admin-Zugangsdaten)
└── users.json              (Wird automatisch erstellt)
```

### 8. Passwort-Hash generieren (für sichere Admin-Credentials)

Für maximale Sicherheit sollten Sie Passwort-Hashes verwenden:

```python
python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash(input('Passwort: ')))"
```

Dann in `admin_credentials.yml`:
```yaml
admins:
  - username: "admin"
    password_hash: "scrypt:32768:8:1$abc123..."  # Ihr generierter Hash
```

### 9. Troubleshooting

**Container startet nicht:**
```powershell
docker-compose logs homepage
```

**SSH-Verbindung fehlgeschlagen:**
```powershell
# Teste SSH manuell
ssh dataserver@100.66.170.64

# Prüfe SSH-Key
dir $env:USERPROFILE\.ssh\id_rsa
```

**Admin-Credentials funktionieren nicht:**
- Prüfen Sie die Datei auf dem Server: `ssh dataserver@100.66.170.64 "cat /srv/schuler-daten/admin_credentials.yml"`
- Prüfen Sie YAML-Syntax (keine Tabs, korrekte Einrückung)

**Users werden nicht gespeichert:**
- Prüfen Sie Schreibrechte: `ssh dataserver@100.66.170.64 "ls -la /srv/schuler-daten"`
- Sollte: `drwxr-xr-x dataserver dataserver`

### 10. Sicherheitshinweise

✅ **Empfohlen:**
- Verwenden Sie SSH-Key-Authentifizierung (keine Passwörter)
- Verwenden Sie Passwort-Hashes in admin_credentials.yml
- Setzen Sie `chmod 600` auf sensible Dateien auf dem Server
- Ändern Sie SECRET_KEY in .env

❌ **Vermeiden:**
- Klartext-Passwörter in admin_credentials.yml (nur für Tests)
- Admin-Credentials in Git einchecken
- Default-SECRET_KEY in Produktion

### 11. Wichtige Änderungen gegenüber vorher

**ENTFERNT:**
- ❌ Lokaler `./Daten` Ordner
- ❌ Docker-Socket Volume
- ❌ VM/Container-Management
- ❌ Backup-System
- ❌ MariaDB-Datenbank

**NEU:**
- ✅ Alles wird per SSH auf Server gespeichert
- ✅ Admin-geschützte Registrierung
- ✅ Einfaches Login-System
- ✅ Keine lokalen Daten mehr

### 12. Datei-Umbenennungen (noch durchzuführen)

Nach erfolgreicher Implementierung müssen Sie noch die neuen Dateien aktivieren:

```powershell
# Im Verzeichnis: d:\Neuer Ordner\homepage-data\

# Templates
mv templates\base_new.html templates\base.html -Force
mv templates\login_new.html templates\login.html -Force
mv templates\register_new.html templates\register.html -Force
mv templates\user_dashboard_new.html templates\user_dashboard.html -Force

# App (wird bereits im Dockerfile gemacht)
# app_new_ssh.py -> wird zu app.py kopiert
```

### Support

Bei Problemen prüfen Sie:
1. Docker-Logs: `docker-compose logs -f`
2. SSH-Verbindung: `ssh dataserver@100.66.170.64`
3. Server-Dateien: `ssh dataserver@100.66.170.64 "ls -la /srv/schuler-daten"`
