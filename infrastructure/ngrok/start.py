#!/usr/bin/env python3
import time

from pyngrok import ngrok

# Start the tunnel
tunnel = ngrok.connect(8000)
print("[OK] Ngrok tunnel created!")
print(f"[WEB] Public URL: {tunnel.public_url}")
print(f"[CHAT] Your business partner can access: {tunnel.public_url}/chat/")
print(f"[API] API endpoint: {tunnel.public_url}/chat/api/")
print("\nPress Ctrl+C to stop the tunnel")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[STOP] Stopping tunnel...")
    ngrok.disconnect(tunnel.public_url)
    print("[OK] Tunnel stopped")
