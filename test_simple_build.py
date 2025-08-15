#!/usr/bin/env python3
"""
Simple script to test Android app build
"""
import subprocess
import os

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        print(f"🔧 Running: {command}")
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Success!")
            return True
        else:
            print(f"❌ Failed!")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🏗️  Building Android App...")
    
    android_dir = "backend/GeminiLiveDemo"
    
    if not os.path.exists(android_dir):
        print(f"❌ Directory {android_dir} not found")
        return
    
    # Try to build
    if run_command("./gradlew assembleDebug", cwd=android_dir):
        print("✅ Build successful!")
        print("📱 APK should be in: app/build/outputs/apk/debug/")
    else:
        print("❌ Build failed!")

if __name__ == "__main__":
    main() 