#!/usr/bin/env python3
import time
import subprocess
import sys
import os

def kill_existing_ngrok():
    """Kill any existing ngrok processes"""
    try:
        subprocess.run(["taskkill", "/f", "/im", "ngrok.exe"],
                      capture_output=True, check=False)
        time.sleep(2)
    except:
        pass

def start_ngrok():
    """Start ngrok using the command line directly"""
    try:
        # Kill existing processes first
        kill_existing_ngrok()

        # Start ngrok using command line
        process = subprocess.Popen([
            "ngrok", "http", "8000", "--log=stdout"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        print("[OK] Ngrok started with PID:", process.pid)
        print("[INFO] Check http://127.0.0.1:4040 for the public URL")
        print("[INFO] Press Ctrl+C to stop")

        # Keep the process running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[STOP] Stopping ngrok...")
            process.terminate()
            process.wait()
            print("[OK] Ngrok stopped")

    except FileNotFoundError:
        print("[ERROR] ngrok not found. Please install ngrok first.")
        print("[INFO] Download from: https://ngrok.com/download")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to start ngrok: {e}")
        return False

if __name__ == "__main__":
    start_ngrok()
