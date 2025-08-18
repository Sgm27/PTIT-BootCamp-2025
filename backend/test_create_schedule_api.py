#!/usr/bin/env python3
"""
Test script to create a schedule via API
"""
import requests
import json
import time
from datetime import datetime, timedelta

# API Configuration
API_BASE = "http://localhost:8000"
TARGET_USER_ID = "6dbbe787-9645-4203-94c1-3e5b1e9ca54c"  # son123@gmail.com

def test_create_schedule():
    """Test creating a schedule via API"""
    
    print("=== Test Create Schedule API ===")
    
    # Create schedule data
    scheduled_time = datetime.now() + timedelta(hours=1)  # 1 hour from now
    scheduled_timestamp = int(scheduled_time.timestamp())
    
    schedule_data = {
        "elderly_id": TARGET_USER_ID,
        "title": f"Test Schedule - {datetime.now().strftime('%H:%M:%S')}",
        "message": "This is a test schedule created via API",
        "scheduled_at": scheduled_timestamp,
        "notification_type": "medicine_reminder",
        "category": "medicine",
        "priority": "normal",
        "created_by": TARGET_USER_ID
    }
    
    print(f"Creating schedule with data:")
    print(f"  - Title: {schedule_data['title']}")
    print(f"  - Message: {schedule_data['message']}")
    print(f"  - Scheduled At: {scheduled_time}")
    print(f"  - User ID: {TARGET_USER_ID}")
    
    try:
        # Make API request
        response = requests.post(
            f"{API_BASE}/api/schedules",
            json=schedule_data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=10
        )
        
        print(f"\nAPI Response:")
        print(f"  - Status Code: {response.status_code}")
        print(f"  - Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"  - Response Data: {json.dumps(response_data, indent=2)}")
            print(f"\n✅ Schedule created successfully!")
            return True
        else:
            print(f"  - Error Response: {response.text}")
            print(f"\n❌ Failed to create schedule. Status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection error: Could not connect to {API_BASE}")
        print("Make sure the backend server is running on port 8000")
        return False
    except requests.exceptions.Timeout:
        print(f"\n❌ Timeout error: Request took too long")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def test_get_user_schedules():
    """Test getting user schedules to verify the created schedule"""
    
    print("\n=== Test Get User Schedules ===")
    
    try:
        # Make API request
        response = requests.get(
            f"{API_BASE}/api/public/schedules/{TARGET_USER_ID}",
            headers={
                "Accept": "application/json"
            },
            timeout=10
        )
        
        print(f"API Response:")
        print(f"  - Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            schedules = response_data.get("schedules", [])
            print(f"  - Found {len(schedules)} schedules")
            
            if schedules:
                print(f"  - Latest schedule:")
                latest = schedules[0]
                print(f"    * ID: {latest.get('id')}")
                print(f"    * Title: {latest.get('title')}")
                print(f"    * Message: {latest.get('message')}")
                print(f"    * Scheduled At: {latest.get('scheduled_at')}")
                print(f"    * Category: {latest.get('category')}")
                print(f"    * Is Sent: {latest.get('is_sent')}")
            
            return True
        else:
            print(f"  - Error Response: {response.text}")
            print(f"\n❌ Failed to get schedules. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error getting schedules: {e}")
        return False

if __name__ == "__main__":
    print("Testing Schedule Creation and Retrieval")
    print("=" * 50)
    
    # Test creating a schedule
    success = test_create_schedule()
    
    if success:
        # Wait a moment for the database to update
        print("\nWaiting 2 seconds for database update...")
        time.sleep(2)
        
        # Test getting schedules to verify
        test_get_user_schedules()
    
    print("\n" + "=" * 50)
    print("Test completed!") 