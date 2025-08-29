#!/usr/bin/env python3
"""
Test user schedules API
"""
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration
API_BASE = "https://backend-bootcamp.sonktx.online"
DB_CONFIG = {
    'host': '13.215.139.225',
    'port': 5432,
    'database': 'healthcare_ai',
    'user': 'postgres',
    'password': 'postgres'
}

def test_user_schedules():
    """Test user schedules API"""
    user_id = "6dbbe787-9645-4203-94c1-3e5b1e9ca54c"  # son123@gmail.com
    
    print(f"🔍 Testing schedules for user: {user_id}")
    
    # Test public endpoint
    try:
        response = requests.get(f"{API_BASE}/api/public/schedules/{user_id}", timeout=10)
        print(f"📤 Public API response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   - Success: {data.get('success')}")
            print(f"   - Total: {data.get('total')}")
            print(f"   - Schedules count: {len(data.get('schedules', []))}")
            
            schedules = data.get('schedules', [])
            if schedules:
                print("   - Sample schedules:")
                for i, schedule in enumerate(schedules[:3], 1):
                    print(f"     {i}. {schedule.get('title')} - {schedule.get('scheduled_at')}")
            else:
                print("   - No schedules returned")
        else:
            print(f"   - Error: {response.text}")
    except Exception as e:
        print(f"❌ Public API error: {e}")
    
    # Check database directly
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT COUNT(*) as count
            FROM notifications 
            WHERE user_id = %s AND notification_type IN ('medicine_reminder', 'appointment_reminder', 'health_check', 'custom')
        """, (user_id,))
        result = cur.fetchone()
        db_count = result['count']
        
        print(f"\n🗄️ Database check:")
        print(f"   - Schedules in DB: {db_count}")
        
        if db_count > 0:
            cur.execute("""
                SELECT title, scheduled_at, notification_type
                FROM notifications 
                WHERE user_id = %s AND notification_type IN ('medicine_reminder', 'appointment_reminder', 'health_check', 'custom')
                ORDER BY created_at DESC
                LIMIT 3
            """, (user_id,))
            sample_schedules = cur.fetchall()
            
            print("   - Sample schedules from DB:")
            for i, schedule in enumerate(sample_schedules, 1):
                print(f"     {i}. {schedule['title']} ({schedule['notification_type']}) - {schedule['scheduled_at']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    test_user_schedules() 