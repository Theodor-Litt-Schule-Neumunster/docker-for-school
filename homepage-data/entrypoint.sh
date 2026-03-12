#!/bin/bash
set -e

echo "=== DockerLab Homepage startet ==="

# Stelle sicher, dass data-Verzeichnis existiert
mkdir -p /data

echo "✓ Daten-Verzeichnis: /data"
echo "Starte Flask-Anwendung..."
exec python app.py
