#!/usr/bin/env python3
"""
Test script for delete schedule functionality
Tests the DELETE /api/schedules/{schedule_id} endpoint with user_id parameter
"""

import requests
import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "6dbbe787-9645-4203-94c1-3e5b1e9ca54c"  # son123@gmail.com user ID

def test_delete_schedule():
    """Test the delete schedule endpoint"""
    
    print("=== Testing Delete Schedule Functionality ===")
    print(f"Base URL: {BASE_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print()
    
    # First, let's get the list of schedules to find one to delete
    print("1. Getting user schedules...")
    try:
        response = requests.get(f"{BASE_URL}/api/public/schedules/{TEST_USER_ID}")
        if response.status_code == 200:
            data = response.json()
            schedules = data.get("schedules", [])
            print(f"   Found {len(schedules)} schedules")
            
            if schedules:
                # Use the first schedule for testing
                test_schedule = schedules[0]
                schedule_id = test_schedule["id"]
                schedule_title = test_schedule["title"]
                print(f"   Using schedule: {schedule_title} (ID: {schedule_id})")
                
                # Test delete with user_id parameter
                print("\n2. Testing delete schedule with user_id parameter...")
                delete_url = f"{BASE_URL}/api/schedules/{schedule_id}?user_id={TEST_USER_ID}"
                print(f"   DELETE URL: {delete_url}")
                
                delete_response = requests.delete(delete_url)
                print(f"   Response Status: {delete_response.status_code}")
                print(f"   Response Body: {delete_response.text}")
                
                if delete_response.status_code == 200:
                    print("   ✅ SUCCESS: Schedule deleted successfully!")
                    
                    # Verify deletion by trying to get the schedule again
                    print("\n3. Verifying deletion...")
                    verify_response = requests.get(f"{BASE_URL}/api/public/schedules/{TEST_USER_ID}")
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        remaining_schedules = verify_data.get("schedules", [])
                        remaining_count = len([s for s in remaining_schedules if s["id"] == schedule_id])
                        
                        if remaining_count == 0:
                            print("   ✅ VERIFICATION SUCCESS: Schedule no longer exists in list")
                        else:
                            print(f"   ❌ VERIFICATION FAILED: Schedule still exists ({remaining_count} instances)")
                    else:
                        print(f"   ⚠️  Could not verify deletion: {verify_response.status_code}")
                        
                else:
                    print("   ❌ FAILED: Could not delete schedule")
                    print(f"   Error: {delete_response.text}")
                    
            else:
                print("   No schedules found to test deletion")
                
        else:
            print(f"   ❌ Failed to get schedules: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection Error: Backend server is not running")
        print("   Please start the backend server first")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n=== Test Complete ===")

def test_mark_schedule_complete():
    """Test the mark schedule complete endpoint"""
    
    print("\n=== Testing Mark Schedule Complete Functionality ===")
    
    # First, let's get the list of schedules to find one to mark complete
    print("1. Getting user schedules...")
    try:
        response = requests.get(f"{BASE_URL}/api/public/schedules/{TEST_USER_ID}")
        if response.status_code == 200:
            data = response.json()
            schedules = data.get("schedules", [])
            print(f"   Found {len(schedules)} schedules")
            
            if schedules:
                # Find a schedule that's not completed
                incomplete_schedules = [s for s in schedules if not s.get("is_sent", False)]
                
                if incomplete_schedules:
                    test_schedule = incomplete_schedules[0]
                    schedule_id = test_schedule["id"]
                    schedule_title = test_schedule["title"]
                    print(f"   Using incomplete schedule: {schedule_title} (ID: {schedule_id})")
                    
                    # Test mark complete with user_id parameter
                    print("\n2. Testing mark schedule complete with user_id parameter...")
                    complete_url = f"{BASE_URL}/api/schedules/{schedule_id}/complete?user_id={TEST_USER_ID}"
                    print(f"   POST URL: {complete_url}")
                    
                    complete_response = requests.post(complete_url)
                    print(f"   Response Status: {complete_response.status_code}")
                    print(f"   Response Body: {complete_response.text}")
                    
                    if complete_response.status_code == 200:
                        print("   ✅ SUCCESS: Schedule marked as complete!")
                    else:
                        print("   ❌ FAILED: Could not mark schedule as complete")
                        print(f"   Error: {complete_response.text}")
                else:
                    print("   No incomplete schedules found to test")
                    
        else:
            print(f"   ❌ Failed to get schedules: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection Error: Backend server is not running")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    print("Delete Schedule API Test")
    print("=" * 50)
    
    # Test delete functionality
    test_delete_schedule()
    
    # Test mark complete functionality
    test_mark_schedule_complete()
    
    print("\nAll tests completed!") 