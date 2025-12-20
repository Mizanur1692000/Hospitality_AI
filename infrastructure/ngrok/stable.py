#!/usr/bin/env python3
import time
import sys
import signal
from pyngrok import ngrok

class StableNgrok:
    def __init__(self, port=8000):
        self.port = port
        self.tunnel = None
        self.running = True

    def signal_handler(self, signum, frame):
        print("\n[STOP] Received interrupt signal, shutting down...")
        self.running = False
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        if self.tunnel:
            try:
                ngrok.disconnect(self.tunnel.public_url)
                print("[OK] Tunnel disconnected")
            except Exception as e:
                print(f"[WARN] Error disconnecting tunnel: {e}")

    def start_tunnel(self):
        try:
            # Kill any existing ngrok processes first
            import subprocess
            try:
                subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"],
                             capture_output=True, check=False)
                time.sleep(2)
            except:
                pass

            # Start new tunnel
            self.tunnel = ngrok.connect(self.port)
            print("[OK] Ngrok tunnel created!")
            print(f"[WEB] Public URL: {self.tunnel.public_url}")
            print(f"[CHAT] Chat interface: {self.tunnel.public_url}/chat/")
            print(f"[API] API endpoint: {self.tunnel.public_url}/chat/api/")
            print("\nPress Ctrl+C to stop the tunnel")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to create tunnel: {e}")
            return False

    def run(self):
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        while self.running:
            if not self.tunnel:
                if not self.start_tunnel():
                    print("[RETRY] Retrying in 10 seconds...")
                    time.sleep(10)
                    continue

            try:
                # Check if tunnel is still alive
                import requests
                response = requests.get(self.tunnel.public_url, timeout=5)
                if response.status_code != 200:
                    print("[WARN] Tunnel appears to be down, restarting...")
                    self.cleanup()
                    self.tunnel = None
                    continue

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                print(f"[WARN] Tunnel check failed: {e}")
                print("[RESTART] Restarting tunnel...")
                self.cleanup()
                self.tunnel = None
                time.sleep(5)

        self.cleanup()

if __name__ == "__main__":
    ngrok_manager = StableNgrok(8000)
    ngrok_manager.run()
