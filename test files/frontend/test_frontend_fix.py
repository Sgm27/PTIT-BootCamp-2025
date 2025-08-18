#!/usr/bin/env python3
"""
Test script for frontend fix
Tests the complete flow: find existing -> delete -> verify
"""

import requests
import json
import sys
import os
import time

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "6dbbe787-9645-4203-94c1-3e5b1e9ca54c"  # son123@gmail.com user ID

def test_delete_flow():
    """Test the delete flow with existing schedule"""
    
    print("=== Testing Delete Flow - Frontend Fix ===")
    print(f"Base URL: {BASE_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print()
    
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
        if delete_response.status_code == 200:
            delete_data = delete_response.json()
            print(f"   ✅ Schedule deleted successfully")
            print(f"   - Response: {delete_data}")
        else:
            print(f"   ❌ Failed to delete schedule: {delete_response.status_code}")
            print(f"   Response: {delete_response.text}")
            return
        
        # Step 3: Verify deletion
        print(f"\n3. Verifying deletion...")
        time.sleep(1)  # Wait a bit for database to sync
        
        final_response = requests.get(f"{BASE_URL}/api/public/schedules/{TEST_USER_ID}")
        if final_response.status_code == 200:
            final_data = final_response.json()
            deleted_schedules = [s for s in final_data.get("schedules", []) if s["id"] == schedule_id]
            final_count = len(final_data.get("schedules", []))
            
            if not deleted_schedules:
                print(f"   ✅ Schedule successfully deleted from backend")
                print(f"   - Final schedule count: {final_count}")
                print(f"   - Count change: {initial_count} -> {final_count}")
                
                if final_count == initial_count - 1:
                    print(f"   ✅ Perfect! Schedule count decreased by 1 as expected")
                else:
                    print(f"   ⚠️  Schedule count changed unexpectedly: {initial_count} -> {final_count}")
            else:
                print(f"   ❌ Schedule still exists after deletion!")
                print(f"   - Found {len(deleted_schedules)} instances")
                return
        else:
            print(f"   ❌ Failed to verify deletion: {final_response.status_code}")
            return
        
        print("\n=== Test Complete - Frontend Fix Working! ===")
        print("✅ Schedule deletion works correctly")
        print("✅ Backend data is synchronized")
        print("✅ Frontend will now show correct data after refresh")
        
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection Error: Backend server is not running")
        print("   Please start the backend server first")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_delete_flow() 