<<<<<<< HEAD
# Theodor Litt - Schüler Login-System

Webbasiertes Login-System für Schüler mit VM-Verwaltung und Remote-Datenspeicherung.

## 🚀 Quick Start

### 1. Voraussetzungen prüfen

- ✅ Docker Desktop läuft
- ✅ SSH-Key existiert (`%USERPROFILE%\.ssh\id_rsa` oder `id_ed25519`)
- ✅ Zugriff auf Server (100.66.170.64)

### 2. Konfiguration erstellen

```powershell
# .env Datei aus Vorlage erstellen
copy .env.example .env

# .env bearbeiten (SSH-Server anpassen)
notepad .env
```

### 3. Container starten

```powershell
# Automatischer Start mit Diagnose
.\start.ps1 start

# ODER manuell:
docker-compose up --build -d
```

### 4. Zugriff

- **Homepage:** http://localhost:3000
- **Admin-Login:** Credentials von Server (`/srv/schuler-daten/admin_credentials.yml`)

---

## 📋 Verfügbare Befehle

```powershell
.\start.ps1 start      # Container starten
.\start.ps1 stop       # Container stoppen
.\start.ps1 restart    # Container neu starten
.\start.ps1 logs       # Live-Logs anzeigen
.\start.ps1 status     # Status anzeigen
.\start.ps1 fix        # Probleme beheben
.\start.ps1 clean      # Alles zurücksetzen
```

---

## 💾 Datenspeicherung

### WICHTIG: Alle Daten werden auf dem Server gespeichert!

**Lokaler Computer:**
- Nur Docker-Container und Konfiguration
- Keine Schüler-Daten oder VMs

**Remote-Server (100.66.170.64):**
- `/srv/schuler-daten/` - Alle Schüler-Daten und VMs

---

## 🧰 Fehlerbehebung

### Container starten nicht

```powershell
# Automatische Reparatur
.\start.ps1 fix

# Logs prüfen
.\start.ps1 logs
```

### SSH-Verbindung fehlschlägt

```powershell
# SSH-Key testen
ssh dataserver@100.66.170.64 "echo OK"

# SSH-Key neu generieren
=======
# Theodor Litt - SSH-basiertes Login-System
## Setup-Anleitung

### 1. Voraussetzungen

- Docker & Docker Compose installiert
- SSH-Zugriff auf den Remote-Server (192.168.178.1)
- SSH-Key-Authentifizierung eingerichtet

### 2. Server-seitige Einrichtung

Auf dem **SSH-Server** (192.168.178.1):

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
    email: "admin@dockerlab.de"
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
SSH_REMOTE_HOST=192.168.178.1
SSH_REMOTE_USER=dataserver
SSH_REMOTE_PATH=/srv/schuler-daten
SECRET_KEY=IhrGeheimesSecretKeyHier
```

**Option B:** Mit Standard-Werten (bereits in docker-compose.yml)

### 4. SSH-Key-Setup (falls noch nicht vorhanden)

```powershell
# SSH-Key generieren (falls nicht vorhanden)
>>>>>>> 919387af8e60d736714c6b8f6bc4516becd1493a
ssh-keygen -t rsa -b 4096 -f $env:USERPROFILE\.ssh\id_rsa

# Public Key auf Server kopieren
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh dataserver@100.66.170.64 "cat >> ~/.ssh/authorized_keys"
<<<<<<< HEAD
```

---

## 📁 Projekt-Struktur

```
d:\Neuer Ordner\
├── docker-compose.yml           # Container-Konfiguration
├── start.ps1                    # Management-Script
├── .env                         # Ihre Konfiguration (NICHT committen!)
├── .env.example                 # Beispiel-Konfiguration
├── SETUP.md                     # Ausführliche Anleitung
├── README.md                    # Diese Datei
└── homepage-data/
    ├── app.py                   # Flask-Anwendung
    ├── Dockerfile.homepage      # Docker-Image
    ├── requirements.txt         # Python-Dependencies
    └── templates/               # HTML-Templates
```

---

## 🔒 Sicherheit

- ✅ Alle Daten nur auf dem Server
- ✅ SSH-Key-Authentifizierung
- ✅ Admin-Passwörter nur auf Server
- ❌ Keine lokale Datenspeicherung
- ❌ Keine Passwörter in Git

---

## 📚 Dokumentation

- **Setup-Anleitung:** [SETUP.md](SETUP.md)
- **Server-Konfiguration:** Siehe SETUP.md Abschnitt 2

---

## ⚙️ Konfiguration

Bearbeiten Sie `.env` für:

```env
# Server-Adresse
SSH_REMOTE_HOST=100.66.170.64
```

---

## 🆘 Support

Bei Problemen:

1. Prüfen Sie die Logs: `.\start.ps1 logs`
2. Status prüfen: `.\start.ps1 status`
3. Automatische Reparatur: `.\start.ps1 fix`
4. Siehe [SETUP.md](SETUP.md) für Details

---

**Version:** 2.0 (Server-basiert)  
**Datum:** März 2026
=======

# Test SSH-Verbindung
ssh dataserver@100.66.170.64 "ls -la /srv/schuler-daten"
```

### 5. Docker-Container starten (Lokal)

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

**Auf dem SSH-Server (192.168.178.1):**
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
- Prüfen Sie die Datei auf dem Server: `ssh dataserver@192.168.178.1 "cat /srv/schuler-daten/admin_credentials.yml"`
- Prüfen Sie YAML-Syntax (keine Tabs, korrekte Einrückung)

**Users werden nicht gespeichert:**
- Prüfen Sie Schreibrechte: `ssh dataserver@192.168.178.1 "ls -la /srv/schuler-daten"`
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

### Support

Bei Problemen prüfen Sie:
1. Docker-Logs: `docker-compose logs -f`
2. SSH-Verbindung: `ssh dataserver@192.168.178.1`
3. Server-Dateien: `ssh dataserver@192.168.178.1 "ls -la /srv/schuler-daten"`
>>>>>>> 919387af8e60d736714c6b8f6bc4516becd1493a
