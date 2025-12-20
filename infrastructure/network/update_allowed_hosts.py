#!/usr/bin/env python3
"""
Script to automatically update Django ALLOWED_HOSTS with current ngrok URL
"""
import re
import time
import requests
import os
from pathlib import Path

def get_ngrok_url():
    """Get the current ngrok public URL"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('tunnels'):
                public_url = data['tunnels'][0]['public_url']
                # Extract hostname from URL (remove https://)
                hostname = public_url.replace('https://', '').replace('http://', '')
                return hostname
    except Exception as e:
        print(f"[WARN] Could not get ngrok URL: {e}")
    return None

def update_django_settings(ngrok_hostname):
    """Update Django settings.py to include the ngrok hostname"""
    settings_path = Path("hospitality_ai_backend/settings.py")

    if not settings_path.exists():
        print("[ERROR] Django settings.py not found")
        return False

    try:
        # Read current settings
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if ALLOWED_HOSTS already contains the hostname
        if ngrok_hostname in content:
            print(f"[INFO] Hostname {ngrok_hostname} already in ALLOWED_HOSTS")
            return True

        # Pattern to match ALLOWED_HOSTS line
        pattern = r'ALLOWED_HOSTS\s*=\s*env\.list\("DJANGO_ALLOWED_HOSTS",\s*default=\[([^\]]*)\]\)'

        def replace_allowed_hosts(match):
            current_hosts = match.group(1)
            # Parse existing hosts
            hosts = []
            if current_hosts.strip():
                # Remove quotes and split by comma
                hosts = [h.strip().strip('"\'') for h in current_hosts.split(',')]

            # Add ngrok hostname if not already present
            if ngrok_hostname not in hosts:
                hosts.append(ngrok_hostname)

            # Format the new hosts list
            hosts_str = ', '.join([f'"{h}"' for h in hosts])
            return f'ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[{hosts_str}])'

        # Replace the ALLOWED_HOSTS line
        new_content = re.sub(pattern, replace_allowed_hosts, content)

        # Write back to file
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"[SUCCESS] Added {ngrok_hostname} to ALLOWED_HOSTS")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to update settings: {e}")
        return False

def monitor_ngrok_and_update():
    """Monitor ngrok and update Django settings when URL changes"""
    last_hostname = None

    print("[START] Monitoring ngrok for hostname changes...")

    while True:
        try:
            current_hostname = get_ngrok_url()

            if current_hostname and current_hostname != last_hostname:
                print(f"[DETECTED] New ngrok hostname: {current_hostname}")

                if update_django_settings(current_hostname):
                    print("[RESTART] Please restart Django server to apply changes")
                    print(f"[INFO] Run: python manage.py runserver")
                    last_hostname = current_hostname
                else:
                    print("[ERROR] Failed to update Django settings")

            time.sleep(10)  # Check every 10 seconds

        except KeyboardInterrupt:
            print("\n[STOP] Monitoring stopped")
            break
        except Exception as e:
            print(f"[ERROR] Monitor error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # One-time update mode
        hostname = get_ngrok_url()
        if hostname:
            update_django_settings(hostname)
        else:
            print("[ERROR] Could not get ngrok hostname")
    else:
        # Continuous monitoring mode
        monitor_ngrok_and_update()
