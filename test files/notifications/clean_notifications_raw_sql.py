#!/usr/bin/env python3
"""
Script to clean notifications using raw SQL
"""
import psycopg2
from db.db_config import DB_CONFIG

def clean_notifications_raw_sql():
    """Clean notifications using raw SQL"""
    
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
        
        # Delete all notifications for this user
        cur.execute("DELETE FROM notifications WHERE user_id = %s", (elderly_user_id,))
        deleted_count = cur.rowcount
        print(f"🗑️ Deleted {deleted_count} notifications")
        
        # Commit the deletion
        conn.commit()
        print("✅ All notifications deleted successfully")
        
        # Close connection
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning notifications: {e}")
        return False

if __name__ == "__main__":
    success = clean_notifications_raw_sql()
    if success:
        print("\n✅ Notifications cleaned successfully!")
        print("You can now recreate schedules with correct enum values.")
    else:
        print("\n❌ Failed to clean notifications.")
        exit(1) 