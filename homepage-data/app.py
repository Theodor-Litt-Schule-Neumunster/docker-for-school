#!/usr/bin/env python3
"""
DockerLab - VM Management System mit SSH-Steuerung
Windows Server 2022, Debian VMs, VS Code Server
Admin-Panel für User-Verwaltung
"""

import os
import json
import yaml
import re
import subprocess
import shutil
import tarfile
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import paramiko
from io import StringIO

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'theodor-litt-secret-key-change-in-production')

# SSH Konfiguration aus Umgebungsvariablen
SSH_HOST = os.getenv('SSH_REMOTE_HOST', '100.66.170.64')
SSH_REMOTE_HOST = SSH_HOST  # Alias für Kompatibilität
SSH_USER = os.getenv('SSH_REMOTE_USER', 'dataserver')
SSH_PATH = os.getenv('SSH_REMOTE_PATH', '/srv/schuler-daten')
SSH_KEY_PATH = os.path.expanduser('~/.ssh/id_rsa')

# Pfade auf Remote-Server (nur für User-Verwaltung)
REMOTE_USERS_FILE = f"{SSH_PATH}/users.json"
REMOTE_ADMIN_CREDENTIALS = f"{SSH_PATH}/admin_credentials.yml"

# Lokale Pfade für VMs (laufen auf diesem PC)
LOCAL_VMS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'vm-data'))

# VNC Port-Mapping (10 gleichzeitige User)
VNC_PORT_START = 5900
NOVNC_PORT_START = 6080


# ============================================================================
# SSH Helper-Funktionen
# ============================================================================

