#!/usr/bin/env python3
"""
Script to check table structure
"""
import psycopg2
from db.db_config import DB_CONFIG

def check_table_structure():
    """Check table structure"""
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Check notifications table structure
        cur.execute("""
            SELECT column_name, data_type, udt_name, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'notifications'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("📋 Notifications table structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} ({col[2]}) - Nullable: {col[3]}")
        
        # Check enum values
        cur.execute("""
            SELECT enumlabel 
            FROM pg_enum 
            WHERE enumtypid = (
                SELECT oid FROM pg_type WHERE typname = 'notification_type_enum'
            )
        """)
        
        enum_values = cur.fetchall()
        print(f"\n🔍 notification_type_enum values:")
        for val in enum_values:
            print(f"  - {val[0]}")
        
        # Close connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_table_structure() 