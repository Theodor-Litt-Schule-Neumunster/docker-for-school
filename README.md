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
ssh-keygen -t rsa -b 4096 -f $env:USERPROFILE\.ssh\id_rsa

# Public Key auf Server kopieren
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh dataserver@100.66.170.64 "cat >> ~/.ssh/authorized_keys"
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
