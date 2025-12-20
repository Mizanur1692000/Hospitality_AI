#!/usr/bin/env python3
"""
Quick Ngrok Setup for Investor Meeting
This script will help you expose your Django server via ngrok
"""

import time

from pyngrok import ngrok


def quick_ngrok_setup():
    """Quick setup for ngrok tunnel"""
    print("🚀 Quick Ngrok Setup for Investor Meeting")
    print("=" * 50)

    # Check if authtoken is already set
    try:
        # Try to create a tunnel without setting authtoken (uses existing config)
        tunnel = ngrok.connect(8000)
        print("✅ Ngrok tunnel created successfully!")
        print(f"🌐 Public URL: {tunnel.public_url}")
        print(f"📱 Chat Interface: {tunnel.public_url}/chat/")
        print(f"🔗 API Endpoints: {tunnel.public_url}/api/")
        print(f"📊 Admin Panel: {tunnel.public_url}/admin/")
        print("\n🎯 For your investor meeting, share these URLs:")
        print(f"   • Main Demo: {tunnel.public_url}/chat/")
        print(f"   • API Status: {tunnel.public_url}/api/")
        print("\nPress Ctrl+C to stop the tunnel")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping tunnel...")
            ngrok.disconnect(tunnel.public_url)
            print("✅ Tunnel stopped")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 To fix this, you need to:")
        print("1. Sign up at: https://dashboard.ngrok.com/signup")
        print("2. Get your authtoken at: https://dashboard.ngrok.com/get-started/your-authtoken")
        print("3. Run: ngrok config add-authtoken YOUR_TOKEN")
        print("\nOr if you already have ngrok installed, run:")
        print("ngrok http 8000")


if __name__ == "__main__":
    quick_ngrok_setup()
