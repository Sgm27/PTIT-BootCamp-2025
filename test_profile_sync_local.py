#!/usr/bin/env python3
"""
Simple test for Profile Update API endpoint
"""

import requests
import json

# Use local server for testing
BASE_URL = "http://localhost:8000"

def test_profile_update_api():
    """Test the new profile update endpoint"""
    print("🧪 Testing Profile Update API")
    print("=" * 40)
    
    # Test data
    test_user = {
        "user_type": "elderly",
        "full_name": "Test User",
        "email": "test@example.com",
        "phone": "+84123456789",
        "password": "test123",
        "address": "Test Address"
    }
    
    try:
        # Step 1: Register user
        print("1️⃣ Registering test user...")
        register_response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=test_user,
            timeout=5
        )
        
        if register_response.status_code != 200:
            print(f"❌ Registration failed: {register_response.status_code}")
            print(f"Response: {register_response.text}")
            return
        
        register_data = register_response.json()
        user_id = register_data["user"]["user_id"]
        print(f"✅ User registered. ID: {user_id}")
        
        # Step 2: Test profile update
        print("\n2️⃣ Testing profile update...")
        update_data = {
            "full_name": "Updated Test User",
            "email": "updated@example.com",
            "phone": "+84987654321",
            "address": "Updated Address"
        }
        
        update_response = requests.put(
            f"{BASE_URL}/api/auth/profile/{user_id}",
            json=update_data,
            timeout=5
        )
        
        print(f"Update response status: {update_response.status_code}")
        print(f"Update response: {update_response.text}")
        
        if update_response.status_code == 200:
            print("✅ Profile update API is working!")
        else:
            print("❌ Profile update API failed")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {BASE_URL}")
        print("   Start the server with: cd backend && python run_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_profile_update_api() 