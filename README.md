# DockerLab – Die komplette Anleitung (für Einsteiger erklärt)

> **Für wen ist diese Anleitung?**  
> Diese Anleitung richtet sich an alle, die noch keine oder wenig Erfahrung mit Docker haben. Jeder Begriff wird erklärt, jeder Schritt wird begründet. Wer schon Docker-Erfahrung hat, kann einfach in die gewünschten Kapitel springen.

---

## Inhaltsverzeichnis

1. [Was ist Docker überhaupt?](#1-was-ist-docker-überhaupt)
2. [Was ist DockerLab und wozu brauche ich es?](#2-was-ist-dockerlab-und-wozu-brauche-ich-es)
3. [Wie ist das Projekt aufgebaut?](#3-wie-ist-das-projekt-aufgebaut)
4. [Voraussetzungen – Was muss vorher installiert sein?](#4-voraussetzungen--was-muss-vorher-installiert-sein)
5. [Schritt-für-Schritt-Installation](#5-schritt-für-schritt-installation)
6. [Die Oberfläche verstehen](#6-die-oberfläche-verstehen)
7. [Container erstellen – Schritt für Schritt](#7-container-erstellen--schritt-für-schritt)
8. [Container verwalten](#8-container-verwalten)
9. [Nextcloud-Synchronisation einrichten (optional)](#9-nextcloud-synchronisation-einrichten-optional)
10. [Praxisbeispiele](#10-praxisbeispiele)
11. [Was passiert im Hintergrund? (Technik erklärt)](#11-was-passiert-im-hintergrund-technik-erklärt)
12. [Häufige Fehler und Lösungen](#12-häufige-fehler-und-lösungen)
13. [Sicherheitshinweise](#13-sicherheitshinweise)
14. [DockerLab deinstallieren](#14-dockerlab-deinstallieren)
15. [Glossar – Fachbegriffe erklärt](#15-glossar--fachbegriffe-erklärt)

---

## 1. Was ist Docker überhaupt?

Stell dir vor, du möchtest ein Programm (z. B. einen Webserver) auf deinem Computer starten. Normalerweise musst du das Programm installieren, die richtige Version von Python/Java/Node.js einrichten, Abhängigkeiten installieren, und hoffen, dass nichts mit deinem System kollidiert.

**Docker löst genau dieses Problem.**

Docker packt ein Programm zusammen mit allem, was es braucht (Laufzeit, Bibliotheken, Konfiguration) in eine Art **Schachtel** – einen sogenannten **Container**. Diese Schachtel kannst du auf jedem Rechner starten und das Programm läuft – egal welches Betriebssystem oder welche anderen Programme schon installiert sind.

### Die wichtigsten Begriffe

| Begriff | Einfache Erklärung |
|---|---|
| **Image** | Eine Vorlage/Blaupause für einen Container. Wie eine DVD, von der du das Programm installierst. Heruntergeladen von Docker Hub. |
| **Container** | Ein laufendes Programm, das aus einem Image gestartet wurde. Wie ein Programm, das aus der DVD-Vorlage installiert wurde und jetzt läuft. |
| **Docker Hub** | Eine Art "App Store" für Docker Images. Millionen von fertigen Images sind dort gratis verfügbar (z. B. `nginx`, `postgres`, `redis`). |
| **Port** | Eine Nummer, über die ein Programm nach außen erreichbar ist. Wie eine Zimmernummer im Hotel. Port `80` = Standard-Webserver, Port `5432` = PostgreSQL-Datenbank. |
| **Volume** | Ein Ordner-Mapping zwischen Container und deinem Computer. So bleiben Daten auch nach dem Container-Neustart erhalten. |
| **Docker Compose** | Ein Werkzeug, um mehrere Container gleichzeitig zu verwalten. Alle Einstellungen stehen in einer `docker-compose.yml`-Datei. |

### Warum ist das nützlich für mich?

- **Isolierung**: Jedes Programm läuft in seiner eigenen Sandbox, ohne andere zu stören.
- **Einfacher Start**: Ein einziger Befehl startet das ganze System.
- **Kein Aufräumen**: Löscht du den Container, ist alles weg – keine Rückstände auf dem System.
- **Reproduzierbarkeit**: Das Programm läuft auf deinem PC genauso wie bei einem Kollegen.

---

## 2. Was ist DockerLab und wozu brauche ich es?

**DockerLab** ist eine Web-Oberfläche (läuft im Browser), mit der du Docker-Container bequem verwalten kannst, **ohne** Komandozeilen-Befehle tippen zu müssen.

### Was kann DockerLab?

- **Container anzeigen**: Alle laufenden und gestoppten Container werden in einer übersichtlichen Liste dargestellt.
- **Container starten/stoppen/neustarten**: Per Knopfdruck, ohne Terminal.
- **Neue Container erstellen**: Image-Name, Port und Umgebungsvariablen einfach ins Formular eingeben.
- **Container löschen**: Mit Sicherheitsabfrage, damit nichts aus Versehen gelöscht wird.
- **Logs speichern**: Beim Stoppen oder Löschen werden die letzten Logs automatisch gespeichert.
- **Nextcloud-Sync** (optional): Container-Daten lassen sich zu einer Nextcloud-Instanz synchronisieren.

### Was kann DockerLab **nicht**?

- DockerLab ist kein vollständiges Docker-Management-Tool wie Portainer. Es ist ein schlankes, persönliches Werkzeug für den Heimgebrauch.
- Es ist nicht für den produktiven Einsatz auf öffentlich zugänglichen Servern konzipiert.

---

## 3. Wie ist das Projekt aufgebaut?

Hier ist ein Überblick über alle Dateien und Ordner – mit Erklärung, wozu jede einzelne dient:

```
DockerLab/
│
├── docker-compose.yml          ← Startet DockerLab selbst
├── README.md                   ← Kurze Übersichts-README
├── README_DETAILLIERT.md       ← Diese Datei hier
│
├── data/                       ← Alle gespeicherten Daten (wird automatisch erstellt)
│   ├── containers.json         ← Liste aller bekannten Container (JSON-Format)
│   ├── containers/             ← Pro Container ein Unterordner mit seinen Daten
│   │   └── mein-container/     ← Daten-Ordner für den Container "mein-container"
│   └── logs/                   ← Log-Dateien der Container
│       └── mein-container.log  ← Letzte 5000 Log-Zeilen von "mein-container"
│
└── homepage-data/              ← Quellcode der Web-Anwendung
    ├── app.py                  ← Das Herzstück: Python-Webserver (Flask)
    ├── Dockerfile.homepage     ← Bauanleitung für den DockerLab-Container selbst
    ├── entrypoint.sh           ← Startbefehl beim Container-Start
    ├── requirements.txt        ← Python-Pakete, die benötigt werden
    ├── static/                 ← Statische Dateien (Favicon, CSS if any)
    └── templates/
        └── main.html           ← Die komplette Web-Oberfläche (HTML/CSS/JS)
```

### Jede Datei im Detail

#### `docker-compose.yml`
Das ist die **Schaltzentrale** für Docker Compose. Sie beschreibt, wie DockerLab selbst gestartet werden soll:
- Welches Dockerfile soll gebaut werden?
- Auf welchem Port ist die App erreichbar? → Port `3000`
- Was wird ins Dateisystem des Containers eingebunden?
  - `/var/run/docker.sock` → Der sogenannte Docker-Socket. Damit kann DockerLab mit dem Docker-Daemon des Hosts kommunizieren und andere Container steuern.
  - `./data` → Der lokale `data/`-Ordner wird als `/data` in den Container gemountet, damit Daten persistent gespeichert bleiben.
- Welche Umgebungsvariablen werden übergeben? (SECRET_KEY, Nextcloud-Zugangsdaten)

#### `homepage-data/app.py`
Das Backend der Anwendung, geschrieben in **Python** mit dem **Flask**-Framework. Hier passiert die eigentliche Arbeit:
- Verbindung zur Docker-API über das offizielle Python-Docker-SDK
- REST-API-Endpunkte für das Frontend (z. B. `POST /api/containers/start`)
- Nextcloud-Synchronisation via WebDAV
- Automatisches Speichern von Container-Logs

#### `homepage-data/templates/main.html`
Das **Frontend** – alles, was du im Browser siehst. Eine einzige HTML-Datei mit eingebettetem CSS und JavaScript. Kein separates Framework nötig – reines Vanilla-JS kommuniziert mit dem Python-Backend.

#### `homepage-data/Dockerfile.homepage`
Die **Bauanleitung** für den DockerLab-Container:
1. Startet von einem schlanken Python-3.9-Image
2. Installiert `docker-ce-cli` (die Docker-Befehlszeile), damit DockerLab Docker-Befehle ausführen kann
3. Installiert die Python-Abhängigkeiten aus `requirements.txt`
4. Kopiert den Anwendungscode hinein
5. Startet die App über `entrypoint.sh`

#### `homepage-data/requirements.txt`
Die Python-Pakete die DockerLab benötigt:

| Paket | Wozu? |
|---|---|
| `Flask` | Web-Framework – macht aus Python eine Webanwendung |
| `Werkzeug` | Hilfsbibliothek für Flask |
| `requests` | HTTP-Anfragen stellen – z. B. für Nextcloud WebDAV |
| `docker` | Offizielles Python-SDK für die Docker-API |

---

## 4. Voraussetzungen – Was muss vorher installiert sein?

### Docker Desktop (Windows / macOS)

Docker Desktop ist die einfachste Art, Docker unter Windows oder macOS zu nutzen.

**Windows:**
1. Gehe auf [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Lade "Docker Desktop for Windows" herunter
3. Installiere es (Standardeinstellungen sind in Ordnung)
4. Starte Docker Desktop – das Wal-Symbol erscheint in der Taskleiste
5. Warte, bis der Status "Docker Desktop is running" anzeigt

**Wichtig unter Windows:** Docker Desktop benötigt entweder WSL 2 (Windows Subsystem for Linux) oder Hyper-V. Der Installer führt dich durch die Einrichtung.

**macOS:**
1. Lade Docker Desktop für deinen Chip-Typ (Intel oder Apple Silicon) herunter
2. Ziehe die App in den Programme-Ordner
3. Starte Docker Desktop

### Überprüfen ob Docker funktioniert

Öffne ein Terminal (Windows: PowerShell oder Eingabeaufforderung, macOS: Terminal) und tippe:

```bash
docker --version
```

Du solltest etwas wie `Docker version 25.0.3, build ...` sehen. Wenn du eine Fehlermeldung bekommst, läuft Docker Desktop noch nicht.

Teste außerdem:

```bash
docker run hello-world
```

Wenn du die Meldung "Hello from Docker!" siehst, funktioniert alles korrekt.

### Docker Compose

Docker Compose ist bei Docker Desktop **bereits enthalten** – du musst nichts extra installieren.

Prüfe es trotzdem:

```bash
docker compose version
```

Du solltest `Docker Compose version v2.x.x` sehen.

---

## 5. Schritt-für-Schritt-Installation

### Schritt 1: Projekt herunterladen

Falls du das Projekt als ZIP heruntergeladen hast:
1. Entpacke die ZIP-Datei in einen Ordner deiner Wahl (z. B. `C:\DockerLab` oder `~/DockerLab`)

Falls du Git verwendest:
```bash
git clone <repository-url>
cd DockerLab
```

### Schritt 2: Umgebungsvariablen einrichten

DockerLab kann mit einer `.env`-Datei konfiguriert werden. Diese Datei enthält geheime Zugangsdaten und ist **nicht** im Repository enthalten (aus Sicherheitsgründen).

**Option A: Ohne Nextcloud (einfacher Einstieg)**

Erstelle im Projektordner eine Datei namens `.env` (der Dateiname beginnt mit einem Punkt, kein `.txt` am Ende!) mit folgendem Inhalt:

```env
SECRET_KEY=mein-geheimer-schluessel-hier-ersetzen
NEXTCLOUD_URL=
NEXTCLOUD_USERNAME=
NEXTCLOUD_PASSWORD=
NEXTCLOUD_PATH=/DockerLab
```

> **Hinweis zu SECRET_KEY:** Ersetze `mein-geheimer-schluessel-hier-ersetzen` durch eine zufällige Zeichenkette. Du kannst z. B. einen Passwort-Generator verwenden. Dieser Schlüssel wird verwendet, um Flask-Sessions zu verschlüsseln.

**Option B: Mit Nextcloud**

```env
SECRET_KEY=mein-geheimer-schluessel-hier-ersetzen
NEXTCLOUD_URL=https://deine-nextcloud.example.com
NEXTCLOUD_USERNAME=dein-benutzername
NEXTCLOUD_PASSWORD=dein-app-passwort
NEXTCLOUD_PATH=/DockerLab
```

> **Hinweis:** Verwende ein **App-Passwort**, kein normales Nextcloud-Passwort. Wie du ein App-Passwort erstellst, ist in [Kapitel 9](#9-nextcloud-synchronisation-einrichten-optional) erklärt.

### Schritt 3: DockerLab bauen und starten

Öffne ein Terminal im Projektordner und führe aus:

```bash
docker compose up -d
```

Was hier passiert (Schritt für Schritt):
1. Docker Compose liest die `docker-compose.yml`
2. Es baut ein neues Image aus `homepage-data/Dockerfile.homepage` (beim ersten Start dauert das 1–3 Minuten – Python und Docker CLI werden installiert)
3. Der Container `dockerlab-homepage` wird gestartet
4. Der Parameter `-d` bedeutet "detached" – der Container läuft im Hintergrund

Du siehst eine Ausgabe wie:
```
[+] Building 45.2s (12/12) FINISHED
[+] Running 1/1
 ✔ Container dockerlab-homepage  Started
```

### Schritt 4: Im Browser öffnen

Öffne deinen Browser und gehe zu:

```
http://localhost:3000
```

Du solltest die DockerLab-Oberfläche sehen. Falls der Browser "Connection refused" meldet, warte 10–20 Sekunden und lade die Seite neu – der Container benötigt beim ersten Start etwas Zeit.

### Schritt 5: Überprüfen ob DockerLab läuft

Im Terminal:

```bash
docker compose ps
```

Ausgabe (Status sollte "Up" oder "healthy" sein):
```
NAME                   STATUS          PORTS
dockerlab-homepage     Up (healthy)    0.0.0.0:3000->3000/tcp
```

---

## 6. Die Oberfläche verstehen

Wenn du `http://localhost:3000` im Browser öffnest, siehst du folgendes:

### Der Header (obere Leiste)

Ganz oben befindet sich die Kopfzeile mit:
- **DockerLab-Logo und Name** – links
- **Sync-Buttons** – rechts (nur sichtbar/aktiv wenn Nextcloud konfiguriert ist)
  - "↑ Zu Nextcloud" – lädt deine Container-Daten hoch
  - "↓ Von Nextcloud" – lädt Container-Daten von Nextcloud herunter

### Die Container-Karten

Jeder Docker-Container wird als eine "Karte" angezeigt. Auf jeder Karte siehst du:

| Information | Bedeutung |
|---|---|
| **Name** | Der Name des Containers (z. B. `my-nginx`) |
| **Image** | Das Image, auf dem der Container basiert (z. B. `nginx:latest`) |
| **Status-Badge** | Grün = läuft, Rot = gestoppt, Gelb = wird gestartet/gestoppt |
| **Ports** | Welche Ports sind nach außen gemappt (z. B. `0.0.0.0:8080->80/tcp`) |
| **Aktionsbuttons** | Start, Stop, Restart, Delete |

### Der "+ Neuer Container"-Button

Ein großer Button unten in der Liste öffnet ein Formular zum Erstellen eines neuen Containers.

### Status-Badges erklärt

| Badge-Farbe | Status | Bedeutung |
|---|---|---|
| 🟢 Grün | `running` | Container läuft |
| 🔴 Rot | `exited` | Container wurde gestoppt oder ist abgestürzt |
| 🟡 Gelb | `restarting` | Container startet neu |
| ⚪ Grau | `created` | Container wurde erstellt, aber noch nicht gestartet |

---

## 7. Container erstellen – Schritt für Schritt

Klicke auf den **"+ Neuer Container"**-Button. Ein Formular öffnet sich:

### Pflichtfelder

**Container Name**
- Gib dem Container einen eindeutigen, beschreibenden Namen
- Nur Kleinbuchstaben, Zahlen und Bindestriche erlaubt
- Beispiel: `mein-webserver`, `postgres-db`, `redis-cache`
- Dieser Name wird auch als Ordnername für die Daten verwendet

**Image**
- Das Docker-Image, aus dem der Container erstellt wird
- Format: `imagename:version` (z. B. `nginx:latest`, `postgres:15`, `redis:alpine`)
- Wenn du keine Version angibst, wird automatisch `:latest` verwendet
- Images werden automatisch von Docker Hub heruntergeladen, falls nicht lokal vorhanden

### Optionale Felder

**Ports**
- Verbindet einen Port deines Computers mit einem Port im Container
- Format: `HOST_PORT:CONTAINER_PORT`
- Mehrere Ports mit Komma trennen: `8080:80,443:443`
- Beispiel: `8080:80` → Du erreichst den Container unter `http://localhost:8080`

> **Warum zwei Ports?**  
> Der Container "denkt", er hört auf Port 80 (Rechte Seite). Aber von außen erreichst du ihn über Port 8080 auf deinem Computer (linke Seite). Das ist praktisch, wenn Port 80 schon belegt ist.

**Umgebungsvariablen (Environment)**
- Konfigurationswerte, die an das Programm im Container übergeben werden
- Format: `SCHLUESSEL=WERT`
- Mehrere Variablen mit Komma trennen: `DB_PASSWORD=geheim,DB_USER=admin`
- Jede Anwendung braucht andere Variablen – schaue in der Dokumentation des jeweiligen Images nach

### Beispiel: Nginx-Webserver

| Feld | Wert |
|---|---|
| Name | `mein-nginx` |
| Image | `nginx:latest` |
| Ports | `8080:80` |
| Environment | *(leer lassen)* |

Nach dem Klick auf "Erstellen" dauert es einen Moment, bis das Image heruntergeladen und der Container gestartet ist. Anschließend ist der Webserver unter `http://localhost:8080` erreichbar.

### Was passiert beim Erstellen?

1. DockerLab prüft, ob bereits ein Container mit dem gleichen Image existiert (um Duplikate zu verhindern)
2. Ein Daten-Ordner unter `data/containers/<containername>/` wird erstellt
3. Dieser Ordner wird in den Container als `/data` gemountet (Ausnahmen: code-server → `/home/coder/project`, VM-Container → `/storage`)
4. Der Container wird mit den angegebenen Einstellungen gestartet

---

## 8. Container verwalten

### Container starten (▶)

Der Container wird gestartet. Voraussetzung: Der Container existiert, ist aber gestoppt.

**Was passiert im Hintergrund:**
1. Die letzten Logs werden unter `data/logs/<name>.log` gespeichert (als Backup vor dem Start)
2. `container.start()` wird aufgerufen
3. Die Container-Liste wird aktualisiert

### Container stoppen (⏸)

Der Container wird geordnet heruntergefahren (Graceful Shutdown).

**Was passiert im Hintergrund:**
1. Die letzten 5000 Log-Zeilen werden gespeichert
2. `container.stop()` wird aufgerufen (sendet SIGTERM, wartet, dann SIGKILL)
3. Der Container bleibt weiter in der Liste (Status: `exited`) – er kann jederzeit wieder gestartet werden

### Container neu starten (🔄)

Entspricht einem Stopp gefolgt von einem Start – in einem Schritt.

### Container löschen (🗑)

**Achtung:** Das Löschen ist dauerhaft!

**Was passiert im Hintergrund:**
1. Logs werden gespeichert
2. Container wird gestoppt
3. Container wird komplett entfernt (`container.remove()`)
4. Der Ordner `data/containers/<containername>/` wird ebenfalls gelöscht

> **Hinweis:** Die Logs unter `data/logs/<containername>.log` bleiben erhalten, als letztes Protokoll der Aktivität.

Eine Bestätigungsabfrage im Browser schützt vor versehentlichem Löschen.

---

## 9. Nextcloud-Synchronisation einrichten (optional)

Die Nextcloud-Sync-Funktion ist **vollständig optional**. DockerLab funktioniert auch ohne sie.

### Wozu ist die Sync-Funktion?

Sie erlaubt es, die `containers.json`-Datei (die Metadaten deiner Container) in einer Nextcloud-Instanz zu sichern. Das ist nützlich, wenn du DockerLab auf mehreren Geräten nutzt und die Container-Liste synchron halten möchtest.

**Wichtig:** Die Sync-Funktion synchronisiert nur die **Metadaten** (Container-Liste), nicht die Container selbst und nicht die Anwendungsdaten.

### Schritt 1: App-Passwort in Nextcloud erstellen

Warum ein App-Passwort? Für automatisierte Tools sollte man nie das Hauptpasswort verwenden. App-Passwörter können jederzeit widerrufen werden, ohne das Hauptkonto zu gefährden.

1. Melde dich in deiner Nextcloud an
2. Klicke oben rechts auf dein Profilbild → **Persönliche Einstellungen**
3. Scrolle nach unten zu **Sicherheit**
4. Unter "App-Passwörter": Gib einen Namen ein (z. B. `DockerLab`) und klicke auf **Neues App-Passwort erstellen**
5. Das angezeigte Passwort **sofort kopieren** – es wird nur einmal angezeigt!

### Schritt 2: .env-Datei aktualisieren

```env
SECRET_KEY=dein-geheimer-schluessel
NEXTCLOUD_URL=https://deine-nextcloud.example.com
NEXTCLOUD_USERNAME=dein-benutzername
NEXTCLOUD_PASSWORD=das-app-passwort-von-schritt-1
NEXTCLOUD_PATH=/DockerLab
```

> **Wichtig bei `NEXTCLOUD_URL`:** Immer mit `https://` beginnen. Kein abschließender Schrägstrich.

### Schritt 3: DockerLab neu starten

```bash
docker compose down
docker compose up -d
```

Damit werden die neuen Umgebungsvariablen geladen.

### Schritt 4: Sync testen

Im Browser: Klicke auf den **"↑ Zu Nextcloud"**-Button. Bei Erfolg erscheint eine grüne Erfolgsmeldung.

In Nextcloud sollte jetzt unter dem konfigurierten Pfad (Standard: `/DockerLab`) eine Datei `containers.json` sichtbar sein.

### Wie funktioniert der Sync technisch?

DockerLab verwendet das **WebDAV-Protokoll**, das Nextcloud standardmäßig anbietet. WebDAV ist ein Erweiterung des HTTP-Protokolls für Dateizugriffe.

- **Upload**: `HTTP PUT` → `https://nextcloud/remote.php/dav/files/<user>/DockerLab/containers.json`
- **Download**: `HTTP GET` → gleiche URL

---

## 10. Praxisbeispiele

### Nginx-Webserver (statische Webseiten)

Nginx ist ein schneller Webserver. Gut zum Ausprobieren oder zum Hosten statischer HTML-Seiten.

| Feld | Wert |
|---|---|
| Name | `webserver` |
| Image | `nginx:latest` |
| Ports | `8080:80` |
| Environment | *(leer)* |

Erreichbar unter: `http://localhost:8080`

Den Inhalt von `data/containers/webserver/` kannst du mit eigenen HTML-Dateien füllen. Nginx sucht standardmäßig in `/usr/share/nginx/html/` – du müsstest das Volume-Mapping noch anpassen, aber für Testzwecke zeigt Nginx direkt die Standard-Welcome-Page.

---

### PostgreSQL-Datenbank

PostgreSQL ist eine leistungsstarke Open-Source-Datenbank.

| Feld | Wert |
|---|---|
| Name | `meine-db` |
| Image | `postgres:15` |
| Ports | `5432:5432` |
| Environment | `POSTGRES_PASSWORD=geheimesPasswort,POSTGRES_USER=admin,POSTGRES_DB=meinprojekt` |

Verbindungsstring für deine Anwendung: `postgresql://admin:geheimesPasswort@localhost:5432/meinprojekt`

> **Wichtig:** Ersetze `geheimesPasswort` durch ein echtes, sicheres Passwort!

---

### Redis-Cache

Redis ist ein extrem schneller In-Memory-Datenspeicher. Ideal für Caching, Sessions oder Queues.

| Feld | Wert |
|---|---|
| Name | `redis-cache` |
| Image | `redis:alpine` |
| Ports | `6379:6379` |
| Environment | *(leer)* |

Verbindung testen:
```bash
docker exec -it redis-cache redis-cli ping
# Ausgabe: PONG
```

---

### VS Code im Browser (code-server)

code-server ist VS Code, das im Browser läuft. DockerLab erkennt das Image automatisch und konfiguriert es korrekt (Authentifizierung wird deaktiviert, Arbeitsverzeichnis wird korrekt gemountet).

| Feld | Wert |
|---|---|
| Name | `vscode` |
| Image | `codercom/code-server:latest` |
| Ports | `8443:8080` |
| Environment | *(leer)* |

Erreichbar unter: `http://localhost:8443`

Deine Projektdateien werden in `data/containers/vscode/` gespeichert.

---

### WordPress + MySQL (zwei Container)

WordPress benötigt eine Datenbank. Erstelle zunächst MySQL:

**Schritt 1 – MySQL:**

| Feld | Wert |
|---|---|
| Name | `wordpress-db` |
| Image | `mysql:8.0` |
| Ports | *(leer – die DB muss nicht von außen erreichbar sein)* |
| Environment | `MYSQL_ROOT_PASSWORD=rootpass,MYSQL_DATABASE=wordpress,MYSQL_USER=wpuser,MYSQL_PASSWORD=wppass` |

**Schritt 2 – WordPress:**

| Feld | Wert |
|---|---|
| Name | `wordpress` |
| Image | `wordpress:latest` |
| Ports | `8090:80` |
| Environment | `WORDPRESS_DB_HOST=wordpress-db,WORDPRESS_DB_NAME=wordpress,WORDPRESS_DB_USER=wpuser,WORDPRESS_DB_PASSWORD=wppass` |

> **Hinweis:** Der Hostname `wordpress-db` funktioniert, weil beide Container im gleichen Docker-Netzwerk (`devnet`) sind und Docker automatisch Container-Namen als Hostnamen auflöst.

---

## 11. Was passiert im Hintergrund? (Technik erklärt)

### Der Docker-Socket – Das Herzstück

In der `docker-compose.yml` steht:
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

`/var/run/docker.sock` ist eine **Unix-Socket-Datei** – eine Art Kommunikationskanal zwischen DockerLab (das selbst in einem Container läuft) und dem Docker-Daemon auf deinem Host-System. Ohne diesen Mount könnte DockerLab keine anderen Container steuern.

### Host-Pfad-Ermittlung

Ein interessantes technisches Problem: Docker-Container kennen nur ihre eigenen Pfade, nicht die echten Pfade auf dem Host. Wenn DockerLab einen neuen Container erstellt und ein Volume mountet (`data/containers/mein-container`), muss es den **echten Host-Pfad** angeben – nicht den Container-Pfad `/data`.

DockerLab löst das durch **Selbst-Inspektion**: Es liest seine eigenen Mount-Informationen aus, um den echten Host-Pfad zu `/data` herauszufinden:

```python
container = docker_client.containers.get('dockerlab-homepage')
for mount in container.attrs.get('Mounts', []):
    if mount.get('Destination') == '/data':
        host_path = mount.get('Source')  # Echter Host-Pfad!
```

### Healthcheck

Docker überprüft regelmäßig, ob DockerLab noch "gesund" ist:
```yaml
healthcheck:
  test: ["CMD", "python3", "-c", "import requests; requests.get('http://localhost:3000')"]
  interval: 30s
  timeout: 10s
  retries: 3
```
Alle 30 Sekunden wird eine HTTP-Anfrage an sich selbst gestellt. Schlägt das 3-mal in Folge fehl, markiert Docker den Container als `unhealthy`.

### Duplikat-Prüfung beim Erstellen

Bevor ein neuer Container erstellt wird, prüft DockerLab: Läuft bereits ein Container mit dem gleichen Image?

```python
normalized_input = image if ':' in image else f"{image}:latest"
for container in existing_containers:
    for tag in container.image.tags:
        if tag == normalized_input:
            return {'success': False, 'error': 'Container mit diesem Image existiert bereits!'}
```

Das verhindert, dass man versehentlich zwei Nginx-Container erstellt, die auf den gleichen Port wollen.

### Besondere Container-Erkennung

DockerLab erkennt spezielle Container-Typen automatisch und passt das Verhalten an:

| Container-Typ | Erkennung | Anpassung |
|---|---|---|
| VM-Container (dockurr/qemu) | `'dockurr'` oder `'qemu'` im Image-Namen | Volume wird als `/storage` gemountet, `privileged: true` aktiviert |
| VS Code (code-server) | `'codercom/code-server'` im Image-Namen | Volume als `/home/coder/project`, Start-Argument `--auth none` |
| Alle anderen | *(kein Match)* | Volume als `/data` |

---

## 12. Häufige Fehler und Lösungen

### "Port already in use" / Port ist bereits belegt

**Symptom:** Beim Erstellen eines Containers erscheint ein Fehler wie `Bind for 0.0.0.0:8080 failed: port is already allocated`.

**Ursache:** Ein anderes Programm oder ein anderer Container verwendet diesen Port bereits.

**Lösung:**
1. Überprüfe, welches Programm den Port verwendet:
   - Windows: `netstat -ano | findstr :8080`
   - macOS/Linux: `lsof -i :8080`
2. Wähle einen anderen Host-Port (z. B. statt `8080:80` verwende `8081:80`)

---

### "No such host" / DNS-Fehler bei Docker Hub

**Symptom:** Beim Erstellen eines Containers erscheint ein Fehler mit `registry-1.docker.io` und `no such host` oder `temporary failure in name resolution`.

**Ursache:** Docker Desktop kann Docker Hub nicht per DNS erreichen. Das ist ein Netzwerkproblem auf Host- oder Docker-Desktop-Ebene.

**Lösung:**
1. Prüfe deine Internetverbindung
2. Teste im Terminal: `docker pull nginx:latest` – schlägt das auch fehl, liegt das Problem bei Docker Desktop
3. Öffne Docker Desktop → **Settings** → **Resources** → **Proxies**: Prüfe ob HTTP/HTTPS-Proxy korrekt konfiguriert ist
4. Prüfe ob `registry-1.docker.io` auflösbar ist: `nslookup registry-1.docker.io`
5. Als letztes Mittel: Docker Desktop neu starten

---

### DockerLab zeigt keine Container an

**Symptom:** Die Container-Liste ist leer, obwohl `docker ps` Container zeigt.

**Mögliche Ursachen und Lösungen:**

1. **Docker-Socket nicht gemountet**: Prüfe `docker-compose.yml` – die Zeile `/var/run/docker.sock:/var/run/docker.sock` muss vorhanden sein
2. **Permission-Problem (Linux)**: Der Docker-Socket gehört der Gruppe `docker`. Füge deinen Benutzer dieser Gruppe hinzu: `sudo usermod -aG docker $USER`
3. **Docker-Daemon läuft nicht**: Starte Docker Desktop neu

```bash
# Logs von DockerLab selbst prüfen:
docker compose logs homepage
```

---

### Nextcloud-Sync funktioniert nicht

**Checkliste:**
- [ ] Ist `NEXTCLOUD_URL` mit `https://` geschrieben? (nicht `http://`)
- [ ] Ist am Ende der URL **kein** Schrägstrich?
- [ ] Wird ein **App-Passwort** verwendet (kein Hauptpasswort)?
- [ ] Existiert der Ordner in Nextcloud? (DockerLab erstellt ihn nicht automatisch!)
- [ ] Ist Nextcloud von dem Rechner, auf dem DockerLab läuft, erreichbar?

**Ordner manuell in Nextcloud erstellen:**
Falls der konfigurierte `NEXTCLOUD_PATH` (Standard: `/DockerLab`) in Nextcloud noch nicht existiert, muss er einmalig manuell erstellt werden.

---

### "Container mit diesem Image existiert bereits"

**Symptom:** Beim Erstellen erscheint die Fehlermeldung, dass ein Container mit diesem Image schon existiert.

**Ursache:** DockerLab verhindert bewusst doppelte Container. Ein Container mit dem gleichen Image läuft bereits.

**Lösung:**
- Prüfe die Container-Liste – welcher Container hat dieses Image?
- Lösche den alten Container, falls er nicht mehr benötigt wird
- Oder wähle eine andere Image-Version (z. B. `nginx:1.25` statt `nginx:latest`)

---

### DockerLab-Seite lädt nicht (localhost:3000)

**Schritt 1:** Ist der Container gestartet?
```bash
docker compose ps
```

**Schritt 2:** Logs lesen:
```bash
docker compose logs homepage
```

**Schritt 3:** Container neu starten:
```bash
docker compose restart
```

**Schritt 4:** Vollständiger Neustart:
```bash
docker compose down
docker compose up -d
```

---

### Nach einem Neustart des PCs sind die Container weg

**Ursache:** Die in DockerLab erstellten Container haben keine `restart`-Policy.

**Lösung:** Um einen Container automatisch zu starten, musst du ihn im Terminal konfigurieren:
```bash
docker update --restart unless-stopped mein-container-name
```

DockerLab selbst startet automatisch nach einem Neustart (dank `restart: unless-stopped` in der `docker-compose.yml`).

---

## 13. Sicherheitshinweise

### SECRET_KEY ändern

Die `.env`-Datei enthält einen `SECRET_KEY`. Dieser wird von Flask verwendet, um z. B. Session-Cookies zu signieren. Verwende einen langen, zufälligen Wert:

```bash
# Zufälligen Schlüssel generieren (Python):
python -c "import secrets; print(secrets.token_hex(32))"
```

### Docker-Socket ist mächtig

`/var/run/docker.sock` zu mounten bedeutet: DockerLab kann **alles** auf dem Docker-Host machen – auch Container mit Root-Rechten und beliebigen Volumes starten. Deshalb:

- Führe DockerLab**nur** in vertrauenswürdigen Umgebungen aus (Heimnetzwerk, lokale Entwicklung)
- Öffne Port 3000 **nicht** für das Internet frei
- DockerLab hat keine eigene Benutzerauthentifizierung

### .env-Datei schützen

Die `.env`-Datei enthält Passwörter. Sie darf **niemals** in ein Git-Repository eingecheckt werden. Füge sie zu `.gitignore` hinzu:

```
.env
data/
```

### Nextcloud App-Passwörter verwenden

Verwende immer App-Passwörter für die Nextcloud-Integration. App-Passwörter haben folgende Vorteile:
- Können einzeln widerrufen werden, ohne das Hauptpasswort zu ändern
- Können nur auf Dateizugriff (WebDAV) beschränkt werden
- Schützen das Hauptkonto bei einer Kompromittierung der `.env`-Datei

---

## 14. DockerLab deinstallieren

### Nur stoppen (Daten bleiben erhalten)

```bash
docker compose down
```

Damit wird der Container gestoppt und entfernt, aber:
- Das gebaute Image bleibt erhalten
- Der `data/`-Ordner bleibt erhalten

### Vollständig entfernen

```bash
# Container stoppen und entfernen
docker compose down

# Gebautes Image entfernen
docker rmi dockerlab-homepage

# Lokale Daten löschen (Achtung: unwiderruflich!)
# Windows PowerShell:
Remove-Item -Recurse -Force .\data\

# macOS/Linux:
rm -rf data/
```

---

## 15. Glossar – Fachbegriffe erklärt

| Begriff | Erklärung |
|---|---|
| **API** | Application Programming Interface – eine definierte Schnittstelle, über die Programme miteinander kommunizieren |
| **Container** | Ein isolierter, in sich geschlossener Prozess in Docker |
| **Daemon** | Ein Hintergrundprozess – der Docker-Daemon (`dockerd`) läuft im Hintergrund und verwaltet alle Container |
| **Detached (`-d`)** | Container läuft im Hintergrund, blockiert das Terminal nicht |
| **Docker Hub** | Offizielle Registry (Sammlung) der Docker-Images unter `hub.docker.com` |
| **Dockerfile** | Eine Textdatei mit Anweisungen, wie ein Docker-Image gebaut wird |
| **docker-compose.yml** | Konfigurationsdatei für Docker Compose |
| **Environment Variable** | Eine Variable, die dem Programm bei Start übergeben wird – üblich für Konfiguration (Passwörter, URLs etc.) |
| **Flask** | Ein leichtgewichtiges Python-Framework für Webanwendungen |
| **Graceful Shutdown** | Das Programm wird "sanft" beendet – es bekommt Zeit zum Aufräumen (im Gegensatz zum harten Abbruch) |
| **Healthcheck** | Automatische Überprüfung, ob ein Container noch korrekt funktioniert |
| **Image** | Eine unveränderliche Vorlage/Blaupause für einen Container |
| **JSON** | JavaScript Object Notation – ein einfaches Textformat zur Datenspeicherung: `{"schluessel": "wert"}` |
| **Mount / Volume** | Ein Ordner des Hosts der in den Container eingebunden wird |
| **Port** | Eine Nummer (1–65535), über die ein Netzwerkdienst erreichbar ist |
| **Registry** | Ein Server der Docker-Images speichert und bereitstellt (z. B. Docker Hub) |
| **REST API** | Ein Stil für Webschnittstellen – Aktionen werden über HTTP-Methoden (GET, POST, DELETE) ausgedrückt |
| **SIGTERM / SIGKILL** | Unix-Signale zum Beenden von Prozessen. SIGTERM = "bitte beende dich", SIGKILL = "sofortiger Abbruch" |
| **Socket** | Ein Kommunikationsendpunkt – `docker.sock` ist ein Unix-Socket für die Docker-API |
| **TAG** | Die Version eines Images (z. B. `latest`, `alpine`, `3.9-slim`) |
| **WebDAV** | Web Distributed Authoring and Versioning – ein Protokoll für Dateizugriff über HTTP, wird von Nextcloud verwendet |
| **WSL 2** | Windows Subsystem for Linux 2 – ermöglicht Linux-Prozesse unter Windows, wird von Docker Desktop genutzt |

---

## Schnellübersicht – Häufige Befehle

```bash
# DockerLab starten
docker compose up -d

# DockerLab stoppen
docker compose down

# Logs von DockerLab anzeigen
docker compose logs -f homepage

# Status prüfen
docker compose ps

# Alle laufenden Container anzeigen
docker ps

# Alle Container (auch gestoppte) anzeigen
docker ps -a

# Image für DockerLab neu bauen (nach Code-Änderungen)
docker compose up -d --build
```

---

*Letzte Aktualisierung: März 2026 | DockerLab – Persönliches Container-Management für Zuhause*
