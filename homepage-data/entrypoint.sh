#!/bin/bash
set -e

echo "=== DockerLab Homepage startet ==="

# Neues HOME-Verzeichnis mit SSH-Keys (beschreibbar)
export HOME="/tmp/dockerlab-home"
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

# SSH-Keys vom read-only Mount kopieren
if [ -d "/root/.ssh" ] && [ -n "$(ls -A /root/.ssh 2>/dev/null | head -n 1)" ]; then
  echo "Kopiere SSH-Keys von /root/.ssh nach $HOME/.ssh..."
  cp -r /root/.ssh/* "$HOME/.ssh/" 2>/dev/null || true
  chmod 600 "$HOME/.ssh"/id_* 2>/dev/null || true
  chmod 644 "$HOME/.ssh"/*.pub 2>/dev/null || true
  echo "✓ SSH-Keys erfolgreich kopiert nach $HOME/.ssh"
else
  echo "WARNUNG: Keine SSH-Keys gefunden im Mount!"
  echo "Bitte SSH-Keys in Docker-Compose korrekt mounten."
fi

# Host-Key akzeptieren
if [ -n "$SSH_REMOTE_HOST" ]; then
  echo "Akzeptiere SSH-Host-Key für $SSH_REMOTE_HOST..."
  mkdir -p "$HOME/.ssh"
  touch "$HOME/.ssh/known_hosts"
  ssh-keyscan -H "$SSH_REMOTE_HOST" >> "$HOME/.ssh/known_hosts" 2>/dev/null || true
fi

# SSH-Verbindung testen (optional, nicht blockierend)
if [ -n "$SSH_REMOTE_HOST" ] && [ -n "$SSH_REMOTE_USER" ]; then
  echo "Teste SSH-Verbindung zu $SSH_REMOTE_USER@$SSH_REMOTE_HOST..."
  if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no \
     "$SSH_REMOTE_USER@$SSH_REMOTE_HOST" "echo OK" 2>/dev/null; then
    echo "✓ SSH-Verbindung erfolgreich!"
  else
    echo "⚠ SSH-Verbindung fehlgeschlagen (wird bei Bedarf erneut versucht)"
  fi
fi

echo "Starte Flask-Anwendung..."
exec python app.py
