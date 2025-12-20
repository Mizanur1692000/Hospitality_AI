#!/usr/bin/env python3
"""
Smart ngrok script that automatically updates Django ALLOWED_HOSTS
"""
import time
import subprocess
import sys
import os
import requests
import re
from pathlib import Path

class SmartNgrok:
    def __init__(self):
        self.ngrok_process = None
        self.last_hostname = None

    def kill_existing_ngrok(self):
        """Kill any existing ngrok processes"""
        try:
            subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"],
                          capture_output=True, check=False)
            time.sleep(2)
        except:
            pass

    def get_ngrok_url(self):
        """Get the current ngrok public URL"""
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('tunnels'):
                    public_url = data['tunnels'][0]['public_url']
                    hostname = public_url.replace('https://', '').replace('http://', '')
                    return hostname
        except:
            pass
        return None

    def update_django_settings(self, ngrok_hostname):
        """Update Django settings.py to include the ngrok hostname"""
        settings_path = Path("hospitality_ai_backend/settings.py")

        if not settings_path.exists():
            return False

        try:
            with open(settings_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if hostname already exists
            if ngrok_hostname in content:
                return True

            # Pattern to match ALLOWED_HOSTS line
            pattern = r'ALLOWED_HOSTS\s*=\s*env\.list\("DJANGO_ALLOWED_HOSTS",\s*default=\[([^\]]*)\]\)'

            def replace_allowed_hosts(match):
                current_hosts = match.group(1)
                hosts = []
                if current_hosts.strip():
                    hosts = [h.strip().strip('"\'') for h in current_hosts.split(',')]

                if ngrok_hostname not in hosts:
                    hosts.append(ngrok_hostname)

                hosts_str = ', '.join([f'"{h}"' for h in hosts])
                return f'ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[{hosts_str}])'

            new_content = re.sub(pattern, replace_allowed_hosts, content)

            with open(settings_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"[UPDATE] Added {ngrok_hostname} to ALLOWED_HOSTS")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to update settings: {e}")
            return False

    def start_ngrok(self):
        """Start ngrok and monitor for URL changes"""
        try:
            self.kill_existing_ngrok()

            print("[START] Starting ngrok...")
            self.ngrok_process = subprocess.Popen([
                "ngrok", "http", "8000", "--log=stdout"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            print("[OK] Ngrok started with PID:", self.ngrok_process.pid)
            print("[INFO] Waiting for ngrok to initialize...")

            # Wait for ngrok to start
            time.sleep(5)

            # Get initial URL and update Django
            hostname = self.get_ngrok_url()
            if hostname:
                print(f"[DETECTED] Ngrok URL: https://{hostname}")
                if self.update_django_settings(hostname):
                    print("[SUCCESS] Django settings updated")
                    print("[IMPORTANT] Restart Django server to apply changes:")
                    print("           python manage.py runserver")
                else:
                    print("[WARNING] Could not update Django settings")
                self.last_hostname = hostname
            else:
                print("[WARNING] Could not get ngrok URL")

            print("\n[INFO] Monitoring for URL changes...")
            print("[INFO] Press Ctrl+C to stop")

            # Monitor for URL changes
            while True:
                time.sleep(10)

                current_hostname = self.get_ngrok_url()
                if current_hostname and current_hostname != self.last_hostname:
                    print(f"[CHANGE] Ngrok URL changed to: https://{current_hostname}")
                    if self.update_django_settings(current_hostname):
                        print("[UPDATE] Django settings updated")
                        print("[IMPORTANT] Restart Django server to apply changes")
                    self.last_hostname = current_hostname

                # Check if ngrok process is still running
                if self.ngrok_process.poll() is not None:
                    print("[ERROR] Ngrok process died, restarting...")
                    return self.start_ngrok()

        except KeyboardInterrupt:
            print("\n[STOP] Stopping ngrok...")
            if self.ngrok_process:
                self.ngrok_process.terminate()
                self.ngrok_process.wait()
            print("[OK] Ngrok stopped")
        except FileNotFoundError:
            print("[ERROR] ngrok not found. Please install ngrok first.")
            print("[INFO] Download from: https://ngrok.com/download")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to start ngrok: {e}")
            return False

if __name__ == "__main__":
    ngrok = SmartNgrok()
    ngrok.start_ngrok()