def get_ssh_client():
    """Erstellt SSH-Verbindung zum Remote-Server"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Deaktiviere veraltete/unsichere Algorithmen
        disabled_algorithms = dict(pubkeys=["ssh-dss"])
        
        # Suche nach verfügbaren SSH-Keys (bevorzuge moderne Keys)
        key_paths = [
            os.path.expanduser("~/.ssh/id_ed25519"),
            os.path.expanduser("~/.ssh/id_rsa"),
            SSH_KEY_PATH
        ]
        
        available_key = None
        for key_path in key_paths:
            if os.path.exists(key_path):
                available_key = key_path
                print(f"Verwende SSH-Key: {key_path}")
                break
        
        # Verbindung mit SSH-Key
        if available_key:
            ssh.connect(
                SSH_HOST, 
                username=SSH_USER, 
                key_filename=available_key, 
                timeout=10,
                disabled_algorithms=disabled_algorithms,
                look_for_keys=True,
                allow_agent=False
            )
        else:
            print(f"WARNUNG: Kein SSH-Key gefunden!")
            ssh.connect(
                SSH_HOST, 
                username=SSH_USER, 
                timeout=10,
                disabled_algorithms=disabled_algorithms,
                look_for_keys=True,
                allow_agent=False
            )
        
        return ssh
    except Exception as e:
        print(f"SSH-Verbindungsfehler: {e}")
        import traceback
        traceback.print_exc()
        return None


def read_remote_file(filepath):
    """Liest eine Datei vom Remote-Server"""
    ssh = get_ssh_client()
    if not ssh:
        return None
    
    try:
        sftp = ssh.open_sftp()
        
        # Prüfe ob Datei existiert
        try:
            sftp.stat(filepath)
        except FileNotFoundError:
            print(f"Datei existiert nicht: {filepath}")
            sftp.close()
            ssh.close()
            return None
        
        # Datei lesen
        with sftp.open(filepath, 'r') as f:
            content = f.read().decode('utf-8')
        
        sftp.close()
        ssh.close()
        return content
        
    except Exception as e:
        print(f"Fehler beim Lesen der Remote-Datei {filepath}: {e}")
        ssh.close()
        return None


def write_remote_file(filepath, content):
    """Schreibt eine Datei auf den Remote-Server"""
    ssh = get_ssh_client()
    if not ssh:
        return False
    
    try:
        sftp = ssh.open_sftp()
        
        # Stelle sicher, dass das Verzeichnis existiert
        remote_dir = os.path.dirname(filepath)
        try:
            sftp.stat(remote_dir)
        except FileNotFoundError:
            # Verzeichnis erstellen
            ssh.exec_command(f'mkdir -p {remote_dir}')
        
        # Datei schreiben
        with sftp.open(filepath, 'w') as f:
            f.write(content.encode('utf-8') if isinstance(content, str) else content)
        
        sftp.close()
        ssh.close()
        return True
        
    except Exception as e:
        print(f"Fehler beim Schreiben der Remote-Datei {filepath}: {e}")
        ssh.close()
        return False


def execute_ssh_command(command, return_output=True):
    """Führt SSH-Befehl aus und gibt Ergebnis zurück"""
    print(f"[SSH] Führe Befehl aus: {command[:100]}...")  # Debug-Log
    ssh = get_ssh_client()
    if not ssh:
        print("[SSH] Fehler: Keine SSH-Verbindung!")
        return None if return_output else False
    
    try:
        stdin, stdout, stderr = ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        
        if return_output:
            output = stdout.read().decode('utf-8').strip()
            error = stderr.read().decode('utf-8').strip()
            
            # Debug-Ausgabe
            if exit_status == 0:
                print(f"[SSH] ✓ Erfolg! Output: {output[:200]}")
            else:
                print(f"[SSH] ✗ Fehler (Exit {exit_status})! Error: {error[:200]}")
            
            ssh.close()
            return {'success': exit_status == 0, 'output': output, 'error': error}
        else:
            ssh.close()
            return exit_status == 0
    except Exception as e:
        print(f"SSH-Befehl Fehler: {e}")
        ssh.close()
        return None if return_output else False


# ============================================================================
# User-Verwaltung (SSH-basiert)
# ============================================================================

def load_users():
    """Lädt users.json vom Remote-Server"""
    content = read_remote_file(REMOTE_USERS_FILE)
    if content:
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"JSON-Fehler beim Laden der Users: {e}")
            return {}
    return {}


def save_users(users):
    """Speichert users.json auf den Remote-Server"""
    try:
        content = json.dumps(users, indent=2, ensure_ascii=False)
        return write_remote_file(REMOTE_USERS_FILE, content)
    except Exception as e:
        print(f"Fehler beim Speichern der Users: {e}")
        return False


def load_admin_credentials():
    """Lädt Admin-Credentials vom Remote-Server"""
    content = read_remote_file(REMOTE_ADMIN_CREDENTIALS)
    if content:
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            print(f"YAML-Fehler beim Laden der Admin-Credentials: {e}")
            return None
    return None


def verify_admin_credentials(username, password):
    """Überprüft Admin-Credentials"""
    admin_creds = load_admin_credentials()
    if not admin_creds:
        print("WARNUNG: Keine Admin-Credentials gefunden!")
        return False
    
    # Prüfe Admin-Liste
    admins = admin_creds.get('admins', [])
    for admin in admins:
        if admin.get('username') == username:
            # Passwort-Hash vergleichen
            stored_hash = admin.get('password_hash')
            if stored_hash and check_password_hash(stored_hash, password):
                return True
            # Alternativ: Klartext-Passwort (nicht empfohlen, aber für einfache Einrichtung)
            stored_password = admin.get('password')
            if stored_password and stored_password == password:
                return True
    
    return False


def get_user_port(username):
    """Berechnet VNC/noVNC Ports für User"""
    users = load_users()
    user_list = sorted(users.keys())
    
    if username not in user_list:
        return None
    
    user_index = user_list.index(username)
    vnc_port = VNC_PORT_START + user_index
    novnc_port = NOVNC_PORT_START + user_index
    
    return {'vnc': vnc_port, 'novnc': novnc_port, 'index': user_index}


# ============================================================================
# VM-Management Klasse (Lokal)
# ============================================================================

import subprocess

class LocalVMManager:
    """Verwaltet VMs über SSH auf Remote-Server"""
    
    def __init__(self):
        self.ssh_host = SSH_HOST
        self.ssh_user = SSH_USER
    
    def create_user_vms(self, username):
        """Erstellt VM-Umgebung für neuen User (lokal)"""
        user_vm_path = os.path.join(LOCAL_VMS_PATH, username)
        print(f"[VM] Erstelle lokales VM-Verzeichnis: {user_vm_path}")
        
        try:
            os.makedirs(os.path.join(user_vm_path, 'windows'), exist_ok=True)
            os.makedirs(os.path.join(user_vm_path, 'debian'), exist_ok=True)
            os.makedirs(os.path.join(user_vm_path, 'vscode-config'), exist_ok=True)
            print(f"[VM] ✓ Verzeichnisse erstellt")
            return True
        except Exception as e:
            print(f"[VM] ✗ Fehler beim Erstellen: {e}")
            return False
    
    def start_windows_vm(self, username):
        """Startet Windows Server 2022 VM lokal über dockur/windows"""
        print(f"[VM] Starte Windows VM für User: {username}")
        ports = get_user_port(username)
        if not ports:
            print(f"[VM] ✗ Fehler: Keine Ports für User {username}")
            return {'success': False, 'error': 'Port-Zuweisung fehlgeschlagen'}
        
        print(f"[VM] Ports: VNC={ports['vnc']}, noVNC={ports['novnc']}")
        
        vm_name = f"{username}-windows"
        vm_path = os.path.join(LOCAL_VMS_PATH, username, 'windows')
        
        print(f"[VM] Lokaler VM-Pfad: {vm_path}")
        os.makedirs(vm_path, exist_ok=True)
        
        # Docker-Befehl als String zusammensetzen (funktioniert besser mit komplexen Parametern)
        command = [
            'docker', 'run', '-d',
            '--name', vm_name,
            '--privileged',
            '-p', f"{ports['novnc']}:8006",
            '-p', f"{ports['vnc']}:5900",
            '-v', f"{os.path.abspath(vm_path)}:/storage",
            '-e', 'VERSION=win2022',
            '-e', 'RAM_SIZE=4G',
            '-e', 'CPU_CORES=2',
            '-e', 'DISK_SIZE=64G',
            'dockurr/windows'
        ]
        
        print(f"[VM] Führe Docker-Befehl lokal aus...")
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"[VM] ✓ Windows VM erfolgreich gestartet: {vm_name}")
                print(f"[VM] Container-ID: {result.stdout.strip()[:12]}")
                return {'success': True, 'output': result.stdout.strip()}
            else:
                print(f"[VM] ✗ Fehler: {result.stderr}")
                return {'success': False, 'error': result.stderr}
        except Exception as e:
            print(f"[VM] ✗ Exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def start_debian_vm(self, username):
        """Startet Debian VM lokal über qemus/qemu"""
        print(f"[VM] Starte Debian VM für User: {username}")
        ports = get_user_port(username)
        if not ports:
            print(f"[VM] ✗ Fehler: Keine Ports für User {username}")
            return {'success': False, 'error': 'Port-Zuweisung fehlgeschlagen'}
        
        print(f"[VM] Ports: VNC={ports['vnc']}, noVNC={ports['novnc']+10}")
        
        vm_name = f"{username}-debian"
        vm_path = os.path.join(LOCAL_VMS_PATH, username, 'debian')
        
        print(f"[VM] Lokaler VM-Pfad: {vm_path}")
        os.makedirs(vm_path, exist_ok=True)
        
        command = [
            'docker', 'run', '-d',
            '--name', vm_name,
            '--privileged',
            '-p', f"{ports['novnc']+10}:8006",
            '-v', f"{os.path.abspath(vm_path)}:/storage",
            '-e', 'BOOT=debian',
            '-e', 'RAM_SIZE=2G',
            '-e', 'CPU_CORES=2',
            '-e', 'DISK_SIZE=32G',
            'qemux/qemu'
        ]
        
        print(f"[VM] Führe Docker-Befehl lokal aus...")
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"[VM] ✓ Debian VM erfolgreich gestartet: {vm_name}")
                print(f"[VM] Container-ID: {result.stdout.strip()[:12]}")
                return {'success': True, 'output': result.stdout.strip()}
            else:
                print(f"[VM] ✗ Fehler: {result.stderr}")
                return {'success': False, 'error': result.stderr}
        except Exception as e:
            print(f"[VM] ✗ Exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def stop_vm(self, username, vm_type):
        """Stoppt VM lokal"""
        vm_name = f"{username}-{vm_type}"
        print(f"[VM] Stoppe {vm_type} VM: {vm_name}")
        
        try:
            # Stoppe Container lokal
            result = subprocess.run(['docker', 'stop', vm_name], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print(f"[VM] ✓ VM gestoppt")
                # Container entfernen
                subprocess.run(['docker', 'rm', vm_name], capture_output=True, text=True)
                return {'success': True, 'message': 'VM gestoppt'}
            else:
                print(f"[VM] ✗ Fehler: {result.stderr}")
                return {'success': False, 'error': result.stderr}
        except Exception as e:
            print(f"[VM] ✗ Exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_vm(self, username, vm_type):
        """Löscht VM lokal"""
        vm_name = f"{username}-{vm_type}"
        vm_path = os.path.join(LOCAL_VMS_PATH, username, vm_type)
        print(f"[VM] Lösche {vm_type} VM: {vm_name}")
        
        try:
            # Stoppe und entferne Container
            subprocess.run(['docker', 'stop', vm_name], capture_output=True, text=True)
            subprocess.run(['docker', 'rm', vm_name], capture_output=True, text=True)
            
            # Lösche lokale Daten
            import shutil
            if os.path.exists(vm_path):
                shutil.rmtree(vm_path)
                print(f"[VM] ✓ VM-Daten gelöscht: {vm_path}")
            
            return {'success': True, 'message': 'VM gelöscht'}
        except Exception as e:
            print(f"[VM] ✗ Exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_vm_status(self, username):
        """Gibt Status aller VMs zurück (lokal)"""
        status = {}
        
        # Ports für den User abrufen
        ports = get_user_port(username)
        
        for vm_type in ['windows', 'debian', 'vscode']:
            vm_name = f"{username}-{vm_type}"
            
            try:
                # Prüfe ob Container läuft
                result_running = subprocess.run(
                    ['docker', 'ps', '-q', '-f', f'name={vm_name}'],
                    capture_output=True, text=True
                )
                is_running = bool(result_running.stdout.strip())
                
                # Prüfe ob Container existiert (auch gestoppt)
                result_exists = subprocess.run(
                    ['docker', 'ps', '-aq', '-f', f'name={vm_name}'],
                    capture_output=True, text=True
                )
                is_created = bool(result_exists.stdout.strip())
                
                status[vm_type] = {
                    'running': is_running,
                    'created': is_created,
                    'name': vm_name
                }
                
                # Füge Ports hinzu
                if ports:
                    if vm_type == 'windows':
                        status[vm_type]['vnc_port'] = ports['vnc']
                        status[vm_type]['novnc_port'] = ports['novnc']
                    elif vm_type == 'debian':
                        status[vm_type]['vnc_port'] = ports['vnc']
                        status[vm_type]['novnc_port'] = ports['novnc'] + 10
                    elif vm_type == 'vscode':
                        status[vm_type]['port'] = 8080 + ports['index']
            
            except Exception as e:
                print(f"[VM] Fehler beim Status-Check für {vm_name}: {e}")
                status[vm_type] = {'running': False, 'created': False, 'name': vm_name}
        
        if ports:
            status['ports'] = ports
        
        return status
    
    def start_vscode(self, username):
        """Startet VS Code Server lokal"""
        ports = get_user_port(username)
        if not ports:
            return {'success': False, 'error': 'Port-Zuweisung fehlgeschlagen'}
        
        vm_name = f"{username}-vscode"
        vm_path = os.path.join(LOCAL_VMS_PATH, username, 'vscode-config')
        vscode_port = 8080 + ports['index']
        
        print(f"[VM] Starte VS Code Server: {vm_name} auf Port {vscode_port}")
        
        try:
            # Erstelle Verzeichnis falls es nicht existiert
            os.makedirs(vm_path, exist_ok=True)
            
            # Prüfe ob Container bereits läuft
            result_check = subprocess.run(['docker', 'ps', '-q', '-f', f'name={vm_name}'], capture_output=True, text=True)
            if result_check.stdout.strip():
                print(f"[VM] Container läuft bereits: {vm_name}")
                return {'success': True, 'message': 'VS Code Server läuft bereits', 'port': vscode_port}
            
            # Starte Container
            result = subprocess.run([
                'docker', 'run', '-d',
                '--name', vm_name,
                '-p', f'{vscode_port}:8080',
                '-v', f'{os.path.abspath(vm_path)}:/home/coder/project',
                '-e', f'PASSWORD={username}123',
                'codercom/code-server:latest'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"[VM] ✓ VS Code Server gestartet")
                return {'success': True, 'message': 'VS Code Server gestartet', 'port': vscode_port}
            else:
                print(f"[VM] ✗ Fehler: {result.stderr}")
                return {'success': False, 'error': result.stderr}
        
        except Exception as e:
            print(f"[VM] ✗ Exception: {e}")
            return {'success': False, 'error': str(e)}


# Globale VM Manager Instanz
vm_manager = LocalVMManager()


# ============================================================================
# Login Decorators
# ============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Bitte melden Sie sich an.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session or not session.get('admin'):
            flash('Admin-Berechtigung erforderlich.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# Routes
# ============================================================================

@app.route('/')
def index():
    """Hauptseite"""
    if 'username' in session:
        return redirect(url_for('dashboard'))
    if 'admin' in session:
        return redirect(url_for('admin_panel'))
    return redirect(url_for('login'))


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin-Login (separater Zugang)"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Bitte füllen Sie alle Felder aus.', 'error')
            return render_template('admin_login.html')
        
        if verify_admin_credentials(username, password):
            session['admin'] = True
            session['admin_username'] = username
            flash('Admin-Login erfolgreich!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Ungültige Admin-Zugangsdaten.', 'error')
    
    return render_template('admin_login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login-Seite"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Bitte füllen Sie alle Felder aus.', 'error')
            return render_template('login.html')
        
        # User-Daten laden
        users = load_users()
        
        if username not in users:
            flash('Benutzername oder Passwort falsch.', 'error')
            return render_template('login.html')
        
        user = users[username]
        
        # Passwort überprüfen
        if not check_password_hash(user['password_hash'], password):
            flash('Benutzername oder Passwort falsch.', 'error')
            return render_template('login.html')
        
        # Login erfolgreich
        session['username'] = username
        
        # Letzten Login aktualisieren
        user['last_login'] = datetime.now().isoformat()
        users[username] = user
        save_users(users)
        
        flash('Erfolgreich angemeldet!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
@app.route('/admin/add-user', methods=['GET', 'POST'])
@admin_required
def register():
    """User-Registrierung (nur für Admins im Admin-Panel)"""
    if request.method == 'POST':
        # User-Details
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')
        
        # Validierung
        if not username or not password:
            flash('Benutzername und Passwort sind erforderlich.', 'error')
            return render_template('register.html')
        
        if len(username) < 3:
            flash('Benutzername muss mindestens 3 Zeichen lang sein.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Passwort muss mindestens 6 Zeichen lang sein.', 'error')
            return render_template('register.html')
        
        if password != password_confirm:
            flash('Passwörter stimmen nicht überein.', 'error')
            return render_template('register.html')
        
        # User-Daten laden
        users = load_users()
        
        # Prüfe ob Username bereits existiert
        if username in users:
            flash('Dieser Benutzername ist bereits vergeben.', 'error')
            return render_template('register.html')
        
        # Neuen User erstellen
        users[username] = {
            'username': username,
            'email': email or f"{username}@theodor-litt.local",
            'password_hash': generate_password_hash(password),
            'created': datetime.now().isoformat(),
            'last_login': None,
            'created_by_admin': session.get('admin_username', 'admin')
        }
        
        # Speichern
        if save_users(users):
            # VM-Umgebung erstellen
            if vm_manager.create_user_vms(username):
                flash(f'Benutzer "{username}" erfolgreich erstellt und VMs initialisiert!', 'success')
            else:
                flash(f'Benutzer erstellt, aber VM-Initialisierung fehlgeschlagen.', 'warning')
            
            return redirect(url_for('admin_panel'))
        else:
            flash('Fehler beim Speichern des Benutzers.', 'error')
    
    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Schüler-Dashboard mit VM-Controls"""
    username = session.get('username')
    users = load_users()
    user = users.get(username, {})
    
    # VM-Status abrufen
    vm_status = vm_manager.get_vm_status(username)
    
    return render_template('user_dashboard.html', 
                         username=username, 
                         user=user, 
                         vm_status=vm_status,
                         ssh_host=SSH_HOST)


