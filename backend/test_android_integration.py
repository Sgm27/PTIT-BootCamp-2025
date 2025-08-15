#!/usr/bin/env python3
"""
Android App Integration Test Script
Tests the integration between Android app and backend API
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_backend_availability():
    """Test if backend is accessible"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is accessible")
            return True
        else:
            print(f"❌ Backend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

def test_api_endpoints():
    """Test all required API endpoints"""
    endpoints = [
        ("Health Check", f"{BASE_URL}/health", "GET"),
        ("API Documentation", f"{BASE_URL}/docs", "GET"),
        ("Schedules API", f"{API_BASE}/schedules", "GET"),
    ]
    
    print("\n🔍 Testing API Endpoints")
    print("-" * 40)
    
    results = []
    for name, url, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, timeout=5)
            
            status = "✅" if response.status_code < 400 else "⚠️"
            print(f"{status} {name}: {response.status_code}")
            
            if response.status_code < 400:
                results.append(True)
            else:
                results.append(False)
                
        except Exception as e:
            print(f"❌ {name}: {e}")
            results.append(False)
    
    return results

def test_authentication_flow():
    """Test authentication flow (without real credentials)"""
    print("\n🔐 Testing Authentication Flow")
    print("-" * 40)
    
    # Test protected endpoints without auth
    protected_endpoints = [
        ("Schedules", f"{API_BASE}/schedules"),
        ("User Profile", f"{API_BASE}/auth/profile/test_user"),
        ("Elderly Patients", f"{API_BASE}/auth/elderly-patients/test_user"),
    ]
    
    results = []
    for name, url in protected_endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 401:
                print(f"✅ {name}: Correctly requires authentication")
                results.append(True)
            else:
                print(f"⚠️ {name}: Unexpected status {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {name}: {e}")
            results.append(False)
    
    return results

def test_schedule_creation():
    """Test schedule creation (without auth)"""
    print("\n📅 Testing Schedule Creation")
    print("-" * 40)
    
    schedule_data = {
        "title": "Test Medicine Reminder",
        "message": "Take blood pressure medication",
        "scheduled_at": (datetime.now() + timedelta(hours=1)).isoformat(),
        "notification_type": "medicine_reminder",
        "category": "medicine",
        "priority": "high"
    }
    
    try:
        response = requests.post(f"{API_BASE}/schedules", json=schedule_data, timeout=5)
        if response.status_code == 401:
            print("✅ Schedule creation: Correctly requires authentication")
            return True
        else:
            print(f"⚠️ Schedule creation: Unexpected status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Schedule creation: {e}")
        return False

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n📊 Integration Test Report")
    print("=" * 50)
    
    # Test backend availability
    backend_ok = test_backend_availability()
    
    if not backend_ok:
        print("\n❌ Backend is not available. Please start the server first.")
        print("   Run: python start_backend.py")
        return
    
    # Test API endpoints
    api_results = test_api_endpoints()
    api_success = sum(api_results)
    api_total = len(api_results)
    
    # Test authentication
    auth_results = test_authentication_flow()
    auth_success = sum(auth_results)
    auth_total = len(auth_results)
    
    # Test schedule creation
    schedule_ok = test_schedule_creation()
    
    # Summary
    print("\n📈 Test Summary")
    print("-" * 30)
    print(f"Backend Availability: {'✅' if backend_ok else '❌'}")
    print(f"API Endpoints: {api_success}/{api_total} ✅")
    print(f"Authentication: {auth_success}/{auth_total} ✅")
    print(f"Schedule Creation: {'✅' if schedule_ok else '❌'}")
    
    # Overall status
    total_tests = 1 + api_total + auth_total + 1
    passed_tests = (1 if backend_ok else 0) + api_success + auth_success + (1 if schedule_ok else 0)
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Backend is ready for Android app integration.")
        print("\n📱 Next steps:")
        print("   1. Build and install Android app")
        print("   2. Test login functionality")
        print("   3. Test family connection feature")
        print("   4. Verify data synchronization")
    else:
        print("⚠️ Some tests failed. Check the backend implementation.")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify all endpoints are registered in backend.py")
        print("   2. Check database connection")
        print("   3. Verify authentication middleware")
        print("   4. Check server logs for errors")

def main():
    """Main function"""
    print("🧪 Android App Integration Test")
    print("=" * 50)
    print("Testing backend API endpoints and authentication")
    print("Required for Android app family connection feature")
    print()
    
    generate_test_report()

if __name__ == "__main__":
    main() 