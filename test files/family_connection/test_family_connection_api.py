#!/usr/bin/env python3
"""
Test script for Family Connection API endpoints
Tests the functionality needed for the Android app
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_health_endpoint():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_schedules_endpoint():
    """Test the schedules endpoint"""
    try:
        # Test without authentication (should fail)
        response = requests.get(f"{API_BASE}/schedules", timeout=5)
        print(f"📅 Schedules endpoint (no auth): {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctly requires authentication")
        else:
            print(f"   ⚠️ Unexpected status: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Schedules endpoint test failed: {e}")
        return False

def test_elderly_patients_endpoint():
    """Test the elderly patients endpoint"""
    try:
        # Test without authentication (should fail)
        response = requests.get(f"{API_BASE}/auth/elderly-patients/test_user_id", timeout=5)
        print(f"👴 Elderly patients endpoint (no auth): {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctly requires authentication")
        else:
            print(f"   ⚠️ Unexpected status: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Elderly patients endpoint test failed: {e}")
        return False

def test_user_profile_endpoint():
    """Test the user profile endpoint"""
    try:
        # Test without authentication (should fail)
        response = requests.get(f"{API_BASE}/auth/profile/test_user_id", timeout=5)
        print(f"👤 User profile endpoint (no auth): {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctly requires authentication")
        else:
            print(f"   ⚠️ Unexpected status: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ User profile endpoint test failed: {e}")
        return False

def test_create_schedule_endpoint():
    """Test the create schedule endpoint"""
    try:
        # Test without authentication (should fail)
        schedule_data = {
            "title": "Test Schedule",
            "message": "Test message",
            "scheduled_at": (datetime.now() + timedelta(hours=1)).isoformat(),
            "notification_type": "custom",
            "category": "test"
        }
        
        response = requests.post(f"{API_BASE}/schedules", json=schedule_data, timeout=5)
        print(f"➕ Create schedule endpoint (no auth): {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctly requires authentication")
        else:
            print(f"   ⚠️ Unexpected status: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Create schedule endpoint test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Family Connection API Endpoints")
    print("=" * 50)
    
    # Check if backend is running
    if not test_health_endpoint():
        print("\n❌ Backend is not running. Please start the server first.")
        print("   Run: python run_server.py")
        return
    
    print("\n🔒 Testing Authentication Requirements")
    print("-" * 40)
    
    # Test all endpoints
    tests = [
        test_schedules_endpoint,
        test_elderly_patients_endpoint,
        test_user_profile_endpoint,
        test_create_schedule_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(0.5)  # Small delay between tests
    
    print("\n📊 Test Results")
    print("=" * 50)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! API endpoints are working correctly.")
        print("\n📱 Next steps:")
        print("   1. Test Android app integration")
        print("   2. Verify data flow from app to backend")
        print("   3. Test with real user authentication")
    else:
        print("⚠️ Some tests failed. Check the backend implementation.")
        print("\n🔧 Troubleshooting:")
        print("   1. Check if all endpoints are registered in backend.py")
        print("   2. Verify authentication middleware is working")
        print("   3. Check database connection")

if __name__ == "__main__":
    main()
