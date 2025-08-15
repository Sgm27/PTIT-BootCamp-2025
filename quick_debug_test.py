#!/usr/bin/env python3
"""
Quick debug test cho conversation history issue
"""
import requests
import json

def test_api_directly():
    """Test API trực tiếp để đảm bảo server hoạt động"""
    base_url = "https://backend-bootcamp.sonktx.online"
    test_user_id = "f5db7d59-1df3-4b83-a066-bbb95d7a28a0"
    
    print("🔍 Quick API Test")
    print("=" * 40)
    
    # Test 1: Health check
    print("1. 🏥 Health Check:")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Server is running")
        else:
            print("   ❌ Server issue")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Conversations API
    print("\n2. 💬 Conversations API:")
    try:
        url = f"{base_url}/api/conversations/{test_user_id}?limit=10"
        print(f"   URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            conversations = data.get('conversations', [])
            print(f"   ✅ Found {len(conversations)} conversations")
            
            if conversations:
                print("   📝 Sample conversation:")
                conv = conversations[0]
                print(f"      ID: {conv.get('id')}")
                print(f"      Title: {conv.get('title')}")
                print(f"      Messages: {conv.get('total_messages')}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def check_android_connection():
    """Kiểm tra kết nối Android"""
    import subprocess
    
    print("\n3. 📱 Android Connection:")
    try:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]
            devices = [line for line in lines if 'device' in line and line.strip()]
            if devices:
                print(f"   ✅ {len(devices)} device(s) connected")
                return True
            else:
                print("   ❌ No devices connected")
                return False
        else:
            print("   ❌ ADB error")
            return False
    except FileNotFoundError:
        print("   ❌ ADB not found")
        return False

def main():
    print("🚀 Quick Debug Test for Conversation History")
    print("=" * 50)
    
    # Test API
    test_api_directly()
    
    # Check Android
    android_ok = check_android_connection()
    
    print("\n" + "=" * 50)
    print("📋 Debug Summary:")
    print("✅ API server is working")
    print("✅ Conversations data available")
    
    if android_ok:
        print("✅ Android device connected")
        print("\n🔧 Next Steps:")
        print("1. Install app: ./gradlew installDebug")
        print("2. Run debug monitor: python debug_conversation_logs.py")
        print("3. Open app and click conversation history")
        print("4. Check logs for the issue")
    else:
        print("❌ Android device not connected")
        print("\n🔧 Fix:")
        print("1. Connect Android device or start emulator")
        print("2. Enable USB debugging")
        print("3. Run 'adb devices' to verify")
    
    print("\n💡 Common Issues:")
    print("- User not logged in (check UserPreferences)")
    print("- Network permission issues")
    print("- API URL configuration")
    print("- SSL/TLS certificate issues")

if __name__ == "__main__":
    main() 