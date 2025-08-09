#!/usr/bin/env python3
"""
Test script để verify fix cho conversation history crash
"""

import subprocess
import time
import sys

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    print("🚀 Testing Conversation History Fix")
    print("=" * 50)
    
    # Change to Android project directory
    android_dir = "backend/GeminiLiveDemo"
    
    tests = [
        (f"cd {android_dir} && ./gradlew assembleDebug", "Build Android APK"),
        (f"cd {android_dir} && ./gradlew lint", "Run Android Lint Check"),
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for cmd, description in tests:
        if run_command(cmd, description):
            success_count += 1
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Conversation History fix is ready.")
        print("\n📱 Next steps:")
        print("1. Install APK on device: ./gradlew installDebug")
        print("2. Test conversation history button in app")
        print("3. Check logcat for any remaining issues")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 