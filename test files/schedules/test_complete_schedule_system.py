#!/usr/bin/env python3
"""
Complete Schedule System Test
Tests the entire schedule system including API, database, and voice notifications
"""
import requests
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import time

# Configuration
API_BASE = "https://backend-bootcamp.sonktx.online"
DB_CONFIG = {
    'host': '13.215.139.225',
    'port': 5432,
    'database': 'healthcare_ai',
    'user': 'postgres',
    'password': 'postgres'
}

def test_database_connection():
    """Test database connection"""
    print("🔌 Testing database connection...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()
        print(f"✅ Database connected: {version[0]}")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_api_endpoints():
    """Test all API endpoints"""
    print("\n🌐 Testing API endpoints...")
    
    endpoints = [
        ("Public Schedules", f"{API_BASE}/api/public/schedules/test"),
        ("Authenticated Schedules", f"{API_BASE}/api/schedules"),
        ("Health Check", f"{API_BASE}/health"),
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {name}: {response.status_code}")
            if response.status_code == 200:
                data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                if 'success' in data:
                    print(f"   - Success: {data['success']}")
                if 'total' in data:
                    print(f"   - Total: {data['total']}")
        except Exception as e:
            print(f"❌ {name}: {e}")

def test_schedule_creation():
    """Test schedule creation via API"""
    print("\n➕ Testing schedule creation...")
    
    # Sample schedule data
    schedule_data = {
        "elderly_id": "test_user_123",
        "title": "Test Schedule - Voice Notification",
        "message": "Đây là lịch trình test với thông báo voice",
        "scheduled_at": int((datetime.now() + timedelta(minutes=5)).timestamp()),
        "notification_type": "medicine_reminder",
        "category": "medicine",
        "priority": "high"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/schedules",
            json=schedule_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📤 Schedule creation response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Schedule created successfully!")
            print(f"   - Success: {data.get('success')}")
            print(f"   - Message: {data.get('message')}")
            if 'schedule' in data:
                schedule = data['schedule']
                print(f"   - ID: {schedule.get('id')}")
                print(f"   - Title: {schedule.get('title')}")
                print(f"   - Scheduled: {schedule.get('scheduled_at')}")
            return True
        elif response.status_code == 401:
            print("⚠️ Expected: Authentication required")
            return False
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Schedule creation failed: {e}")
        return False

def test_voice_notification():
    """Test voice notification generation"""
    print("\n🔊 Testing voice notification...")
    
    try:
        voice_data = {
            "text": "Lịch trình: Uống thuốc huyết áp. Vui lòng uống thuốc theo chỉ định của bác sĩ.",
            "voice_type": "female",
            "language": "vi"
        }
        
        response = requests.post(
            f"{API_BASE}/api/generate-voice-notification",
            json=voice_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"📤 Voice notification response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Voice notification generated!")
            print(f"   - Success: {data.get('success')}")
            print(f"   - Audio length: {len(data.get('audio_base64', ''))}")
            return True
        else:
            print(f"❌ Voice notification failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Voice notification test failed: {e}")
        return False

def check_database_schedules():
    """Check schedules in database"""
    print("\n🗄️ Checking database schedules...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Count total notifications
        cur.execute("SELECT COUNT(*) FROM notifications")
        total_notifications = cur.fetchone()['count']
        print(f"📊 Total notifications: {total_notifications}")
        
        # Count schedule notifications
        cur.execute("""
            SELECT COUNT(*) FROM notifications 
            WHERE notification_type IN ('medicine_reminder', 'appointment_reminder', 'health_check', 'custom')
        """)
        schedule_count = cur.fetchone()['count']
        print(f"📅 Schedule notifications: {schedule_count}")
        
        # Get recent schedules
        cur.execute("""
            SELECT id, title, user_id, notification_type, scheduled_at, is_sent, has_voice
            FROM notifications 
            WHERE notification_type IN ('medicine_reminder', 'appointment_reminder', 'health_check', 'custom')
            ORDER BY created_at DESC
            LIMIT 5
        """)
        schedules = cur.fetchall()
        
        print(f"\n📋 Recent schedules:")
        for schedule in schedules:
            print(f"   - {schedule['title']}")
            print(f"     ID: {schedule['id']}")
            print(f"     User: {schedule['user_id']}")
            print(f"     Type: {schedule['notification_type']}")
            print(f"     Scheduled: {schedule['scheduled_at']}")
            print(f"     Sent: {schedule['is_sent']}")
            print(f"     Has Voice: {schedule['has_voice']}")
            print()
        
        conn.close()
        return len(schedules)
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return 0

def test_android_api_compatibility():
    """Test API compatibility with Android app"""
    print("\n📱 Testing Android API compatibility...")
    
    # Test public endpoint with user ID (as Android app would call)
    test_user_id = "6dbbe787-9645-4203-94c1-3e5b1e9ca54c"  # User from database
    
    try:
        response = requests.get(f"{API_BASE}/api/public/schedules/{test_user_id}", timeout=10)
        print(f"📤 Public schedules for user {test_user_id}: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API response successful!")
            print(f"   - Success: {data.get('success')}")
            print(f"   - Total schedules: {data.get('total')}")
            
            schedules = data.get('schedules', [])
            if schedules:
                print(f"   - Found {len(schedules)} schedules")
                for i, schedule in enumerate(schedules[:3], 1):
                    print(f"     {i}. {schedule.get('title')} - {schedule.get('scheduled_at')}")
            else:
                print("   - No schedules found")
            
            return True
        else:
            print(f"❌ API call failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Android API compatibility test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Complete Schedule System Test")
    print("=" * 60)
    
    # Test database connection
    if not test_database_connection():
        print("❌ Cannot proceed without database connection")
        return
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test Android API compatibility
    android_ok = test_android_api_compatibility()
    
    # Test schedule creation
    creation_ok = test_schedule_creation()
    
    # Test voice notification
    voice_ok = test_voice_notification()
    
    # Check database
    schedule_count = check_database_schedules()
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 60)
    print(f"✅ Database Connection: {'OK' if test_database_connection() else 'FAILED'}")
    print(f"✅ Android API Compatibility: {'OK' if android_ok else 'FAILED'}")
    print(f"✅ Schedule Creation: {'OK' if creation_ok else 'FAILED'}")
    print(f"✅ Voice Notification: {'OK' if voice_ok else 'FAILED'}")
    print(f"📅 Total Schedules in DB: {schedule_count}")
    
    if android_ok and creation_ok and voice_ok:
        print("\n🎉 All tests passed! The schedule system is working correctly.")
        print("\n📱 Android app should now be able to:")
        print("   - Load schedules without 'đang tải lịch trình...' error")
        print("   - Create new schedules with voice notifications")
        print("   - Receive voice notifications for due schedules")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main() 