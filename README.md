# DockerLab - Container Management System

Einfaches Web-Interface zur Verwaltung von Docker-Containern mit lokaler Speicherung und optionaler Nextcloud-Synchronisation.

## Features

✅ **Container-Verwaltung**
- Container anzeigen, starten, stoppen, neu starten
- Neue Container erstellen
- Container löschen
- Ports und Umgebungsvariablen konfigurieren

✅ **Lokale Speicherung**
- Alle Daten werden im `data/` Ordner gespeichert
- Aktivitätsprotokoll für alle Container-Aktionen
- Persistente Speicherung zwischen Neustarts

✅ **Nextcloud-Synchronisation** (optional)
- Manuelles Hochladen zu Nextcloud per Knopfdruck
- Daten von Nextcloud herunterladen
- Vollständig optional - funktioniert auch ohne Nextcloud

## Installation & Start

### 1. Voraussetzungen
- Docker & Docker Compose installiert
- (Optional) Nextcloud-Account für Sync-Funktion

### 2. Konfiguration

Kopieren Sie `.env.example` zu `.env` und passen Sie die Werte an:

```bash
cp .env.example .env
```

**Ohne Nextcloud:**
```env
SECRET_KEY=ihr-geheimer-schluessel
NEXTCLOUD_URL=
NEXTCLOUD_USERNAME=
NEXTCLOUD_PASSWORD=
```

**Mit Nextcloud:**
```env
SECRET_KEY=ihr-geheimer-schluessel
NEXTCLOUD_URL=https://ihre-nextcloud.de
NEXTCLOUD_USERNAME=ihr-username
NEXTCLOUD_PASSWORD=ihr-app-passwort
NEXTCLOUD_PATH=/DockerLab
```

### 3. Starten

```bash
docker-compose up -d
```

### 4. Zugriff

Öffnen Sie im Browser: `http://localhost:3000`

## Verwendung

### Container erstellen
1. Klicken Sie auf "**+ Neuer Container**"
2. Geben Sie Name und Image ein (z.B. `nginx:latest`)
3. Optional: Ports konfigurieren (z.B. `8080:80`)
4. Optional: Umgebungsvariablen (z.B. `DB_HOST=localhost`)
5. Klicken Sie auf "**Container erstellen**"

### Container verwalten
- **▶ Start**: Container starten
- **⏸ Stop**: Container stoppen
- **🔄 Restart**: Container neu starten
- **🗑 Delete**: Container löschen (inkl. Bestätigung)

### Nextcloud-Synchronisation
Wenn Nextcloud konfiguriert ist:

- **↑ Zu Nextcloud hochladen**: Lädt lokale Container-Daten zu Nextcloud hoch
- **↓ Von Nextcloud laden**: Lädt gespeicherte Daten von Nextcloud herunter

## Verzeichnisstruktur

```
DockerLab/
├── data/                      # Lokale Datenspeicherung
│   └── containers.json       # Container-Aktionen und Metadaten
├── homepage-data/            # Anwendungscode
│   ├── app.py               # Flask-Anwendung
│   ├── templates/
│   │   └── main.html       # Web-Interface
│   ├── Dockerfile.homepage
│   └── requirements.txt
├── docker-compose.yml        # Docker-Konfiguration
└── .env                     # Ihre Konfiguration (nicht in Git!)
```

## Beispiele

### Nginx Webserver erstellen
- **Name**: `my-nginx`
- **Image**: `nginx:latest`
- **Ports**: `8080:80`

### PostgreSQL Datenbank erstellen
- **Name**: `my-postgres`
- **Image**: `postgres:15`
- **Ports**: `5432:5432`
- **Environment**: `POSTGRES_PASSWORD=geheim, POSTGRES_USER=admin`

### Redis Cache erstellen
- **Name**: `my-redis`
- **Image**: `redis:alpine`
- **Ports**: `6379:6379`

## Sicherheitshinweise

⚠️ **Wichtig:**
- Ändern Sie `SECRET_KEY` in `.env` für Produktion
- Verwenden Sie Nextcloud **App-Passwörter** statt Haupt-Passwort
- Fügen Sie `.env` zur `.gitignore` hinzu (nicht ins Repository!)
- DockerLab benötigt Zugriff auf Docker-Socket - verwenden Sie es nur in vertrauenswürdigen Umgebungen

## Nextcloud einrichten

1. In Nextcloud einloggen
2. **Einstellungen** → **Sicherheit** → **App-Passwörter**
3. Neues App-Passwort erstellen (z.B. "DockerLab")
4. Passwort in `.env` eintragen

## Troubleshooting

### Container wird nicht angezeigt
- Prüfen Sie, ob Docker läuft: `docker ps`
- Überprüfen Sie die Logs: `docker-compose logs homepage`

### Nextcloud-Sync funktioniert nicht
- Prüfen Sie die Zugangsdaten in `.env`
- Verwenden Sie die vollständige URL mit `https://`
- Verwenden Sie ein App-Passwort, nicht Ihr Haupt-Passwort

### Port bereits belegt
- Ändern Sie den Port in `docker-compose.yml` (z.B. `3001:3000`)
- Oder stoppen Sie den anderen Container auf Port 3000

## Deinstallation

```bash
# Container stoppen und entfernen
docker-compose down

# Inkl. Daten löschen
rm -rf data/
```

## Technische Details

- **Backend**: Python Flask
- **Frontend**: HTML/CSS/JavaScript (Vanilla)
- **Docker-SDK**: Python Docker-Bibliothek
- **WebDAV**: Nextcloud-Synchronisation über WebDAV-Protokoll
- **Speicherformat**: JSON

## Lizenz

Dieses Projekt ist für persönliche und Bildungszwecke.
