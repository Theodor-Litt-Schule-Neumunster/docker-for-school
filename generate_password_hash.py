#!/usr/bin/env python3
"""
Hilfsskript: Passwort-Hash für Admin-Credentials generieren
Verwendung: python generate_password_hash.py
"""

from werkzeug.security import generate_password_hash
import sys

def main():
    print("=" * 60)
    print("Admin Passwort-Hash Generator")
    print("Für sichere admin_credentials.yml")
    print("=" * 60)
    print()
    
    # Passwort eingeben
    try:
        password = input("Geben Sie das Passwort ein: ").strip()
        
        if not password:
            print("❌ Fehler: Passwort darf nicht leer sein!")
            sys.exit(1)
        
        if len(password) < 8:
            print("⚠️  WARNUNG: Passwort ist sehr kurz! Empfohlen: mindestens 8 Zeichen")
        
        # Hash generieren
        password_hash = generate_password_hash(password)
        
        print()
        print("✅ Passwort-Hash erfolgreich generiert!")
        print()
        print("-" * 60)
        print("Kopieren Sie diesen Hash in admin_credentials.yml:")
        print("-" * 60)
        print()
        print(f'password_hash: "{password_hash}"')
        print()
        print("-" * 60)
        print()
        print("Beispiel admin_credentials.yml:")
        print()
        print("admins:")
        print("  - username: \"ihr_username\"")
        print(f"    password_hash: \"{password_hash}\"")
        print("    email: \"ihre@email.de\"")
        print()
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nAbgebrochen.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
