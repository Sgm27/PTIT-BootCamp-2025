#!/usr/bin/env python3
"""
Script to check enum values in database
"""
import psycopg2
from db.db_config import DB_CONFIG

def check_enum_values():
    """Check enum values in database"""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Check notification_type_enum values
        cur.execute("""
            SELECT unnest(enum_range(NULL::notification_type_enum)) as enum_value
        """)
        
        enum_values = cur.fetchall()
        print("📋 Notification Type Enum Values:")
        for value in enum_values:
            print(f"  - {value[0]}")
        
        # Check user_type_enum values
        cur.execute("""
            SELECT unnest(enum_range(NULL::user_type_enum)) as enum_value
        """)
        
        enum_values = cur.fetchall()
        print(f"\n📋 User Type Enum Values:")
        for value in enum_values:
            print(f"  - {value[0]}")
        
        # Close connection
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking enum values: {e}")
        return False

if __name__ == "__main__":
    success = check_enum_values()
    if success:
        print("\n✅ Enum values check completed!")
    else:
        print("\n❌ Failed to check enum values.")
        exit(1) 