#!/usr/bin/env python3
import requests
import json

def test_conversation_api():
    """Test the conversation API endpoint"""
    
    user_id = 'f5db7d59-1df3-4b83-a066-bbb95d7a28a0'
    # Try localhost first, then remote
    urls = [
        f'http://localhost:8000/api/conversations/{user_id}',
        f'http://13.216.164.63:8000/api/conversations/{user_id}'
    ]
    
    for url in urls:
        try:
            print(f"Testing API: {url}")
            response = requests.get(url, timeout=5)
            print(f'Status Code: {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                print(f'Response keys: {list(data.keys())}')
                
                if 'conversations' in data:
                    conversations = data['conversations']
                    print(f'Found {len(conversations)} conversations')
                    
                    for i, conv in enumerate(conversations[:3]):  # Show first 3
                        title = conv.get('title', 'No title')
                        messages = conv.get('total_messages', 0)
                        started_at = conv.get('started_at', 'Unknown')
                        print(f'  {i+1}. "{title}" - {messages} messages - {started_at}')
                    return  # Success, exit
                else:
                    print('No conversations key in response')
                    print(f'Full response: {json.dumps(data, indent=2)}')
                    return  # Success, exit
            else:
                print(f'Error response: {response.text}')
                
        except Exception as e:
            print(f'Error: {e}')
            continue  # Try next URL
    
    print("All URLs failed")

if __name__ == "__main__":
    test_conversation_api() 