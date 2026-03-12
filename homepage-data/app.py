#!/usr/bin/env python3
import os
import docker
import requests
import shutil
from requests.auth import HTTPBasicAuth
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, Response, stream_with_context
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dockerlab-secret-key')
import json
DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
LOGS_PATH = os.path.join(DATA_PATH, 'logs')
CONTAINERS_FILE = os.path.join(DATA_PATH, 'containers.json')
NEXTCLOUD_URL = os.getenv('NEXTCLOUD_URL', '')
NEXTCLOUD_USERNAME = os.getenv('NEXTCLOUD_USERNAME', '')
NEXTCLOUD_PASSWORD = os.getenv('NEXTCLOUD_PASSWORD', '')
NEXTCLOUD_PATH = os.getenv('NEXTCLOUD_PATH', '/DockerLab')
try:
    docker_client = docker.from_env()
except Exception as e:
    print(f"WARNUNG: Docker-Client konnte nicht initialisiert werden: {e}")
    docker_client = None
_host_data_path_cache = None
def get_host_data_path():
    """Ermittelt den echten Host-Pfad von /data durch Selbstinspektion des eigenen Containers.
    Das ist nötig, weil der Docker-Daemon Host-Pfade braucht, keine Container-Pfade."""
    global _host_data_path_cache
    if _host_data_path_cache:
        return _host_data_path_cache
    try:
        container = docker_client.containers.get('dockerlab-homepage')
        for mount in container.attrs.get('Mounts', []):
            if mount.get('Destination') == '/data':
                host_path = mount.get('Source')
                print(f"Host-Pfad für /data gefunden: {host_path}")
                _host_data_path_cache = host_path
                return host_path
    except Exception as e:
        print(f"Warnung: Host-Pfad konnte nicht per Selbstinspektion ermittelt werden: {e}")
    print(f"Fallback: Verwende Container-Pfad {DATA_PATH} als Host-Pfad")
    return DATA_PATH
def get_webdav_auth():
    """Gibt WebDAV Auth-Objekt zurück"""
    if not NEXTCLOUD_USERNAME or not NEXTCLOUD_PASSWORD:
        return None
    return HTTPBasicAuth(NEXTCLOUD_USERNAME, NEXTCLOUD_PASSWORD)
