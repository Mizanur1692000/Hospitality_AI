#!/usr/bin/env python3
import subprocess
import time
import sys
import signal
import threading
import os

class AppManager:
    def __init__(self):
        self.django_process = None
        self.ngrok_process = None
        self.running = True

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
            self.ngrok_process = subprocess.Popen([
                sys.executable, "scripts/stable_ngrok.py"
            ], cwd=os.getcwd())
            print("[OK] Ngrok tunnel started")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to start ngrok: {e}")
            return False

    def monitor_processes(self):
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

                time.sleep(10)  # Check every 10 seconds

            except Exception as e:
                print(f"[ERROR] Monitor error: {e}")
                time.sleep(5)

    def run(self):
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        print("=== Hospitality AI Agent Startup ===")
        print("Starting Django server and ngrok tunnel...")

        # Start Django
        if not self.start_django():
            print("[FAIL] Could not start Django server")
            return

        # Wait a moment for Django to start
        time.sleep(3)

        # Start ngrok
        if not self.start_ngrok():
            print("[FAIL] Could not start ngrok tunnel")
            self.cleanup()
            return

        print("\n=== Services Started ===")
        print("Django: http://127.0.0.1:8000/")
        print("Check ngrok terminal for public URL")
        print("Press Ctrl+C to stop all services")

        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
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
    app_manager = AppManager()
    app_manager.run()
