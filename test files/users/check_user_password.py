#!/usr/bin/env python3
"""
Check user password for son123@gmail.com
"""

import requests
import json

def check_user_password():
    """Check if user son123@gmail.com exists and test passwords"""
    base_url = "https://backend.vcaremind.io.vn"
    auth_url = f"{base_url}/api/auth/login"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Common passwords to test
    passwords = [
        "123456",
        "password",
        "123456789",
        "admin",
        "user123",
        "test123",
        "123123",
        "qwerty",
        "password123",
        "12345678"
    ]
    
    print("🔍 CHECKING USER PASSWORD")
    print("=" * 50)
    print(f"👤 User: son123@gmail.com")
    print(f"🌐 URL: {auth_url}")
    print("=" * 50)
    
    for i, password in enumerate(passwords, 1):
        print(f"\n🧪 Test #{i:02d}: Password = '{password}'")
        
        login_payload = {
            "identifier": "son123@gmail.com",
            "password": password
        }
        
        try:
            response = requests.post(
                auth_url,
                json=login_payload,
                headers=headers,
                timeout=10
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("✅ LOGIN SUCCESSFUL!")
                    print(f"👤 User ID: {result.get('user', {}).get('user_id')}")
                    print(f"👤 Name: {result.get('user', {}).get('full_name')}")
                    print(f"📧 Email: {result.get('user', {}).get('email')}")
                    print(f"🔑 Session Token: {result.get('session_token', '')[:20]}...")
                    return password, result
                else:
                    print(f"❌ Login failed: {result.get('message')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                if response.status_code == 401:
                    print("   - Invalid credentials")
                elif response.status_code == 404:
                    print("   - User not found")
                else:
                    print(f"   - Response: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("❌ NO VALID PASSWORD FOUND")
    print("=" * 50)
    return None, None

def create_test_user():
    """Create test user if it doesn't exist"""
    base_url = "https://backend.vcaremind.io.vn"
    register_url = f"{base_url}/api/auth/register"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("\n🔧 CREATING TEST USER")
    print("=" * 50)
    
    register_payload = {
        "user_type": "elderly",
        "full_name": "Test User Son",
        "email": "son123@gmail.com",
        "phone": "0123456789",
        "password": "123456",
        "date_of_birth": "1980-01-01",
        "gender": "male",
        "address": "Test Address"
    }
    
    try:
        response = requests.post(
            register_url,
            json=register_payload,
            headers=headers,
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ USER CREATED SUCCESSFULLY!")
                print(f"👤 User ID: {result.get('user', {}).get('user_id')}")
                print(f"👤 Name: {result.get('user', {}).get('full_name')}")
                print(f"📧 Email: {result.get('user', {}).get('email')}")
                return True
            else:
                print(f"❌ Creation failed: {result.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    # First try to find existing user
    password, user_data = check_user_password()
    
    if password:
        print(f"\n🎉 FOUND VALID PASSWORD: '{password}'")
        print("You can now use this password in the voice test script.")
    else:
        print("\n❌ No valid password found. Trying to create user...")
        if create_test_user():
            print("\n✅ User created. Now try running the voice test again.")
        else:
            print("\n❌ Failed to create user. Please check the backend.") 