def sync_to_nextcloud():
    """Synchronisiert lokale Daten mit Nextcloud"""
    if not NEXTCLOUD_URL or not NEXTCLOUD_USERNAME or not NEXTCLOUD_PASSWORD:
        return {'success': False, 'error': 'Nextcloud nicht konfiguriert'}
    
    try:
        webdav_url = f"{NEXTCLOUD_URL}/remote.php/dav/files/{NEXTCLOUD_USERNAME}{NEXTCLOUD_PATH}/containers.json"
        
        containers = get_all_containers()
        content = json.dumps(containers, indent=2, default=str)
        os.makedirs(DATA_PATH, exist_ok=True)
        with open(CONTAINERS_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        response = requests.put(
            webdav_url,
            data=content.encode('utf-8'),
            auth=get_webdav_auth(),
            timeout=10
        )
        
        if response.status_code in [200, 201, 204]:
            return {'success': True, 'message': 'Erfolgreich zu Nextcloud synchronisiert'}
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}: {response.text}'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}
def sync_from_nextcloud():
    """Lädt Daten von Nextcloud herunter"""
    if not NEXTCLOUD_URL or not NEXTCLOUD_USERNAME or not NEXTCLOUD_PASSWORD:
        return {'success': False, 'error': 'Nextcloud nicht konfiguriert'}
    
    try:
        webdav_url = f"{NEXTCLOUD_URL}/remote.php/dav/files/{NEXTCLOUD_USERNAME}{NEXTCLOUD_PATH}/containers.json"
        
        response = requests.get(
            webdav_url,
            auth=get_webdav_auth(),
            timeout=10
        )
        
        if response.status_code == 200:
            os.makedirs(DATA_PATH, exist_ok=True)
            with open(CONTAINERS_FILE, 'w', encoding='utf-8') as f:
                f.write(response.text)
            return {'success': True, 'message': 'Erfolgreich von Nextcloud synchronisiert'}
        elif response.status_code == 404:
            return {'success': False, 'error': 'Keine Daten auf Nextcloud gefunden'}
        else:
            return {'success': False, 'error': f'HTTP {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}
def save_container_logs(container):
    """Speichert die letzten Logs eines Containers in /data/logs/{name}.log"""
    try:
        os.makedirs(LOGS_PATH, exist_ok=True)
        log_file = os.path.join(LOGS_PATH, f"{container.name}.log")
        logs = container.logs(tail=5000, timestamps=True).decode('utf-8', errors='replace')
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(logs)
        print(f"Logs gespeichert: {log_file}")
    except Exception as e:
        print(f"Warnung: Logs konnten nicht gespeichert werden: {e}")
def get_all_containers():
    """Gibt alle Docker-Container zurück (außer dockerlab-homepage selbst)"""
    if not docker_client:
        return []
    
    try:
        containers = docker_client.containers.list(all=True)
        container_list = []
        
        for container in containers:
            if container.name == 'dockerlab-homepage':
                continue
                
            container_list.append({
                'id': container.short_id,
                'name': container.name,
                'image': container.image.tags[0] if container.image.tags else container.image.short_id,
                'status': container.status,
                'state': container.attrs['State']['Status'],
                'created': container.attrs['Created'],
                'ports': container.ports
            })
        
        return container_list
    except Exception as e:
        print(f"Fehler beim Abrufen der Container: {e}")
        return []
def start_container(container_name):
    """Startet einen Container"""
    if not docker_client:
        return {'success': False, 'error': 'Docker-Client nicht verfügbar'}
    
    try:
        container = docker_client.containers.get(container_name)
        save_container_logs(container)
        container.start()
        return {'success': True, 'message': f'Container {container_name} gestartet'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
def stop_container(container_name):
    """Stoppt einen Container"""
    if not docker_client:
        return {'success': False, 'error': 'Docker-Client nicht verfügbar'}
    
    try:
        container = docker_client.containers.get(container_name)
        save_container_logs(container)
        container.stop()
        return {'success': True, 'message': f'Container {container_name} gestoppt'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
def restart_container(container_name):
    """Startet einen Container neu"""
    if not docker_client:
        return {'success': False, 'error': 'Docker-Client nicht verfügbar'}
    
    try:
        container = docker_client.containers.get(container_name)
        container.restart()
        return {'success': True, 'message': f'Container {container_name} neu gestartet'}
    except Exception as e:
        return {'success': False, 'error': str(e)}
def delete_container(container_name):
    """Löscht einen Container und seine Daten"""
    if not docker_client:
        return {'success': False, 'error': 'Docker-Client nicht verfügbar'}
    
    try:
        container = docker_client.containers.get(container_name)
        save_container_logs(container)
        container.stop()
        container.remove()
        
        container_data_path = os.path.join(DATA_PATH, 'containers', container_name)
        if os.path.exists(container_data_path):
            try:
                shutil.rmtree(container_data_path)
                print(f"Container-Daten gelöscht: {container_data_path}")
            except Exception as e:
                print(f"Warnung: Container-Daten konnten nicht gelöscht werden: {e}")
        
        return {'success': True, 'message': f'Container {container_name} und Daten gelöscht'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def format_docker_error(error):
    """Macht häufige Docker-Fehler für die UI verständlicher."""
    message = str(error)
    lower_message = message.lower()

    if 'registry-1.docker.io' in lower_message:
        if 'no such host' in lower_message or 'temporary failure in name resolution' in lower_message:
            return (
                'Docker Desktop kann Docker Hub aktuell nicht per DNS erreichen '
                '(registry-1.docker.io). Das ist ein Netzwerkproblem auf Host- oder '
                'Docker-Desktop-Ebene. Prüfen Sie Internetverbindung, DNS/Proxy in '
                'Docker Desktop und testen Sie danach `docker pull nginx:latest` im Terminal erneut.'
            )
        if 'proxy' in lower_message:
            return (
                'Docker Desktop erreicht Docker Hub wegen einer Proxy-Konfiguration nicht. '
                'Prüfen Sie in Docker Desktop unter Settings > Resources > Proxies die HTTP/HTTPS-Proxy-Werte '
                'und testen Sie anschließend `docker pull nginx:latest` erneut.'
            )

    return message

def create_container(name, image, ports=None, environment=None):
    """Erstellt einen neuen Container mit persistenten Daten in ./data/containers/{name}/"""
    if not docker_client:
        return {'success': False, 'error': 'Docker-Client nicht verfügbar'}
    
    # Prüfen, ob bereits ein Container mit dem gleichen Image existiert
    try:
        existing_containers = docker_client.containers.list(all=True)
        # Normalisiere das Input-Image
        normalized_input = image if ':' in image else f"{image}:latest"
        
        for container in existing_containers:
            if container.name == 'dockerlab-homepage':
                continue
            
            # Alle Tags des Container-Images prüfen
            container_tags = container.image.tags if container.image.tags else []
            
            for tag in container_tags:
                if tag == normalized_input or tag == image:
                    return {
                        'success': False, 
                        'error': f'Dieser Container existiert bereits! Ein Container mit dem Image "{tag}" läuft bereits unter dem Namen "{container.name}".'
                    }
    except Exception as e:
        print(f"Warnung bei Container-Prüfung: {e}")
    
    try:
        container_data_path = os.path.join(DATA_PATH, 'containers', name)
        os.makedirs(container_data_path, exist_ok=True)
        print(f"Container-Daten-Verzeichnis erstellt: {container_data_path}")
        
        host_data_root = get_host_data_path()
        host_container_data_path = os.path.join(host_data_root, 'containers', name)
        
        port_bindings = {}
        if ports:
            for port_mapping in ports.split(','):
                if ':' in port_mapping:
                    host_port, container_port = port_mapping.strip().split(':')
                    port_bindings[f'{container_port}/tcp'] = int(host_port)
        
        env_dict = {}
        if environment:
            for env_var in environment.split(','):
                if '=' in env_var:
                    key, value = env_var.strip().split('=', 1)
                    env_dict[key] = value
        
        is_vm_container = 'dockurr' in image.lower() or 'qemu' in image.lower()
        is_code_server = 'codercom/code-server' in image.lower()
        if is_vm_container:
            bind_path = '/storage'
        elif is_code_server:
            bind_path = '/home/coder/project'
        else:
            bind_path = '/data'
        volumes = {
            host_container_data_path: {'bind': bind_path, 'mode': 'rw'}
        }

        container_command = ['--auth', 'none', '/home/coder/project'] if is_code_server else None
        working_dir = '/home/coder/project' if is_code_server else None
        
        container = docker_client.containers.run(
            image,
            name=name,
            ports=port_bindings if port_bindings else None,
            environment=env_dict if env_dict else None,
            volumes=volumes,
            command=container_command,
            working_dir=working_dir,
            privileged=is_vm_container,
            detach=True
        )
        
        return {'success': True, 'message': f'Container {name} erstellt und gestartet'}
    except Exception as e:
        return {'success': False, 'error': format_docker_error(e)}
@app.route('/')
def index():
    """Hauptseite mit Container-Übersicht"""
    containers = get_all_containers()
    nextcloud_configured = bool(NEXTCLOUD_URL and NEXTCLOUD_USERNAME and NEXTCLOUD_PASSWORD)
    
    return render_template('main.html',
                          containers=containers,
                          nextcloud_configured=nextcloud_configured)
def format_ports(raw_ports):
    """Formatiert Docker-Port-Dict in lesbaren String"""
    if not raw_ports:
        return ''
    parts = []
    for container_port, bindings in raw_ports.items():
        if bindings:
            for b in bindings:
                parts.append(f"{b['HostPort']}:{container_port.split('/')[0]}")
        else:
            parts.append(container_port)
    return ', '.join(parts)
@app.route('/api/containers')
def api_containers():
    """API Endpoint für Container-Liste (gibt Array zurück)"""
    try:
        raw = get_all_containers()
        result = []
        for c in raw:
            result.append({
                'id': c['id'],
                'name': c['name'],
                'image': c['image'],
                'status': c['status'],
                'ports': format_ports(c['ports']),
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/api/containers/create', methods=['POST'])
def api_containers_create():
    """API Endpoint zum Erstellen eines Containers"""
    data = request.json
    name = data.get('name', '').strip()
    image = data.get('image', '').strip()
    ports = data.get('ports', '')
    environment = data.get('environment', '')
    if not name or not image:
        return jsonify({'error': 'Name und Image erforderlich'}), 400
    result = create_container(name, image, ports, environment)
    if result.get('success'):
        return jsonify(result)
    return jsonify({'error': result.get('error', 'Unbekannter Fehler')}), 500
@app.route('/api/containers/<container_id>/<action>', methods=['POST'])
def api_containers_action(container_id, action):
    """API Endpoint für Container-Aktionen (start/stop/restart/delete)"""
    if action == 'start':
        result = start_container(container_id)
    elif action == 'stop':
        result = stop_container(container_id)
    elif action == 'restart':
        result = restart_container(container_id)
    elif action == 'delete':
        result = delete_container(container_id)
    else:
        return jsonify({'error': 'Unbekannte Aktion'}), 400
    if result.get('success'):
        return jsonify(result)
    return jsonify({'error': result.get('error', 'Unbekannter Fehler')}), 500
@app.route('/api/containers/<container_id>/logs')
def api_container_logs(container_id):
    """Streamt Logs eines Containers via Server-Sent Events in Echtzeit"""
    if not docker_client:
        return jsonify({'error': 'Docker-Client nicht verfügbar'}), 500
    try:
        container = docker_client.containers.get(container_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    def generate():
        try:
            history = container.logs(tail=200, timestamps=True).decode('utf-8', errors='replace')
            for line in history.splitlines():
                yield f"data: {line}\n\n"
        except Exception:
            pass
        try:
            for chunk in container.logs(stream=True, follow=True, timestamps=True):
                line = chunk.decode('utf-8', errors='replace').rstrip('\n')
                if line:
                    yield f"data: {line}\n\n"
        except Exception as e:
            yield f"data: [Stream beendet: {e}]\n\n"
    return Response(stream_with_context(generate()), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})
@app.route('/api/nextcloud/sync-to', methods=['POST'])
def api_nextcloud_sync_to():
    """API Endpoint zum Upload zu Nextcloud"""
    result = sync_to_nextcloud()
    if result.get('success'):
        return jsonify(result)
    return jsonify({'error': result.get('error', 'Synchronisierung fehlgeschlagen')}), 500
@app.route('/api/nextcloud/sync-from', methods=['POST'])
def api_nextcloud_sync_from():
    """API Endpoint zum Download von Nextcloud"""
    result = sync_from_nextcloud()
    if result.get('success'):
        return jsonify(result)
    return jsonify({'error': result.get('error', 'Synchronisierung fehlgeschlagen')}), 500
if __name__ == '__main__':
    print("=" * 70)
    print("DockerLab - Container Management System")
    print("=" * 70)
    
    if docker_client:
        print(f"✓ Docker verbunden")
    else:
        print(f"✗ Docker nicht verfügbar")
    
    if NEXTCLOUD_URL and NEXTCLOUD_USERNAME and NEXTCLOUD_PASSWORD:
        print(f"✓ Nextcloud konfiguriert: {NEXTCLOUD_URL}")
    else:
        print(f"ℹ Nextcloud nicht konfiguriert (optional)")
    
    print("=" * 70)
    print("Server läuft auf http://localhost:3000")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=3000, debug=True)