@app.route('/logout')
def logout():
    """Logout (Schüler)"""
    session.pop('username', None)
    flash('Sie wurden abgemeldet.', 'info')
    return redirect(url_for('login'))


@app.route('/admin-logout')
def admin_logout():
    """Logout (Admin)"""
    session.pop('admin', None)
    session.pop('admin_username', None)
    flash('Admin-Logout erfolgreich.', 'info')
    return redirect(url_for('admin_login'))


# ============================================================================
# API Routes - VM-Management
# ============================================================================

@app.route('/api/vm/windows/start', methods=['POST'])
@login_required
def api_start_windows():
    """Startet Windows VM"""
    username = session.get('username')
    result = vm_manager.start_windows_vm(username)
    return jsonify(result)


@app.route('/api/vm/debian/start', methods=['POST'])
@login_required
def api_start_debian():
    """Startet Debian VM"""
    username = session.get('username')
    result = vm_manager.start_debian_vm(username)
    return jsonify(result)


@app.route('/api/vm/<vm_type>/stop', methods=['POST'])
@login_required
def api_stop_vm(vm_type):
    """Stoppt VM"""
    username = session.get('username')
    result = vm_manager.stop_vm(username, vm_type)
    return jsonify(result)


@app.route('/api/vm/<vm_type>/delete', methods=['POST'])
@login_required
def api_delete_vm(vm_type):
    """Löscht VM"""
    username = session.get('username')
    result = vm_manager.delete_vm(username, vm_type)
    return jsonify(result)


