#!/usr/bin/env python3
"""
Test conversation API và thêm dữ liệu test nếu cần
"""
import requests
import json
import sys
from datetime import datetime, timedelta

def test_conversation_api():
    """Test conversation API endpoints"""
    base_url = "https://backend.vcaremind.io.vn"
    test_user_id = "f5db7d59-1df3-4b83-a066-bbb95d7a28a0"  # Test user từ documents
    
    print("🔍 Testing Conversation API")
    print("=" * 50)
    
    # Test 1: Get conversations
    print(f"\n1. 📋 Get Conversations for User: {test_user_id}")
    try:
        response = requests.get(
            f"{base_url}/api/conversations/{test_user_id}?limit=10",
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            conversations = data.get('conversations', [])
            print(f"   ✅ Found {len(conversations)} conversations")
            
            for i, conv in enumerate(conversations[:3]):  # Show first 3
                print(f"   📝 Conversation {i+1}:")
                print(f"      ID: {conv.get('id')}")
                print(f"      Title: {conv.get('title')}")
                print(f"      Started: {conv.get('started_at')}")
                print(f"      Messages: {conv.get('total_messages')}")
                print(f"      Active: {conv.get('is_active')}")
                print(f"      Summary: {conv.get('summary', 'No summary')[:50]}...")
            
            return conversations
        else:
            print(f"   ❌ Failed: {response.text}")
            return []
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []

def add_test_conversations():
    """Thêm dữ liệu test conversations nếu cần"""
    base_url = "https://backend.vcaremind.io.vn"
    test_user_id = "f5db7d59-1df3-4b83-a066-bbb95d7a28a0"
    
    print(f"\n2. ➕ Adding Test Conversations")
    
    # Sample conversations
    test_conversations = [
        {
            "title": "Tư vấn sức khỏe tim mạch",
            "summary": "Thảo luận về các triệu chứng đau ngực và cách phòng ngừa bệnh tim mạch",
            "messages": [
                {"role": "user", "content": "Tôi bị đau ngực gần đây, có phải bệnh tim không?"},
                {"role": "assistant", "content": "Đau ngực có thể có nhiều nguyên nhân khác nhau. Tôi khuyên bạn nên đi khám bác sĩ để được chẩn đoán chính xác."}
            ]
        },
        {
            "title": "Hỏi về thuốc huyết áp",
            "summary": "Tư vấn về cách sử dụng thuốc huyết áp và tác dụng phụ",
            "messages": [
                {"role": "user", "content": "Thuốc huyết áp có tác dụng phụ gì không?"},
                {"role": "assistant", "content": "Thuốc huyết áp có thể có một số tác dụng phụ như chóng mặt, mệt mỏi. Bạn nên uống đúng liều và theo dõi phản ứng của cơ thể."}
            ]
        },
        {
            "title": "Chế độ ăn cho người tiểu đường",
            "summary": "Tư vấn chế độ dinh dưỡng phù hợp cho người bệnh tiểu đường",
            "messages": [
                {"role": "user", "content": "Người tiểu đường nên ăn gì?"},
                {"role": "assistant", "content": "Người tiểu đường nên ăn nhiều rau xanh, hạn chế đường và tinh bột, chia nhỏ bữa ăn trong ngày."}
            ]
        }
    ]
    
    created_count = 0
    for conv_data in test_conversations:
        try:
            # Create conversation
            create_response = requests.post(
                f"{base_url}/api/conversations",
                json={
                    "user_id": test_user_id,
                    "title": conv_data["title"],
                    "session_id": f"test_session_{datetime.now().timestamp()}"
                },
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if create_response.status_code == 200:
                conv_result = create_response.json()
                conversation_id = conv_result.get("conversation_id")
                print(f"   ✅ Created: {conv_data['title']}")
                created_count += 1
                
                # Add messages to conversation
                for msg in conv_data["messages"]:
                    msg_response = requests.post(
                        f"{base_url}/api/conversations/{conversation_id}/messages",
                        json={
                            "role": msg["role"],
                            "content": msg["content"],
                            "user_id": test_user_id
                        },
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    if msg_response.status_code != 200:
                        print(f"   ⚠️  Failed to add message: {msg_response.text}")
            else:
                print(f"   ❌ Failed to create: {conv_data['title']} - {create_response.text}")
                
        except Exception as e:
            print(f"   ❌ Error creating {conv_data['title']}: {e}")
    
    print(f"   📊 Created {created_count}/{len(test_conversations)} conversations")
    return created_count

def test_conversation_detail():
    """Test conversation detail endpoint"""
    base_url = "https://backend.vcaremind.io.vn"
    test_user_id = "f5db7d59-1df3-4b83-a066-bbb95d7a28a0"
    
    print(f"\n3. 🔍 Test Conversation Detail")
    
    # First get conversations to get an ID
    try:
        response = requests.get(
            f"{base_url}/api/conversations/{test_user_id}?limit=1",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            conversations = data.get('conversations', [])
            
            if conversations:
                conv_id = conversations[0]['id']
                print(f"   Testing detail for conversation: {conv_id}")
                
                detail_response = requests.get(
                    f"{base_url}/api/conversations/{test_user_id}/{conv_id}",
                    timeout=10
                )
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    print(f"   ✅ Detail retrieved successfully")
                    print(f"   Title: {detail_data.get('conversation', {}).get('title')}")
                    print(f"   Messages: {len(detail_data.get('messages', []))}")
                    return True
                else:
                    print(f"   ❌ Detail failed: {detail_response.text}")
            else:
                print(f"   ⚠️  No conversations found to test detail")
        else:
            print(f"   ❌ Failed to get conversations: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return False

def main():
    print("🚀 Testing Conversation Data for Android App")
    print("=" * 60)
    
    # Test existing conversations
    conversations = test_conversation_api()
    
    # Add test data if needed
    if len(conversations) < 3:
        print(f"\n⚠️  Only {len(conversations)} conversations found. Adding test data...")
        add_test_conversations()
        
        # Test again after adding
        print(f"\n🔄 Re-testing after adding data...")
        conversations = test_conversation_api()
    
    # Test conversation detail
    test_conversation_detail()
    
    print("\n" + "=" * 60)
    print("📱 Android App Test Instructions:")
    print("1. Build and install app: cd backend/GeminiLiveDemo && ./gradlew installDebug")
    print("2. Open app and login")
    print("3. Click 'Lịch sử trò chuyện' button")
    print("4. Verify conversations are displayed")
    print("5. Click on a conversation to view details")
    
    if len(conversations) > 0:
        print(f"\n✅ Ready for testing! Found {len(conversations)} conversations")
        return True
    else:
        print(f"\n❌ No conversations available for testing")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 