#!/usr/bin/env python3
"""
Script to build and test Android app conversation history feature
"""
import subprocess
import os
import time

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        print(f"🔧 Running: {command}")
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print(f"✅ Success: {command}")
            if result.stdout:
                print(f"Output: {result.stdout[:500]}...")
        else:
            print(f"❌ Failed: {command}")
            print(f"Error: {result.stderr}")
            
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print(f"⏰ Timeout: {command}")
        return False, "", "Command timed out"
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, "", str(e)

def check_android_setup():
    """Check if Android development environment is set up"""
    print("🔍 Checking Android development environment...")
    
    # Check if gradlew exists
    gradlew_path = "backend/GeminiLiveDemo/gradlew.bat"
    if os.path.exists(gradlew_path):
        print("✅ Gradle wrapper found")
        return True
    else:
        print("❌ Gradle wrapper not found")
        return False

def build_app():
    """Build the Android app"""
    print("🏗️  Building Android app...")
    
    android_dir = "backend/GeminiLiveDemo"
    
    # Clean build
    success, stdout, stderr = run_command("./gradlew clean", cwd=android_dir)
    if not success:
        print("❌ Clean failed")
        return False
    
    # Build debug APK
    success, stdout, stderr = run_command("./gradlew assembleDebug", cwd=android_dir)
    if not success:
        print("❌ Build failed")
        print(f"Build error: {stderr}")
        return False
    
    print("✅ App built successfully")
    return True

def check_adb():
    """Check if ADB is available and device is connected"""
    print("🔍 Checking ADB and device connection...")
    
    success, stdout, stderr = run_command("adb devices")
    if not success:
        print("❌ ADB not found or not working")
        return False
    
    if "device" in stdout and not stdout.count("device") == 1:
        print("✅ Device connected")
        return True
    else:
        print("⚠️  No device connected")
        print("Available devices:")
        print(stdout)
        return False

def install_app():
    """Install the app on connected device"""
    print("📱 Installing app...")
    
    android_dir = "backend/GeminiLiveDemo"
    
    success, stdout, stderr = run_command("./gradlew installDebug", cwd=android_dir)
    if not success:
        print("❌ Installation failed")
        print(f"Install error: {stderr}")
        return False
    
    print("✅ App installed successfully")
    return True

def get_app_logs():
    """Get app logs from logcat"""
    print("📋 Getting app logs...")
    
    # Clear logcat first
    run_command("adb logcat -c")
    
    print("📱 App logs (last 50 lines):")
    success, stdout, stderr = run_command("adb logcat -d | grep -E '(ConversationHistory|MainActivity|ApiClient)' | tail -50")
    
    if stdout:
        print(stdout)
    else:
        print("No relevant logs found")

def main():
    """Main function"""
    print("=" * 60)
    print("🧪 ANDROID APP CONVERSATION HISTORY TEST")
    print("=" * 60)
    
    # Check Android setup
    if not check_android_setup():
        print("❌ Android development environment not set up properly")
        return
    
    # Build app
    if not build_app():
        print("❌ Failed to build app")
        return
    
    # Check ADB and device
    device_connected = check_adb()
    
    if device_connected:
        # Install app
        if install_app():
            print("\n✅ App installed successfully!")
            print("\n📱 Manual testing steps:")
            print("1. Open the app on your device")
            print("2. Login or use test user data")
            print("3. Tap on 'Lịch sử trò chuyện' button")
            print("4. Check if app crashes or works properly")
            
            print("\n📋 To view logs in real-time, run:")
            print("adb logcat | grep -E '(ConversationHistory|MainActivity|ApiClient)'")
            
            # Wait a bit and get initial logs
            time.sleep(2)
            get_app_logs()
        else:
            print("❌ Failed to install app")
    else:
        print("⚠️  No device connected. App built but not installed.")
        print("To install manually:")
        print("1. Connect your Android device")
        print("2. Enable USB debugging")
        print("3. Run: cd backend/GeminiLiveDemo && ./gradlew installDebug")
    
    print("\n" + "=" * 60)
    print("🏁 TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main() 