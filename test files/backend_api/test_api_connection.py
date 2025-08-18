#!/usr/bin/env python3
"""
Test script to verify API connection and response
"""
import requests
import json

def test_api_connection():
    """Test API connection and conversation endpoint"""
    
    base_url = "https://backend-bootcamp.sonktx.online"
    user_id = "f5db7d59-1df3-4b83-a066-bbb95d7a28a0"
    
    print("=== Testing API Connection ===")
    print(f"Base URL: {base_url}")
    print(f"User ID: {user_id}")
    
    try:
        # Test root endpoint
        print("\n1. Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test conversations endpoint
        print("\n2. Testing conversations endpoint...")
        response = requests.get(f"{base_url}/api/conversations/{user_id}", timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Found {len(data.get('conversations', []))} conversations")
            print(f"Total count: {data.get('total_count', 0)}")
            
            # Show first conversation as example
            conversations = data.get('conversations', [])
            if conversations:
                first_conv = conversations[0]
                print(f"\nFirst conversation:")
                print(f"  ID: {first_conv.get('id')}")
                print(f"  Title: {first_conv.get('title')}")
                print(f"  Messages: {first_conv.get('total_messages')}")
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api_connection() 