#!/usr/bin/env python3
"""
Investor Meeting Demo Script
This script will help you quickly set up ngrok for your investor presentation
"""

import subprocess
import time


def check_ngrok_installed():
    """Check if ngrok is installed"""
    try:
        subprocess.run(["ngrok", "version"], capture_output=True, text=True)
        return True
    except FileNotFoundError:
        return False


def setup_ngrok_auth():
    """Setup ngrok authentication"""
    print("🔧 Ngrok Authentication Setup")
    print("=" * 40)
    print("You need to set up your ngrok authtoken.")
    print("\nQuick Setup:")
    print("1. Go to: https://dashboard.ngrok.com/signup")
    print("2. Sign up for a free account")
    print("3. Get your authtoken from: https://dashboard.ngrok.com/get-started/your-authtoken")
    print("4. Run the command below with your token:")
    print("\n   ngrok config add-authtoken YOUR_TOKEN_HERE")
    print("\nOr if you already have a token, just run:")
    print("   ngrok config add-authtoken YOUR_TOKEN")

    token = input("\nEnter your ngrok authtoken (or press Enter to skip): ").strip()

    if token:
        try:
            subprocess.run(["ngrok", "config", "add-authtoken", token], check=True)
            print("✅ Ngrok configured successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error configuring ngrok: {e}")
            return False
    else:
        print("⏭️  Skipping token setup. Make sure ngrok is configured manually.")
        return True


def start_ngrok_tunnel():
    """Start ngrok tunnel"""
    print("\n🚀 Starting ngrok tunnel...")
    print("=" * 40)

    try:
        # Start ngrok tunnel
        process = subprocess.Popen(["ngrok", "http", "8000"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Wait a moment for ngrok to start
        time.sleep(3)

        # Get the tunnel URL
        try:
            import requests

            response = requests.get("http://localhost:4040/api/tunnels")
            tunnels = response.json()

            if tunnels["tunnels"]:
                public_url = tunnels["tunnels"][0]["public_url"]
                print("✅ Ngrok tunnel is running!")
                print(f"🌐 Public URL: {public_url}")
                print("\n🎯 Investor Meeting URLs:")
                print(f"   • Main Demo: {public_url}/chat/")
                print(f"   • API Status: {public_url}/api/")
                print(f"   • Admin Panel: {public_url}/admin/")
                print(f"\n📱 Share this URL with investors: {public_url}/chat/")
                print("\nPress Ctrl+C to stop the tunnel")

                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Stopping tunnel...")
                    process.terminate()
                    print("✅ Tunnel stopped")

            else:
                print("❌ No tunnels found. Check ngrok status.")

        except Exception as e:
            print(f"❌ Error getting tunnel URL: {e}")
            print("Check ngrok status at: http://localhost:4040")

    except FileNotFoundError:
        print("❌ ngrok not found. Please install ngrok first:")
        print("   Download from: https://ngrok.com/download")
        print("   Or install via: choco install ngrok (Windows)")


def main():
    """Main function"""
    print("🎯 Hospitality AI Agent - Investor Demo")
    print("=" * 50)

    # Check if Django server is running
    print("📋 Prerequisites Check:")
    print("✅ Django server should be running on port 8000")
    print("✅ Make sure you ran: python manage.py runserver")

    # Check ngrok installation
    if not check_ngrok_installed():
        print("❌ ngrok not installed")
        print("📥 Download from: https://ngrok.com/download")
        print("   Or install via: choco install ngrok (Windows)")
        return

    print("✅ ngrok is installed")

    # Setup authentication
    if not setup_ngrok_auth():
        return

    # Start tunnel
    start_ngrok_tunnel()


if __name__ == "__main__":
    main()
