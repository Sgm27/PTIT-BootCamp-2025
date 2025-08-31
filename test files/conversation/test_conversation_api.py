#!/usr/bin/env python3
"""
Test script for conversation API endpoints
"""
import requests
import json
from datetime import datetime

# API Configuration
API_BASE_URL = "https://backend.vcaremind.io.vn"
TEST_USER_ID = "f5db7d59-1df3-4b83-a066-bbb95d7a28a0"

def test_get_conversations():
    """Test getting user conversations"""
    print("🔍 Testing GET /api/conversations/{user_id}")
    
    url = f"{API_BASE_URL}/api/conversations/{TEST_USER_ID}"
    params = {"limit": 10, "offset": 0}
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            conversations = data.get("conversations", [])
            print(f"✅ Success! Found {len(conversations)} conversations")
            
            if conversations:
                # Test with first conversation
                first_conv = conversations[0]
                conv_id = first_conv["id"]
                print(f"First conversation ID: {conv_id}")
                print(f"Title: {first_conv['title']}")
                return conv_id
            else:
                print("⚠️  No conversations found")
                return None
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_get_conversation_detail(conversation_id):
    """Test getting conversation detail"""
    print(f"\n🔍 Testing GET /api/conversations/{TEST_USER_ID}/{conversation_id}")
    
    url = f"{API_BASE_URL}/api/conversations/{TEST_USER_ID}/{conversation_id}"
    
    try:
        response = requests.get(url, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            conversation = data.get("conversation", {})
            messages = data.get("messages", [])
            print(f"✅ Success! Conversation: {conversation.get('title')}")
            print(f"Messages count: {len(messages)}")
            
            if messages:
                print("Sample messages:")
                for i, msg in enumerate(messages[:3]):  # Show first 3 messages
                    print(f"  {i+1}. [{msg['role']}]: {msg['content'][:50]}...")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_api_health():
    """Test API health"""
    print("🔍 Testing API Health")
    
    url = f"{API_BASE_URL}/"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy: {data.get('message', 'OK')}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 CONVERSATION API TEST SUITE")
    print("=" * 60)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Test Time: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Test API health
    if not test_api_health():
        print("\n❌ API health check failed. Stopping tests.")
        return
    
    # Test get conversations
    conversation_id = test_get_conversations()
    
    if conversation_id:
        # Test get conversation detail
        test_get_conversation_detail(conversation_id)
    else:
        print("\n⚠️  No conversations found to test detail endpoint")
    
    print("\n" + "=" * 60)
    print("🏁 TEST SUITE COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main() 