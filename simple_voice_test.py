#!/usr/bin/env python3
"""
Simple Voice Notification Test - Chỉ test 1 notification đơn giản
"""

import requests
import json

def test_voice_notification():
    """Test một voice notification đơn giản"""
    
    # URL endpoint
    url = "https://backend-bootcamp.sonktx.online/api/generate-voice-notification"
    
    # Request data
    payload = {
        "text": "nhớ uống thuốc mà Đức Sơn đã gửi nhé",
        "type": "medicine"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("🔔 Testing Voice Notification...")
    print(f"📝 Text: {payload['text']}")
    print(f"🌐 URL: {url}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("✅ SUCCESS!")
                print(f"📧 Success: {result.get('success', False)}")
                print(f"📧 Message: {result.get('message', 'N/A')}")
                
                # Debug: Print full response structure
                print("🐛 DEBUG - Full Response:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                print(f"📧 Audio Length: {len(result.get('audioBase64', '')) if result.get('audioBase64') else 0} characters")
                print(f"📧 Format: {result.get('audioFormat', 'N/A')}")
                print(f"📧 Timestamp: {result.get('timestamp', 'N/A')}")
                return True
            except json.JSONDecodeError as e:
                print(f"❌ JSON Error: {e}")
                print(f"📄 Raw Response: {response.text[:500]}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request Timeout")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Simple Voice Notification Test")
    print("=" * 50)
    success = test_voice_notification()
    print("=" * 50)
    if success:
        print("🎉 Test PASSED!")
    else:
        print("💥 Test FAILED!")
