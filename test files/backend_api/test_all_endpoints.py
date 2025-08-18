"""
Test all backend endpoints
"""
import requests
import json
import time

def test_endpoint(url, method="GET", data=None, expected_status=200):
    """Test a specific endpoint"""
    try:
        print(f"\n🔍 Testing: {method} {url}")
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        status = response.status_code
        
        if status == expected_status:
            print(f"✅ Status: {status}")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
                if isinstance(response_data, dict):
                    # Show key information
                    if "message" in response_data:
                        print(f"   Message: {response_data['message']}")
                    if "status" in response_data:
                        print(f"   Status: {response_data['status']}")
                    if "timestamp" in response_data:
                        print(f"   Timestamp: {response_data['timestamp']}")
                    if "services" in response_data:
                        print(f"   Services: {len(response_data['services'])} services")
                else:
                    print(f"   Response: {str(response_data)[:100]}...")
            except:
                print(f"   Response: {response.text[:100]}...")
            
            return True
        else:
            print(f"❌ Expected: {expected_status}, Got: {status}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection refused (server not running)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Test all endpoints"""
    base_url = "http://localhost:8000"
    
    print("🚀 Testing All Backend Endpoints")
    print("=" * 50)
    
    # Test basic endpoints
    basic_endpoints = [
        ("/", "GET"),
        ("/health", "GET"),
        ("/api/websocket/health", "GET"),
        ("/api/services/status", "GET"),
    ]
    
    print("\n📋 Testing Basic Endpoints:")
    basic_success = 0
    for endpoint, method in basic_endpoints:
        if test_endpoint(f"{base_url}{endpoint}", method):
            basic_success += 1
    
    # Test conversation endpoints
    print("\n💬 Testing Conversation Endpoints:")
    conv_endpoints = [
        ("/api/conversations/test_user", "GET"),
        ("/api/websocket/status", "GET"),
    ]
    
    conv_success = 0
    for endpoint, method in conv_endpoints:
        if test_endpoint(f"{base_url}{endpoint}", method):
            conv_success += 1
    
    # Test memoir endpoints
    print("\n📚 Testing Memoir Endpoints:")
    memoir_endpoints = [
        ("/api/memoirs/test_user", "GET"),
        ("/api/memoirs/test_user/categories", "GET"),
        ("/api/memoirs/test_user/people", "GET"),
        ("/api/memoirs/test_user/places", "GET"),
        ("/api/memoirs/test_user/stats", "GET"),
        ("/api/memoirs/test_user/timeline", "GET"),
    ]
    
    memoir_success = 0
    for endpoint, method in memoir_endpoints:
        if test_endpoint(f"{base_url}{endpoint}", method):
            memoir_success += 1
    
    # Test user stats
    print("\n👤 Testing User Stats:")
    user_success = 0
    if test_endpoint(f"{base_url}/api/users/test_user/stats", "GET"):
        user_success += 1
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    total_tests = len(basic_endpoints) + len(conv_endpoints) + len(memoir_endpoints) + 1
    total_success = basic_success + conv_success + memoir_success + user_success
    
    print(f"Basic Endpoints:     {basic_success}/{len(basic_endpoints)} ✅")
    print(f"Conversation APIs:   {conv_success}/{len(conv_endpoints)} ✅")
    print(f"Memoir APIs:         {memoir_success}/{len(memoir_endpoints)} ✅")
    print(f"User Stats:          {user_success}/1 ✅")
    print("-" * 50)
    print(f"Total:               {total_success}/{total_tests} ✅")
    
    if total_success == total_tests:
        print("\n🎉 ALL TESTS PASSED! Backend is working perfectly!")
        print("\n🌐 You can now access:")
        print(f"   Main API: {base_url}/")
        print(f"   Health: {base_url}/health")
        print(f"   API Docs: {base_url}/docs")
        print(f"   WebSocket: ws://localhost:8000/gemini-live")
    else:
        print(f"\n⚠️ {total_tests - total_success} tests failed. Some endpoints may have issues.")
        print("Check the logs above for details.")

if __name__ == "__main__":
    main() 