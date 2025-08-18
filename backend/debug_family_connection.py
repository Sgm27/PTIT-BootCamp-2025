#!/usr/bin/env python3
"""
Debug script to test family connection API endpoints
"""
import requests
import json
from datetime import datetime

# Backend server URL
BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    """Test all relevant API endpoints for family connection"""
    
    print("=== Testing Family Connection API Endpoints ===\n")
    
    # Test 1: Check if server is running
    print("1. Testing server connectivity...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print(f"⚠️ Server responded with status: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Check schedules endpoint without auth (should fail)
    print("\n2. Testing schedules endpoint without authentication...")
    try:
        response = requests.get(f"{BASE_URL}/api/schedules", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly requires authentication")
        elif response.status_code == 200:
            print("⚠️ Endpoint accessible without auth (security issue)")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
            except:
                print(f"Raw response: {response.text[:200]}...")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error testing schedules endpoint: {e}")
    
    # Test 3: Check elderly patients endpoint without auth
    print("\n3. Testing elderly patients endpoint without authentication...")
    try:
        # Use a dummy family user ID
        dummy_family_id = "f5db7d59-1df3-4b83-a066-bbb95d7a28a0"  # From our database
        response = requests.get(f"{BASE_URL}/api/auth/elderly-patients/{dummy_family_id}", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctly requires authentication")
        elif response.status_code == 200:
            print("⚠️ Endpoint accessible without auth (security issue)")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
            except:
                print(f"Raw response: {response.text[:200]}...")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error testing elderly patients endpoint: {e}")
    
    # Test 4: Check if we can get user info
    print("\n4. Testing user info endpoints...")
    try:
        # Try to get user by email
        response = requests.get(f"{BASE_URL}/api/auth/users/email/son123@gmail.com", timeout=5)
        print(f"User endpoint status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"User data: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}...")
            except:
                print(f"Raw response: {response.text[:300]}...")
        else:
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Error testing user endpoint: {e}")
    
    # Test 5: Check database directly
    print("\n5. Checking database directly...")
    try:
        from db.db_config import get_db
        from db.models import User, Notification
        
        with get_db() as session:
            # Check elderly user
            elderly_user = session.query(User).filter(User.email == "son123@gmail.com").first()
            if elderly_user:
                print(f"✅ Elderly user found: {elderly_user.full_name} (ID: {elderly_user.id})")
                
                # Check notifications
                notifications = session.query(Notification).filter(
                    Notification.user_id == elderly_user.id
                ).all()
                print(f"✅ Found {len(notifications)} notifications in database")
                
                for notif in notifications:
                    status = "COMPLETED" if notif.is_sent else "PENDING"
                    print(f"  - {notif.title} ({notif.notification_type}) - {notif.scheduled_at} - {status}")
            else:
                print("❌ Elderly user not found in database")
                
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    
    print("\n=== Debug Summary ===")
    print("If the API endpoints require authentication (401 status), then the Android app")
    print("needs to include proper authentication headers when making requests.")
    print("\nThe database contains the schedule data, but the API calls are failing")
    print("due to missing authentication.")

if __name__ == "__main__":
    test_api_endpoints() 