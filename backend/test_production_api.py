#!/usr/bin/env python3
"""
Test production API endpoints
"""
import requests
import json
import sys
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_production_api():
    # Production API URL
    base_url = "https://backend-bootcamp.sonktx.online"
    
    print(f"🚀 Testing Production API: {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. 🔍 Health Check:")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            print("   ✅ Backend is running!")
        else:
            print(f"   ❌ Failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Login endpoint
    print("\n2. 🔐 Login API Test:")
    login_data = {
        "identifier": "sondaitai27@gmail.com",
        "password": "sonktx12345"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Login successful!")
            print(f"   User: {data.get('user', {}).get('full_name')}")
            print(f"   User Type: {data.get('user', {}).get('user_type')}")
            print(f"   Session Token: {data.get('session_token', 'N/A')[:20]}...")
            
            # Test 3: Profile endpoint
            user_id = data.get('user', {}).get('user_id')
            if user_id:
                print(f"\n3. 👤 Profile API Test:")
                try:
                    profile_response = requests.get(
                        f"{base_url}/api/auth/profile/{user_id}",
                        timeout=10
                    )
                    print(f"   Status: {profile_response.status_code}")
                    if profile_response.status_code == 200:
                        profile_data = profile_response.json()
                        print(f"   ✅ Profile retrieved!")
                        print(f"   Name: {profile_data.get('full_name')}")
                        print(f"   Email: {profile_data.get('email')}")
                    else:
                        print(f"   ❌ Profile failed: {profile_response.text}")
                except Exception as e:
                    print(f"   ❌ Profile error: {e}")
        else:
            print(f"   ❌ Login failed: {response.text}")
    except Exception as e:
        print(f"   ❌ Login error: {e}")
    
    # Test 4: Database connection through API
    print(f"\n4. 🗄️  Database Connection Test:")
    print(f"   Database host: {os.getenv('DB_HOST', 'Not set')}")
    print(f"   Database port: {os.getenv('DB_PORT', 'Not set')}")
    
    # Test if we can connect to database directly
    try:
        import psycopg2
        db_config = {
            'host': os.getenv('DB_HOST', '13.216.164.63'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'healthcare_ai'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }
        
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        print(f"   ✅ Database connection successful!")
        print(f"   Total users: {user_count}")
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Production API Test Complete!")
    print("\n📱 Android App should now be able to connect to:")
    print(f"   • API: {base_url}")
    print(f"   • Database: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")

if __name__ == "__main__":
    test_production_api() 