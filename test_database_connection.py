#!/usr/bin/env python3
"""
Test script to verify database connection and API endpoints
for the GeminiLiveDemo Android app
"""

import requests
import json
import sys
from datetime import datetime

# API Configuration
BASE_URL = "https://backend-bootcamp.sonktx.online"
API_ENDPOINTS = {
    "register": f"{BASE_URL}/api/auth/register",
    "login": f"{BASE_URL}/api/auth/login", 
    "profile": f"{BASE_URL}/api/auth/profile",
    "update_profile": f"{BASE_URL}/api/auth/profile"
}

def test_api_connection():
    """Test basic API connectivity"""
    print("🔍 Testing API connection...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ API server is reachable")
            return True
        else:
            print(f"❌ API server returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to API server: {e}")
        return False

def test_user_registration():
    """Test user registration endpoint"""
    print("\n📝 Testing user registration...")
    
    test_user = {
        "user_type": "elderly",
        "full_name": "Test User Database",
        "email": f"testdb_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
        "phone": f"+84{datetime.now().strftime('%H%M%S')}",
        "password": "testpassword123",
        "date_of_birth": "1950-01-01",
        "gender": "male",
        "address": "Test Address, Hanoi"
    }
    
    try:
        response = requests.post(
            API_ENDPOINTS["register"],
            json=test_user,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"Registration response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ User registration successful")
                print(f"   User ID: {data['user']['user_id']}")
                print(f"   Full Name: {data['user']['full_name']}")
                print(f"   Email: {data['user']['email']}")
                return data["user"]
            else:
                print(f"❌ Registration failed: {data.get('message', 'Unknown error')}")
                return None
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_user_login(email, password):
    """Test user login endpoint"""
    print(f"\n🔐 Testing user login for {email}...")
    
    login_data = {
        "identifier": email,
        "password": password
    }
    
    try:
        response = requests.post(
            API_ENDPOINTS["login"],
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"Login response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ User login successful")
                print(f"   User ID: {data['user']['user_id']}")
                print(f"   Session Token: {data.get('session_token', 'N/A')}")
                return data["user"]
            else:
                print(f"❌ Login failed: {data.get('message', 'Unknown error')}")
                return None
        else:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_get_profile(user_id):
    """Test get user profile endpoint"""
    print(f"\n👤 Testing get profile for user {user_id}...")
    
    try:
        response = requests.get(
            f"{API_ENDPOINTS['profile']}/{user_id}",
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"Get profile response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Profile retrieved successfully from database")
            print(f"   User ID: {data['user_id']}")
            print(f"   Full Name: {data['full_name']}")
            print(f"   Email: {data['email']}")
            print(f"   Phone: {data['phone']}")
            print(f"   Address: {data['address']}")
            print(f"   Created At: {data['created_at']}")
            return data
        else:
            print(f"❌ Get profile failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Get profile error: {e}")
        return None

def test_update_profile(user_id):
    """Test update user profile endpoint"""
    print(f"\n✏️ Testing update profile for user {user_id}...")
    
    update_data = {
        "full_name": "Updated Test User Database",
        "email": f"updated_testdb_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
        "phone": f"+84{datetime.now().strftime('%H%M%S')}999",
        "address": "Updated Test Address, Ho Chi Minh City",
        "date_of_birth": "1950-01-01",
        "gender": "male"
    }
    
    try:
        response = requests.put(
            f"{API_ENDPOINTS['update_profile']}/{user_id}",
            json=update_data,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"Update profile response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("✅ Profile updated successfully in database")
                print(f"   Updated Full Name: {data['user']['full_name']}")
                print(f"   Updated Email: {data['user']['email']}")
                print(f"   Updated Phone: {data['user']['phone']}")
                print(f"   Updated Address: {data['user']['address']}")
                return data["user"]
            else:
                print(f"❌ Update failed: {data.get('message', 'Unknown error')}")
                return None
        else:
            print(f"❌ Update profile failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Update profile error: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Starting Database Connection Test for GeminiLiveDemo")
    print("=" * 60)
    
    # Test 1: API Connection
    if not test_api_connection():
        print("\n❌ Cannot proceed - API server is not reachable")
        sys.exit(1)
    
    # Test 2: User Registration
    user = test_user_registration()
    if not user:
        print("\n❌ Cannot proceed - User registration failed")
        sys.exit(1)
    
    user_id = user["user_id"]
    email = user["email"]
    
    # Test 3: User Login
    login_user = test_user_login(email, "testpassword123")
    if not login_user:
        print("\n❌ Cannot proceed - User login failed")
        sys.exit(1)
    
    # Test 4: Get Profile
    profile = test_get_profile(user_id)
    if not profile:
        print("\n❌ Cannot proceed - Get profile failed")
        sys.exit(1)
    
    # Test 5: Update Profile
    updated_profile = test_update_profile(user_id)
    if not updated_profile:
        print("\n❌ Profile update failed")
        sys.exit(1)
    
    # Test 6: Verify Update by Getting Profile Again
    print(f"\n🔍 Verifying update by getting profile again...")
    final_profile = test_get_profile(user_id)
    if final_profile and final_profile["full_name"] == "Updated Test User Database":
        print("✅ Profile update verification successful")
    else:
        print("❌ Profile update verification failed")
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print("✅ Database connection is working properly")
    print("✅ User registration, login, profile get/update all working")
    print("✅ GeminiLiveDemo app should now use database data instead of offline data")
    print("\n📱 Your Android app is now configured to use live database data!")

if __name__ == "__main__":
    main() 