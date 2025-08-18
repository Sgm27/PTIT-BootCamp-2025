#!/usr/bin/env python3
"""
Script to check schedules directly in database
"""
import psycopg2
from db.db_config import DB_CONFIG

def check_schedules_direct():
    """Check schedules directly in database"""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get elderly user ID
        cur.execute("SELECT id FROM users WHERE email = %s", ("son123@gmail.com",))
        user_result = cur.fetchone()
        
        if not user_result:
            print("❌ Elderly user not found")
            return False
        
        elderly_user_id = user_result[0]
        print(f"✅ Found elderly user ID: {elderly_user_id}")
        
        # Check all notifications for this user
        cur.execute("""
            SELECT id, title, message, scheduled_at, notification_type, category, is_sent, created_at
            FROM notifications 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """, (elderly_user_id,))
        
        notifications = cur.fetchall()
        print(f"\n📋 Found {len(notifications)} notifications in database:")
        
        if notifications:
            for i, notification in enumerate(notifications):
                print(f"\n  {i+1}. Notification:")
                print(f"     - ID: {notification[0]}")
                print(f"     - Title: {notification[1]}")
                print(f"     - Message: {notification[2]}")
                print(f"     - Scheduled At: {notification[3]}")
                print(f"     - Type: {notification[4]}")
                print(f"     - Category: {notification[5]}")
                print(f"     - Is Sent: {notification[6]}")
                print(f"     - Created At: {notification[7]}")
        else:
            print("  No notifications found")
        
        # Close connection
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking schedules: {e}")
        return False

if __name__ == "__main__":
    success = check_schedules_direct()
    if success:
        print("\n✅ Database check completed!")
    else:
        print("\n❌ Failed to check database.")
        exit(1) 