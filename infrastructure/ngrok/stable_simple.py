#!/usr/bin/env python3
"""
Simple, stable ngrok script that minimizes restarts
"""
import subprocess
import time
import sys
import signal

class StableNgrok:
    def __init__(self):
        self.ngrok_process = None
        self.running = True

    def signal_handler(self, signum, frame):
        print("\n[STOP] Received interrupt signal...")
        self.running = False
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
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

    def kill_existing_ngrok(self):
        """Kill any existing ngrok processes"""
        try:
            subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"],
                          capture_output=True, check=False)
            time.sleep(3)
        except:
            pass

    def start_ngrok(self):
        """Start ngrok with minimal configuration to reduce restarts"""
        try:
            self.kill_existing_ngrok()

            print("[START] Starting stable ngrok tunnel...")

            # Use minimal ngrok configuration to reduce restarts
            self.ngrok_process = subprocess.Popen([
                "ngrok", "http", "8000",
                "--log=stdout",
                "--log-level=info",
                "--region=us"  # Use US region for stability
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            print("[OK] Ngrok started with PID:", self.ngrok_process.pid)
            print("[INFO] Check http://127.0.0.1:4040 for the public URL")
            print("[INFO] The custom middleware will handle host validation automatically")
            print("[INFO] Press Ctrl+C to stop")

            # Keep the process running
            try:
                while self.running:
                    time.sleep(1)

                    # Check if process is still running
                    if self.ngrok_process.poll() is not None:
                        print("[ERROR] Ngrok process died, restarting...")
                        time.sleep(5)
                        return self.start_ngrok()

            except KeyboardInterrupt:
                pass

        except FileNotFoundError:
            print("[ERROR] ngrok not found. Please install ngrok first.")
            print("[INFO] Download from: https://ngrok.com/download")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to start ngrok: {e}")
            return False
        finally:
            self.cleanup()

if __name__ == "__main__":
    ngrok = StableNgrok()
    ngrok.start_ngrok()
