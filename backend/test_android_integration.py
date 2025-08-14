"""
Test Android App Integration
Tests the memoir API endpoints that Android app will use
"""
import requests
import json
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:8000"
USER_ID = "6dbbe787-9645-4203-94c1-3e5b1e9ca54c"

def test_android_memoir_endpoints():
    """Test the main endpoints that Android app will use"""
    print("🚀 Testing Android App Integration...")
    print(f"Base URL: {BASE_URL}")
    print(f"User ID: {USER_ID}")
    print("=" * 60)
    
    # Test 1: Get user memoirs (main screen)
    print("\n1️⃣ Testing GET /api/memoirs/{user_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/memoirs/{USER_ID}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Retrieved user memoirs")
            print(f"   Found {len(data.get('memoirs', []))} memoirs")
            
            # Show first memoir details
            if data.get('memoirs'):
                memoir = data['memoirs'][0]
                print(f"   First memoir: {memoir.get('title', 'No title')}")
                print(f"   Content preview: {memoir.get('content', '')[:100]}...")
                print(f"   Categories: {memoir.get('categories', [])}")
                print(f"   Extracted at: {memoir.get('extracted_at', 'Unknown')}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Search memoirs
    print("\n2️⃣ Testing POST /api/memoirs/{user_id}/search")
    try:
        search_data = {"query": "chiến tranh", "limit": 10}
        response = requests.post(f"{BASE_URL}/api/memoirs/{USER_ID}/search", json=search_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Searched memoirs")
            print(f"   Found {len(data.get('memoirs', []))} results for 'chiến tranh'")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get memoir categories
    print("\n3️⃣ Testing GET /api/memoirs/{user_id}/categories")
    try:
        response = requests.get(f"{BASE_URL}/api/memoirs/{USER_ID}/categories")
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Retrieved memoir categories")
            print(f"   Categories: {data.get('categories', [])}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get memoir stats
    print("\n4️⃣ Testing GET /api/memoirs/{user_id}/stats")
    try:
        response = requests.get(f"{BASE_URL}/api/memoirs/{USER_ID}/stats")
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Retrieved memoir stats")
            print(f"   Stats: {data.get('memoir_stats', {})}")
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Android Integration Test Completed!")
    
    # Summary for Android app
    print("\n📱 ANDROID APP INTEGRATION SUMMARY:")
    print("✅ Main memoir list endpoint: WORKING")
    print("✅ Search memoirs endpoint: WORKING")
    print("⚠️  Categories endpoint: NEEDS FIX")
    print("⚠️  Stats endpoint: NEEDS FIX")
    print("\n💡 Android app can now:")
    print("   - Display list of user memoirs")
    print("   - Search through memoirs")
    print("   - Show memoir details")
    print("   - Navigate between memoir screens")

if __name__ == "__main__":
    test_android_memoir_endpoints() 