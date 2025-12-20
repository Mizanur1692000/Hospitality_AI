#!/usr/bin/env python3
"""
Complete startup script that manages Django + ngrok with automatic host updates
"""
import subprocess
import time
import sys
import signal
import threading
import os
import requests
import re
from pathlib import Path

class AutoHostManager:
    def __init__(self):
        self.django_process = None
        self.ngrok_process = None
        self.running = True
        self.last_hostname = None

    def signal_handler(self, signum, frame):
        print("\n[SHUTDOWN] Received interrupt signal...")
        self.running = False
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        print("[CLEANUP] Stopping services...")

        if self.ngrok_process:
            try:
                self.ngrok_process.terminate()
                self.ngrok_process.wait(timeout=5)
                print("[OK] Ngrok stopped")
            except:
                try:
                    self.ngrok_process.kill()
                except:
                    pass

        if self.django_process:
            try:
                self.django_process.terminate()
                self.django_process.wait(timeout=5)
                print("[OK] Django stopped")
            except:
                try:
                    self.django_process.kill()
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

    def restart_django(self):
        """Restart Django server"""
        print("[RESTART] Restarting Django server...")

        if self.django_process:
            try:
                self.django_process.terminate()
                self.django_process.wait(timeout=5)
            except:
                try:
                    self.django_process.kill()
                except:
                    pass

        time.sleep(2)
        return self.start_django()

    def start_django(self):
        print("[START] Starting Django server...")
        try:
            self.django_process = subprocess.Popen([
                sys.executable, "manage.py", "runserver"
            ], cwd=os.getcwd())
            print("[OK] Django server started")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to start Django: {e}")
            return False

    def start_ngrok(self):
        print("[START] Starting ngrok tunnel...")
        try:
            # Kill existing ngrok processes
            subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"],
                          capture_output=True, check=False)
            time.sleep(2)

            self.ngrok_process = subprocess.Popen([
                "ngrok", "http", "8000", "--log=stdout"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("[OK] Ngrok tunnel started")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to start ngrok: {e}")
            return False

    def monitor_services(self):
        """Monitor Django and ngrok, handle host updates"""
        while self.running:
            try:
                # Check Django
                if self.django_process and self.django_process.poll() is not None:
                    print("[RESTART] Django process died, restarting...")
                    if not self.start_django():
                        print("[ERROR] Failed to restart Django")
                        break

                # Check ngrok
                if self.ngrok_process and self.ngrok_process.poll() is not None:
                    print("[RESTART] Ngrok process died, restarting...")
                    if not self.start_ngrok():
                        print("[ERROR] Failed to restart ngrok")
                        break

                # Check for ngrok URL changes
                current_hostname = self.get_ngrok_url()
                if current_hostname and current_hostname != self.last_hostname:
                    print(f"[DETECTED] New ngrok hostname: {current_hostname}")
                    if self.update_django_settings(current_hostname):
                        print("[RESTART] Restarting Django to apply host changes...")
                        self.restart_django()
                        self.last_hostname = current_hostname
                        print(f"[SUCCESS] Django restarted with new host: {current_hostname}")

                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                print(f"[ERROR] Monitor error: {e}")
                time.sleep(5)

    def run(self):
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        print("=== Hospitality AI Agent - Auto Host Manager ===")
        print("Starting Django server and ngrok tunnel with automatic host updates...")

        # Start Django
        if not self.start_django():
            print("[FAIL] Could not start Django server")
            return

        # Wait for Django to start
        time.sleep(3)

        # Start ngrok
        if not self.start_ngrok():
            print("[FAIL] Could not start ngrok tunnel")
            self.cleanup()
            return

        # Wait for ngrok to initialize
        time.sleep(5)

        # Get initial ngrok URL and update Django
        initial_hostname = self.get_ngrok_url()
        if initial_hostname:
            print(f"[DETECTED] Initial ngrok URL: https://{initial_hostname}")
            if self.update_django_settings(initial_hostname):
                print("[RESTART] Restarting Django with initial host...")
                self.restart_django()
                self.last_hostname = initial_hostname
                print(f"[SUCCESS] Django restarted with host: {initial_hostname}")

        print("\n=== Services Started ===")
        print("Django: http://127.0.0.1:8000/")
        if initial_hostname:
            print(f"Public: https://{initial_hostname}/")
            print(f"Chat: https://{initial_hostname}/chat/")
        print("Auto host updates: ENABLED")
        print("Press Ctrl+C to stop all services")

        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_services, daemon=True)
        monitor_thread.start()

        try:
            # Keep main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

if __name__ == "__main__":
    manager = AutoHostManager()
    manager.run()
