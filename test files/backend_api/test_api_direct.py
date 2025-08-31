#!/usr/bin/env python3
"""
Test API endpoint directly
"""

import requests
import time

def test_api_direct():
    """Test API endpoint directly"""
    
    print("=== Testing API Endpoint Directly ===")
    
    BASE_URL = "http://localhost:8000"
    TEST_USER_ID = "dd8d892b-fa77-4a71-9520-71baf601c3ba"
    
    try:
        # Step 1: Get current schedules
        print("1. Getting current schedules...")
        response = requests.get(f"{BASE_URL}/api/public/schedules/{TEST_USER_ID}")
        if response.status_code == 200:
            data = response.json()
            schedules = data.get("schedules", [])
            initial_count = len(schedules)
            print(f"   ✅ Found {initial_count} schedules initially")
            
            if initial_count == 0:
                print("   ❌ No schedules found to test deletion")
                return
            
            # Use the first schedule for testing
            test_schedule = schedules[0]
            schedule_id = test_schedule["id"]
            schedule_title = test_schedule["title"]
            print(f"   Using schedule: {schedule_title} (ID: {schedule_id})")
            
        else:
            print(f"   ❌ Failed to get schedules: {response.status_code}")
            return
        
        # Step 2: Delete the test schedule
        print(f"\n2. Deleting test schedule...")
        delete_response = requests.delete(f"{BASE_URL}/api/schedules/{schedule_id}?user_id={TEST_USER_ID}")
        print(f"   Delete response status: {delete_response.status_code}")
        print(f"   Delete response body: {delete_response.text}")
        
        if delete_response.status_code == 200:
            delete_data = delete_response.json()
            print(f"   ✅ Schedule deleted successfully")
            print(f"   - Response: {delete_data}")
        else:
            print(f"   ❌ Failed to delete schedule: {delete_response.status_code}")
            print(f"   Response: {delete_response.text}")
            return
        
        # Step 3: Verify deletion immediately
        print(f"\n3. Verifying deletion immediately...")
        time.sleep(1)  # Wait a bit
        
        final_response = requests.get(f"{BASE_URL}/api/public/schedules/{TEST_USER_ID}")
        if final_response.status_code == 200:
            final_data = final_response.json()
            deleted_schedules = [s for s in final_data.get("schedules", []) if s["id"] == schedule_id]
            final_count = len(final_data.get("schedules", []))
            
            if not deleted_schedules:
                print(f"   ✅ Schedule successfully deleted from backend")
                print(f"   - Final schedule count: {final_count}")
                print(f"   - Count change: {initial_count} -> {final_count}")
            else:
                print(f"   ❌ Schedule still exists after deletion!")
                print(f"   - Found {len(deleted_schedules)} instances")
                print(f"   - Schedule details: {deleted_schedules[0]}")
        else:
            print(f"   ❌ Failed to verify deletion: {final_response.status_code}")
            return
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection Error: Backend server is not running")
        print("   Please start the backend server first")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_direct() 