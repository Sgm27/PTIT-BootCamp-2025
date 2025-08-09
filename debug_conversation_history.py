#!/usr/bin/env python3
"""
Debug script for conversation history feature
"""
import subprocess
import os
import time
import threading

def run_command(command, cwd=None, timeout=None):
    """Run a command and return the result"""
    try:
        print(f"🔧 Running: {command}")
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            print(f"✅ Success!")
            return True, result.stdout
        else:
            print(f"❌ Failed!")
            print(f"Error: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout!")
        return False, "Command timed out"
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, str(e)

def monitor_logs():
    """Monitor Android logs in real-time"""
    print("📋 Starting log monitor...")
    try:
        # Clear logcat first
        subprocess.run("adb logcat -c", shell=True, capture_output=True)
        
        # Monitor logs
        process = subprocess.Popen(
            "adb logcat | grep -E '(MainActivity|ConversationHistory|ApiClient|ApiConfig)'",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print("📱 Monitoring logs (press Ctrl+C to stop):")
        print("-" * 80)
        
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line.strip())
                
    except KeyboardInterrupt:
        print("\n📋 Log monitoring stopped")
        process.terminate()
    except Exception as e:
        print(f"❌ Error monitoring logs: {e}")

def main():
    print("=" * 60)
    print("🐛 CONVERSATION HISTORY DEBUG SCRIPT")
    print("=" * 60)
    
    android_dir = "backend/GeminiLiveDemo"
    
    if not os.path.exists(android_dir):
        print(f"❌ Directory {android_dir} not found")
        return
    
    # Check if device is connected
    success, output = run_command("adb devices")
    if not success or "device" not in output:
        print("⚠️  No Android device connected")
        print("Please connect your device and enable USB debugging")
        return
    
    print("📱 Device connected!")
    
    # Build app
    print("\n🏗️  Building app...")
    success, output = run_command("./gradlew assembleDebug", cwd=android_dir, timeout=300)
    
    if not success:
        print("❌ Build failed!")
        return
    
    # Install app
    print("\n📲 Installing app...")
    success, output = run_command("./gradlew installDebug", cwd=android_dir, timeout=60)
    
    if not success:
        print("❌ Installation failed!")
        return
    
    print("✅ App installed successfully!")
    
    # Start log monitoring in a separate thread
    log_thread = threading.Thread(target=monitor_logs, daemon=True)
    log_thread.start()
    
    print("\n" + "=" * 60)
    print("🎯 MANUAL TESTING INSTRUCTIONS")
    print("=" * 60)
    print("1. Open the app on your device")
    print("2. Tap on 'Lịch sử trò chuyện' button")
    print("3. Watch the logs above for any errors")
    print("4. Press Ctrl+C to stop log monitoring")
    print("=" * 60)
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🏁 Debug session ended")

if __name__ == "__main__":
    main() 