@app.route('/api/vm/status', methods=['GET'])
@login_required
def api_vm_status():
    """Gibt VM-Status zurück"""
    username = session.get('username')
    status = vm_manager.get_vm_status(username)
    return jsonify(status)


@app.route('/api/vscode/start', methods=['POST'])
@login_required
def api_start_vscode():
    """Startet VS Code Server"""
    username = session.get('username')
    result = vm_manager.start_vscode(username)
    return jsonify(result)


@app.route('/api/vscode/stop', methods=['POST'])
@login_required
def api_stop_vscode():
    """Stoppt VS Code Server"""
    username = session.get('username')
    result = vm_manager.stop_vm(username, 'vscode')
    return jsonify(result)


# ============================================================================
# Routes - Admin-Panel
# ============================================================================

@app.route('/admin')
@admin_required
def admin_panel():
    """Admin-Panel"""
    users = load_users()
    
    # VM-Status für alle User abrufen
    user_stats = {}
    for username in users.keys():
        vm_status = vm_manager.get_vm_status(username)
        user_stats[username] = vm_status
    
    return render_template('admin_panel.html', 
                         users=users,
                         user_stats=user_stats,
                         admin_username=session.get('admin_username'))


@app.route('/admin/user/<username>/delete', methods=['POST'])
@admin_required
def admin_delete_user(username):
    """Löscht User und alle VMs"""
    users = load_users()
    
    if username in users:
        # Erst alle VMs stoppen und löschen
        vm_manager.delete_vm(username, 'windows')
        vm_manager.delete_vm(username, 'debian')
        vm_manager.stop_vm(username, 'vscode')
        
        # User-Daten lokal löschen
        user_vm_path = os.path.join(LOCAL_VMS_PATH, username)
        if os.path.exists(user_vm_path):
            shutil.rmtree(user_vm_path)
            print(f"[ADMIN] ✓ User-VM-Daten gelöscht: {user_vm_path}")
        
        # User aus Liste entfernen
        del users[username]
        save_users(users)
        
        flash(f'Benutzer "{username}" und alle VMs gelöscht.', 'success')
    else:
        flash('Benutzer nicht gefunden.', 'error')
    
    return redirect(url_for('admin_panel'))


