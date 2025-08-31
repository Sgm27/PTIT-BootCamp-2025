#!/usr/bin/env python3
"""
Test API endpoint with authentication
"""

import requests
import json
from datetime import datetime

# Backend server URL
BASE_URL = "http://localhost:8000"

def test_api_with_auth():
    """Test API endpoints with authentication"""
    
    print("=== Testing API with Authentication ===\n")
    
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
    
    # Test 2: Try to get schedules with user_id parameter
    print("\n2. Testing schedules endpoint with user_id parameter...")
    try:
        # Use the elderly user ID we know exists
        elderly_user_id = "dd8d892b-fa77-4a71-9520-71baf601c3ba"
        
        # Try different ways to pass user_id
        urls_to_test = [
            f"{BASE_URL}/api/schedules?user_id={elderly_user_id}",
            f"{BASE_URL}/api/schedules?user_id={elderly_user_id}&limit=100",
            f"{BASE_URL}/api/schedules"
        ]
        
        for i, url in enumerate(urls_to_test):
            print(f"\n   Testing URL {i+1}: {url}")
            try:
                response = requests.get(url, timeout=5)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        schedules_count = len(data.get("schedules", []))
                        print(f"   ✅ Success! Found {schedules_count} schedules")
                        
                        if schedules_count > 0:
                            print(f"   First schedule: {data['schedules'][0].get('title', 'N/A')}")
                        else:
                            print(f"   ⚠️ Empty schedules array: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
                            
                    except Exception as e:
                        print(f"   ❌ Error parsing response: {e}")
                        print(f"   Raw response: {response.text[:200]}...")
                        
                elif response.status_code == 401:
                    print("   ✅ Correctly requires authentication")
                else:
                    print(f"   ⚠️ Unexpected status: {response.status_code}")
                    print(f"   Response: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   ❌ Error testing URL: {e}")
                
    except Exception as e:
        print(f"❌ Error testing schedules endpoint: {e}")
    
    # Test 3: Check if there's a way to bypass auth
    print("\n3. Checking for auth bypass...")
    try:
        # Try to see if there are any public endpoints
        response = requests.get(f"{BASE_URL}/api/schedules", timeout=5)
        if response.status_code == 200:
            print("⚠️ Endpoint accessible without auth - this is a security issue")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}...")
            except:
                print(f"Raw response: {response.text[:300]}...")
        else:
            print(f"✅ Endpoint properly protected: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking auth bypass: {e}")
    
    # Test 4: Check database directly again
    print("\n4. Verifying database data...")
    try:
        from db.db_config import get_db
        from db.models import User, Notification
        
        with get_db() as session:
            elderly_user = session.query(User).filter(User.email == "son123@gmail.com").first()
            if elderly_user:
                notifications = session.query(Notification).filter(
                    Notification.user_id == elderly_user.id
                ).all()
                print(f"✅ Database has {len(notifications)} notifications")
                
                # Show first few
                for i, notif in enumerate(notifications[:3]):
                    status = "COMPLETED" if notif.is_sent else "PENDING"
                    print(f"  {i+1}. {notif.title} ({notif.notification_type}) - {notif.scheduled_at} - {status}")
                
                if len(notifications) > 3:
                    print(f"  ... and {len(notifications) - 3} more")
            else:
                print("❌ Elderly user not found in database")
                
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    
    print("\n=== Analysis ===")
    print("If the API returns empty schedules but database has data,")
    print("the issue is likely in the API logic or authentication.")
    print("\nThe Android app needs to either:")
    print("1. Include proper authentication headers")
    print("2. Use a different endpoint that doesn't require auth")
    print("3. The backend needs to be restarted to pick up model changes")

if __name__ == "__main__":
    test_api_with_auth() 