#!/usr/bin/env python3
"""
Test script to check and create sample schedule data
"""
import requests
import json
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration
API_BASE = "https://backend-bootcamp.sonktx.online"
DB_CONFIG = {
    'host': '13.216.164.63',
    'port': 5432,
    'database': 'healthcare_ai',
    'user': 'postgres',
    'password': 'postgres'
}

def test_api_endpoints():
    """Test API endpoints"""
    print("🔍 Testing API endpoints...")
    
    # Test public schedules endpoint
    try:
        response = requests.get(f"{API_BASE}/api/public/schedules/test", timeout=10)
        print(f"✅ Public schedules endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Success: {data.get('success')}")
            print(f"   - Total schedules: {data.get('total')}")
    except Exception as e:
        print(f"❌ Public schedules endpoint failed: {e}")
    
    # Test authenticated schedules endpoint
    try:
        response = requests.get(f"{API_BASE}/api/schedules", timeout=10)
        print(f"✅ Authenticated schedules endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Success: {data.get('success')}")
            print(f"   - Total schedules: {data.get('total')}")
        elif response.status_code == 401:
            print("   - Expected: Authentication required")
    except Exception as e:
        print(f"❌ Authenticated schedules endpoint failed: {e}")

def check_database_schedules():
    """Check existing schedules in database"""
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
        
        # Get sample schedules
        cur.execute("""
            SELECT id, title, user_id, notification_type, scheduled_at, created_at
            FROM notifications 
            WHERE notification_type IN ('medicine_reminder', 'appointment_reminder', 'health_check', 'custom')
            ORDER BY created_at DESC
            LIMIT 5
        """)
        schedules = cur.fetchall()
        
        print(f"\n📋 Sample schedules:")
        for schedule in schedules:
            print(f"   - {schedule['title']}")
            print(f"     User: {schedule['user_id']}")
            print(f"     Type: {schedule['notification_type']}")
            print(f"     Scheduled: {schedule['scheduled_at']}")
            print()
        
        # Get user IDs that have schedules
        cur.execute("""
            SELECT DISTINCT user_id, COUNT(*) as schedule_count
            FROM notifications 
            WHERE notification_type IN ('medicine_reminder', 'appointment_reminder', 'health_check', 'custom')
            GROUP BY user_id
            ORDER BY schedule_count DESC
        """)
        user_schedules = cur.fetchall()
        
        print(f"👥 Users with schedules:")
        for user in user_schedules:
            print(f"   - User {user['user_id']}: {user['schedule_count']} schedules")
        
        conn.close()
        return user_schedules
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return []

def create_sample_schedules():
    """Create sample schedules for testing"""
    print("\n➕ Creating sample schedules...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get a sample user ID (use the first user from users table)
        cur.execute("SELECT id FROM users LIMIT 1")
        user_result = cur.fetchone()
        
        if not user_result:
            print("❌ No users found in database")
            return
        
        user_id = user_result[0]
        print(f"👤 Using user ID: {user_id}")
        
        # Create sample schedules
        sample_schedules = [
            {
                'title': 'Uống thuốc huyết áp',
                'message': 'Uống thuốc huyết áp theo chỉ định của bác sĩ',
                'notification_type': 'medicine_reminder',
                'category': 'medicine',
                'scheduled_at': datetime.now() + timedelta(hours=1)
            },
            {
                'title': 'Tái khám bác sĩ Tim mạch',
                'message': 'Tái khám định kỳ với bác sĩ chuyên khoa tim mạch',
                'notification_type': 'appointment_reminder',
                'category': 'appointment',
                'scheduled_at': datetime.now() + timedelta(hours=3)
            },
            {
                'title': 'Đi bộ 30 phút',
                'message': 'Tập thể dục nhẹ nhàng bằng cách đi bộ',
                'notification_type': 'health_check',
                'category': 'exercise',
                'scheduled_at': datetime.now() + timedelta(hours=6)
            }
        ]
        
        for i, schedule in enumerate(sample_schedules, 1):
            cur.execute("""
                INSERT INTO notifications (
                    user_id, notification_type, title, message, 
                    scheduled_at, priority, category, has_voice, 
                    is_sent, is_read, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                schedule['notification_type'],
                schedule['title'],
                schedule['message'],
                schedule['scheduled_at'],
                'normal',
                schedule['category'],
                True,
                False,
                False,
                datetime.now(),
                datetime.now()
            ))
            print(f"✅ Created schedule {i}: {schedule['title']}")
        
        conn.commit()
        conn.close()
        print("✅ Sample schedules created successfully!")
        
    except Exception as e:
        print(f"❌ Failed to create sample schedules: {e}")

def test_schedule_creation_api():
    """Test schedule creation via API"""
    print("\n🧪 Testing schedule creation API...")
    
    # Sample schedule data
    schedule_data = {
        "elderly_id": "test_user_123",
        "title": "Test Schedule via API",
        "message": "This is a test schedule created via API",
        "scheduled_at": int((datetime.now() + timedelta(hours=2)).timestamp()),
        "notification_type": "medicine_reminder",
        "category": "medicine",
        "priority": "normal"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/schedules",
            json=schedule_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📤 Schedule creation API response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Schedule created successfully!")
            print(f"   - ID: {data.get('schedule', {}).get('id')}")
            print(f"   - Title: {data.get('schedule', {}).get('title')}")
        elif response.status_code == 401:
            print("⚠️ Expected: Authentication required")
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Schedule creation API failed: {e}")

def main():
    """Main function"""
    print("🚀 Schedule Data Test Script")
    print("=" * 50)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Check database
    user_schedules = check_database_schedules()
    
    # Create sample schedules if needed
    if not user_schedules:
        print("\n📝 No schedules found, creating sample data...")
        create_sample_schedules()
        check_database_schedules()
    
    # Test API creation
    test_schedule_creation_api()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main() 