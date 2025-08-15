#!/usr/bin/env python3
"""
Script to test creating 15 users through production API endpoint
This tests the API registration endpoint instead of direct database insertion
"""
import requests
import json
import time
from datetime import datetime, timedelta
import random

# Production API URL
BASE_URL = "https://backend-bootcamp.sonktx.online/"
REGISTER_ENDPOINT = f"{BASE_URL}api/auth/register"

def generate_test_user_data(index):
    """Generate test user data for registration"""
    
    # Sample Vietnamese names
    first_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương"]
    last_names = ["Văn An", "Thị Bình", "Minh Châu", "Thị Dung", "Văn Em", "Thị Phương", "Minh Giang", "Thị Hoa", "Văn Inh", "Thị Kim"]
    
    # Generate random data with timestamp to ensure uniqueness
    import time
    timestamp = int(time.time())
    
    full_name = f"{random.choice(first_names)} {random.choice(last_names)} {index:02d}"
    email = f"testuser{index:02d}_{timestamp}@example.com"  # Add timestamp for uniqueness
    phone = f"09{random.randint(10000000, 99999999)}"
    password = f"TestPass{index:02d}!"
    
    # Random birth date (60-90 years old for elderly users)
    birth_year = random.randint(1934, 1964)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    date_of_birth = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
    
    gender = random.choice(["male", "female"])
    
    # Vietnamese addresses
    addresses = [
        "123 Nguyễn Huệ, Quận 1, TP.HCM",
        "456 Lê Lợi, Quận 3, TP.HCM", 
        "789 Trần Hưng Đạo, Quận 5, TP.HCM",
        "321 Võ Văn Tần, Quận 3, TP.HCM",
        "654 Điện Biên Phủ, Quận Bình Thạnh, TP.HCM",
        "987 Cách Mạng Tháng 8, Quận 10, TP.HCM",
        "147 Nguyễn Thị Minh Khai, Quận 1, TP.HCM",
        "258 Lý Tự Trọng, Quận 1, TP.HCM",
        "369 Hai Bà Trưng, Quận 1, TP.HCM",
        "741 Nguyễn Du, Quận 1, TP.HCM"
    ]
    
    address = random.choice(addresses)
    
    # Mix of elderly and family member types
    user_type = "elderly" if index <= 10 else "family"
    
    return {
        "user_type": user_type,
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "password": password,
        "date_of_birth": date_of_birth,
        "gender": gender,
        "address": address
    }

def create_user_via_api(user_data, index):
    """Create a single user through API"""
    try:
        print(f"\n=== Creating User {index:02d} ===")
        print(f"Name: {user_data['full_name']}")
        print(f"Email: {user_data['email']}")
        print(f"Phone: {user_data['phone']}")
        print(f"Type: {user_data['user_type']}")
        print(f"API URL: {REGISTER_ENDPOINT}")
        
        # Make API request
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(
            REGISTER_ENDPOINT,
            json=user_data,
            headers=headers,
            timeout=30
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200 or response.status_code == 201:
            response_data = response.json()
            print(f"✅ SUCCESS: User created successfully")
            print(f"Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            if 'user' in response_data and response_data['user']:
                user_id = response_data['user'].get('user_id', 'N/A')
                print(f"User ID: {user_id}")
                return True, user_id, response_data
            else:
                print(f"⚠️  WARNING: User created but no user data in response")
                return True, None, response_data
                
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error Response: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print(f"Error Response (raw): {response.text}")
            return False, None, None
            
    except requests.exceptions.Timeout:
        print(f"❌ TIMEOUT: Request timed out after 30 seconds")
        return False, None, None
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR: Could not connect to {REGISTER_ENDPOINT}")
        return False, None, None
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {e}")
        return False, None, None
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False, None, None

def test_create_15_users():
    """Main function to create 15 test users"""
    print("🚀 Starting test: Creating 15 users via Production API")
    print(f"API Endpoint: {REGISTER_ENDPOINT}")
    print(f"Timestamp: {datetime.now()}")
    print("=" * 60)
    
    successful_users = []
    failed_users = []
    
    for i in range(1, 16):  # Create users 01 to 15
        user_data = generate_test_user_data(i)
        success, user_id, response_data = create_user_via_api(user_data, i)
        
        if success:
            successful_users.append({
                'index': i,
                'user_data': user_data,
                'user_id': user_id,
                'response': response_data
            })
        else:
            failed_users.append({
                'index': i,
                'user_data': user_data
            })
        
        # Wait between requests to avoid overwhelming the server
        if i < 15:
            print(f"Waiting 2 seconds before next request...")
            time.sleep(2)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY REPORT")
    print("=" * 60)
    print(f"Total users attempted: 15")
    print(f"✅ Successful: {len(successful_users)}")
    print(f"❌ Failed: {len(failed_users)}")
    print(f"Success rate: {len(successful_users)/15*100:.1f}%")
    
    if successful_users:
        print(f"\n✅ SUCCESSFUL USERS ({len(successful_users)}):")
        for user in successful_users:
            print(f"  {user['index']:02d}. {user['user_data']['full_name']} ({user['user_data']['email']}) - ID: {user['user_id']}")
    
    if failed_users:
        print(f"\n❌ FAILED USERS ({len(failed_users)}):")
        for user in failed_users:
            print(f"  {user['index']:02d}. {user['user_data']['full_name']} ({user['user_data']['email']})")
    
    # Save detailed results to file
    results = {
        'timestamp': datetime.now().isoformat(),
        'api_endpoint': REGISTER_ENDPOINT,
        'total_attempted': 15,
        'successful_count': len(successful_users),
        'failed_count': len(failed_users),
        'success_rate': len(successful_users)/15*100,
        'successful_users': successful_users,
        'failed_users': failed_users
    }
    
    with open('test_create_users_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n📄 Detailed results saved to: test_create_users_results.json")
    
    return len(successful_users) == 15

if __name__ == "__main__":
    success = test_create_15_users()
    if success:
        print(f"\n🎉 ALL TESTS PASSED: Successfully created all 15 users!")
    else:
        print(f"\n⚠️  SOME TESTS FAILED: Check the results above for details") 