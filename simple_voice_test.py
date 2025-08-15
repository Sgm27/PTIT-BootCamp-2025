#!/usr/bin/env python3
"""
Comprehensive Voice Notification Test - Test tất cả notification types với user cụ thể
"""

import requests
import json
import time

class VoiceNotificationTester:
    """Class để test tất cả các loại voice notifications với user authentication"""
    
    def __init__(self):
        self.base_url = "https://backend-bootcamp.sonktx.online"
        self.auth_url = f"{self.base_url}/api/auth/login"
        self.voice_url = f"{self.base_url}/api/generate-voice-notification"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.session_token = None
        self.user_id = None
        self.results = []
        
    def authenticate_user(self):
        """Đăng nhập với user son123@gmail.com để lấy session token"""
        print("🔐 AUTHENTICATING USER")
        print("=" * 50)
        
        login_payload = {
            "identifier": "son123@gmail.com",
            "password": "12345678"  # Password đúng
        }
        
        try:
            response = requests.post(
                self.auth_url,
                json=login_payload,
                headers=self.headers,
                timeout=30
            )
            
            print(f"📊 Login Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    self.session_token = result.get('session_token')
                    self.user_id = result.get('user', {}).get('user_id')
                    
                    print("✅ LOGIN SUCCESSFUL!")
                    print(f"👤 User ID: {self.user_id}")
                    print(f"🔑 Session Token: {self.session_token[:20]}...")
                    print(f"👤 User Name: {result.get('user', {}).get('full_name')}")
                    print(f"📧 Email: {result.get('user', {}).get('email')}")
                    return True
                else:
                    print(f"❌ Login failed: {result.get('message')}")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"📄 Response: {response.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_payloads(self):
        """Tất cả test payloads cho các notification types với user authentication"""
        return [
            # Medicine reminders
            {
                "text": "Nhắc nhở uống thuốc: Đã đến giờ uống Paracetamol 500mg lúc 8:00 sáng. Nhớ uống thuốc đúng giờ để đảm bảo hiệu quả điều trị nhé.",
                "type": "medicine",
                "description": "Medicine Reminder - Paracetamol"
            },
            {
                "text": "Đã đến giờ uống thuốc huyết áp. Nhớ uống thuốc đúng giờ nhé bác.",
                "type": "medicine", 
                "description": "Medicine Reminder - Blood pressure"
            },
            
            # Appointment reminders
            {
                "text": "Nhắc nhở lịch khám: Bác có lịch khám với bác sĩ Nguyễn Văn A vào 14:30 ngày mai. Nhớ chuẩn bị đầy đủ giấy tờ và đến đúng giờ nhé.",
                "type": "appointment",
                "description": "Appointment Reminder - Dr. Nguyen Van A"
            },
            {
                "text": "Lịch khám tim mạch vào 9:00 sáng mai. Nhớ mang theo kết quả xét nghiệm cũ nhé.",
                "type": "appointment",
                "description": "Appointment Reminder - Cardiology"
            },
            
            # Exercise reminders
            {
                "text": "Nhắc nhở tập thể dục: Đã đến giờ đi bộ trong 30 phút. Tập thể dục đều đặn giúp cơ thể khỏe mạnh và tinh thần sảng khoái.",
                "type": "exercise",
                "description": "Exercise Reminder - Walking"
            },
            {
                "text": "Đã đến giờ tập yoga buổi sáng. Hãy chuẩn bị và bắt đầu nhé.",
                "type": "exercise",
                "description": "Exercise Reminder - Yoga"
            },
            
            # Water reminders
            {
                "text": "Nhắc nhở uống nước: Đã đến giờ uống nước. Uống đủ nước giúp cơ thể hoạt động tốt và da dẻ khỏe mạnh.",
                "type": "water",
                "description": "Water Reminder - General"
            },
            {
                "text": "Bác ơi, nhớ uống nước đủ 2 lít mỗi ngày nhé.",
                "type": "water",
                "description": "Water Reminder - Daily goal"
            },
            
            # Meal reminders
            {
                "text": "Nhắc nhở ăn uống: Đã đến giờ ăn sáng. Ăn uống đúng giờ và đầy đủ dinh dưỡng giúp cơ thể khỏe mạnh.",
                "type": "meal",
                "description": "Meal Reminder - Breakfast"
            },
            {
                "text": "Đã đến giờ ăn trưa. Hãy nghỉ ngơi và ăn uống đầy đủ nhé.",
                "type": "meal",
                "description": "Meal Reminder - Lunch"
            },
            
            # Health check reminders
            {
                "text": "Nhắc nhở kiểm tra sức khỏe: Đã đến giờ đo huyết áp. Theo dõi sức khỏe định kỳ giúp phát hiện sớm các vấn đề và có biện pháp điều trị kịp thời.",
                "type": "health_check",
                "description": "Health Check - Blood pressure"
            },
            {
                "text": "Đã đến giờ đo đường huyết. Hãy chuẩn bị máy đo và thực hiện nhé.",
                "type": "health_check",
                "description": "Health Check - Blood sugar"
            },
            
            # Emergency notifications
            {
                "text": "Phát hiện nhịp tim bất thường. Vui lòng liên hệ bác sĩ ngay lập tức.",
                "type": "emergency",
                "description": "Emergency Alert - Heart rate"
            },
            {
                "text": "Huyết áp quá cao. Cần chú ý và nghỉ ngơi ngay.",
                "type": "emergency",
                "description": "Emergency Alert - High blood pressure"
            },
            
            # Custom/Info notifications
            {
                "text": "Chúc bác có một ngày tốt lành và sức khỏe dồi dào.",
                "type": "info",
                "description": "Custom Info - Good wishes"
            },
            {
                "text": "Hôm nay trời đẹp, bác có thể ra ngoài đi dạo một chút nhé.",
                "type": "custom",
                "description": "Custom Info - Weather suggestion"
            }
        ]
    
    def test_single_notification(self, payload, test_index):
        """Test một notification đơn lẻ với user authentication"""
        print(f"\n🧪 TEST #{test_index:02d}: {payload['description']}")
        print("=" * 60)
        print(f"🏷️ Type: {payload['type']}")
        print(f"👤 Authenticated User: son123@gmail.com (ID: {self.user_id})")
        print(f"📝 Text: {payload['text'][:100]}{'...' if len(payload['text']) > 100 else ''}")
        print("-" * 60)
        
        try:
            # Thêm Authorization header nếu có session token
            headers = self.headers.copy()
            if self.session_token:
                headers["Authorization"] = f"Bearer {self.session_token}"
            
            response = requests.post(
                self.voice_url, 
                json=payload, 
                headers=headers, 
                timeout=30
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    audio_length = len(result.get('audioBase64', '')) if result.get('audioBase64') else 0
                    
                    print("✅ SUCCESS!")
                    print(f"🔊 Audio Length: {audio_length:,} characters")
                    print(f"📧 Format: {result.get('audioFormat', 'N/A')}")
                    print(f"⏰ Timestamp: {result.get('timestamp', 'N/A')}")
                    
                    self.results.append({
                        "test": payload['description'],
                        "type": payload['type'],
                        "user_id": self.user_id,
                        "status": "SUCCESS",
                        "audio_length": audio_length,
                        "response_size": len(str(result))
                    })
                    return True
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON Error: {e}")
                    print(f"📄 Raw Response: {response.text[:200]}...")
                    self.results.append({
                        "test": payload['description'],
                        "type": payload['type'],
                        "user_id": self.user_id,
                        "status": f"JSON_ERROR: {e}",
                        "audio_length": 0,
                        "response_size": 0
                    })
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"📄 Response: {response.text[:200]}...")
                self.results.append({
                    "test": payload['description'],
                    "type": payload['type'],
                    "user_id": self.user_id,
                    "status": f"HTTP_ERROR: {response.status_code}",
                    "audio_length": 0,
                    "response_size": 0
                })
                return False
                
        except requests.exceptions.Timeout:
            print("❌ Request Timeout")
            self.results.append({
                "test": payload['description'],
                "type": payload['type'],
                "user_id": self.user_id,
                "status": "TIMEOUT",
                "audio_length": 0,
                "response_size": 0
            })
            return False
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection Error: {e}")
            self.results.append({
                "test": payload['description'],
                "type": payload['type'],
                "user_id": self.user_id,
                "status": f"CONNECTION_ERROR: {e}",
                "audio_length": 0,
                "response_size": 0
            })
            return False
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            self.results.append({
                "test": payload['description'],
                "type": payload['type'],
                "user_id": self.user_id,
                "status": f"ERROR: {e}",
                "audio_length": 0,
                "response_size": 0
            })
            return False
    
    def run_comprehensive_test(self):
        """Chạy test toàn diện cho tất cả notification types với user authentication"""
        print("🚀 COMPREHENSIVE VOICE NOTIFICATION TEST WITH USER AUTHENTICATION")
        print("=" * 80)
        print(f"🌐 Target URL: {self.base_url}")
        print(f"👤 Target User: son123@gmail.com")
        print(f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Bước 1: Authenticate user
        if not self.authenticate_user():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return 0, 0
        
        print("\n" + "=" * 80)
        print("🔐 AUTHENTICATION SUCCESSFUL - PROCEEDING WITH TESTS")
        print("=" * 80)
        
        # Bước 2: Run voice notification tests
        test_payloads = self.test_payloads()
        total_tests = len(test_payloads)
        passed_tests = 0
        
        print(f"📋 Total tests to run: {total_tests}")
        print("=" * 80)
        
        for i, payload in enumerate(test_payloads, 1):
            success = self.test_single_notification(payload, i)
            if success:
                passed_tests += 1
            
            # Small delay between tests
            if i < total_tests:
                print("⏳ Waiting 2 seconds before next test...")
                time.sleep(2)
        
        self.print_summary(total_tests, passed_tests)
        return passed_tests, total_tests
    
    def print_summary(self, total_tests, passed_tests):
        """In tổng kết kết quả test"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY REPORT")
        print("=" * 80)
        
        print(f"👤 Test User: son123@gmail.com (ID: {self.user_id})")
        print(f"✅ Passed: {passed_tests}/{total_tests} tests")
        print(f"❌ Failed: {total_tests - passed_tests}/{total_tests} tests")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Group by type
        types_summary = {}
        for result in self.results:
            type_name = result['type']
            if type_name not in types_summary:
                types_summary[type_name] = {'passed': 0, 'total': 0}
            
            types_summary[type_name]['total'] += 1
            if result['status'] == 'SUCCESS':
                types_summary[type_name]['passed'] += 1
        
        print("\n📋 BREAKDOWN BY TYPE:")
        print("-" * 50)
        for type_name, stats in types_summary.items():
            success_rate = (stats['passed']/stats['total'])*100
            print(f"🏷️  {type_name:12s} | {stats['passed']:2d}/{stats['total']:2d} | {success_rate:5.1f}%")
        
        # Failed tests detail
        failed_tests = [r for r in self.results if r['status'] != 'SUCCESS']
        if failed_tests:
            print(f"\n❌ FAILED TESTS DETAIL:")
            print("-" * 50)
            for i, failed in enumerate(failed_tests, 1):
                print(f"{i:2d}. {failed['test']:<30s} | {failed['status']}")
        
        print("\n" + "=" * 80)
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! 🎉")
        elif passed_tests > 0:
            print("⚠️  SOME TESTS FAILED - Check details above")
        else:
            print("💥 ALL TESTS FAILED - Check connection and server")
        print("=" * 80)

def main():
    """Main function để chạy tất cả tests"""
    tester = VoiceNotificationTester()
    passed, total = tester.run_comprehensive_test()
    
    # Return exit code for CI/CD
    if passed == total:
        exit(0)  # Success
    else:
        exit(1)  # Some tests failed

if __name__ == "__main__":
    main()