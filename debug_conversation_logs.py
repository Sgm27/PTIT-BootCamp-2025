#!/usr/bin/env python3
"""
Script để monitor logs khi debug conversation history
"""
import subprocess
import sys
import time
import threading

def monitor_logs():
    """Monitor Android logs for conversation history debugging"""
    print("🔍 Monitoring Android Logs for Conversation History Debug")
    print("=" * 60)
    print("📱 Instructions:")
    print("1. Make sure your Android device/emulator is connected")
    print("2. Install and open the app")
    print("3. Click on 'Lịch sử trò chuyện' button")
    print("4. Watch the logs below for debugging info")
    print("=" * 60)
    
    # Clear existing logs
    try:
        subprocess.run(["adb", "logcat", "-c"], check=True)
        print("✅ Cleared existing logs")
    except subprocess.CalledProcessError:
        print("⚠️  Could not clear logs (adb might not be available)")
    except FileNotFoundError:
        print("❌ ADB not found. Please make sure Android SDK is installed and adb is in PATH")
        return
    
    # Monitor specific tags
    tags = [
        "ConversationHistory",
        "ConversationAdapter", 
        "ApiClient",
        "MainActivity"
    ]
    
    # Create filter for logcat
    filter_args = []
    for tag in tags:
        filter_args.extend(["-s", f"{tag}:D"])
    
    try:
        print(f"\n🚀 Starting log monitoring for tags: {', '.join(tags)}")
        print("Press Ctrl+C to stop monitoring")
        print("-" * 60)
        
        # Start logcat process
        process = subprocess.Popen(
            ["adb", "logcat"] + filter_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Read logs line by line
        for line in process.stdout:
            line = line.strip()
            if line:
                # Color code important messages
                if "ERROR" in line or "EXCEPTION" in line:
                    print(f"🔴 {line}")
                elif "START" in line or "COMPLETED" in line:
                    print(f"🟢 {line}")
                elif "API CALL" in line or "HTTP RESPONSE" in line:
                    print(f"🔵 {line}")
                elif "USER ID" in line or "LOGIN" in line:
                    print(f"🟡 {line}")
                else:
                    print(f"⚪ {line}")
                    
    except KeyboardInterrupt:
        print("\n\n⏹️  Log monitoring stopped by user")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"\n❌ Error monitoring logs: {e}")

def check_device_connection():
    """Check if Android device is connected"""
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        devices = [line for line in lines if line.strip() and 'device' in line]
        
        if devices:
            print(f"✅ Found {len(devices)} connected device(s):")
            for device in devices:
                print(f"   📱 {device}")
            return True
        else:
            print("❌ No Android devices connected")
            print("💡 Please connect your device or start an emulator")
            return False
    except FileNotFoundError:
        print("❌ ADB not found in PATH")
        print("💡 Please install Android SDK and add adb to your PATH")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking devices: {e}")
        return False

def main():
    print("🐛 Android Conversation History Debug Tool")
    print("=" * 50)
    
    # Check device connection
    if not check_device_connection():
        return False
    
    print("\n" + "=" * 50)
    print("📋 Debug Checklist:")
    print("1. ✅ Device connected")
    print("2. 🔄 Install app: ./gradlew installDebug")
    print("3. 📱 Open app and try conversation history")
    print("4. 👀 Watch logs below for issues")
    print("=" * 50)
    
    # Start monitoring
    monitor_logs()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0) 