@app.route('/admin/user/<username>/reset-password', methods=['POST'])
@admin_required
def admin_reset_password(username):
    """Setzt Passwort zurück"""
    new_password = request.form.get('new_password', 'password123')
    
    users = load_users()
    
    if username in users:
        users[username]['password_hash'] = generate_password_hash(new_password)
        save_users(users)
        flash(f'Passwort für "{username}" zurückgesetzt: {new_password}', 'success')
    else:
        flash('Benutzer nicht gefunden.', 'error')
    
    return redirect(url_for('admin_panel'))


# ============================================================================
# Health Check
# ============================================================================

@app.route('/health')
def health():
    """Health Check für Monitoring"""
    # Prüfe SSH-Verbindung
    ssh = get_ssh_client()
    if ssh:
        ssh.close()
        return {"status": "healthy", "ssh": "connected"}, 200
    else:
        return {"status": "unhealthy", "ssh": "disconnected"}, 503


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("DockerLab - VM Management System")
    print("=" * 60)
    print(f"SSH-Server: {SSH_HOST}")
    print(f"VM-Management: Windows Server 2022 + Debian + VS Code")
    print(f"Max. gleichzeitige User: 10")
    print("=" * 60)
    
    # Erstelle lokales VM-Verzeichnis
    print(f"Erstelle VM-Datenverzeichnis: {LOCAL_VMS_PATH}")
    os.makedirs(LOCAL_VMS_PATH, exist_ok=True)
    print("✓ Verzeichnis bereit!")
    
    # Test SSH-Verbindung beim Start
    print("Teste SSH-Verbindung...")
    ssh = get_ssh_client()
    if ssh:
        print("✓ SSH-Verbindung erfolgreich!")
        ssh.close()
    else:
        print("✗ SSH-Verbindung fehlgeschlagen! Bitte Konfiguration prüfen.")
    
    print("=" * 60)
    print("Server startet auf http://localhost:3000")
    print("Admin-Login: http://localhost:3000/admin-login")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=3000, debug=True)
