#!/usr/bin/env python3
"""
Check and fix enum issue in conversation_messages table
"""
import psycopg2
from db.db_config import DB_CONFIG

def check_enum_types():
    """Check enum types in database"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Check enum types
        cur.execute("""
        SELECT t.typname, e.enumlabel 
        FROM pg_type t 
        JOIN pg_enum e ON t.oid = e.enumtypid 
        WHERE t.typname LIKE '%conversation%' OR t.typname LIKE '%role%'
        ORDER BY t.typname, e.enumsortorder;
        """)
        
        enums = cur.fetchall()
        print('Enum types in database:')
        for enum_type, label in enums:
            print(f'  {enum_type}: {label}')
            
        # Check column type for role
        cur.execute("""
        SELECT column_name, data_type, udt_name 
        FROM information_schema.columns 
        WHERE table_name = 'conversation_messages' AND column_name = 'role';
        """)
        
        column_info = cur.fetchone()
        if column_info:
            print(f'\nRole column info: {column_info}')
        
        # Check distinct roles
        cur.execute('SELECT DISTINCT role FROM conversation_messages;')
        roles = cur.fetchall()
        print(f'\nDistinct roles in data: {[r[0] for r in roles]}')
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def fix_enum_issue():
    """Fix enum issue by updating the enum definition"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        # Check if conversationrole enum exists
        cur.execute("""
        SELECT EXISTS (
            SELECT 1 FROM pg_type 
            WHERE typname = 'conversationrole'
        );
        """)
        
        enum_exists = cur.fetchone()[0]
        print(f"ConversationRole enum exists: {enum_exists}")
        
        if enum_exists:
            # Check current enum values
            cur.execute("""
            SELECT e.enumlabel 
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid 
            WHERE t.typname = 'conversationrole'
            ORDER BY e.enumsortorder;
            """)
            
            current_values = [row[0] for row in cur.fetchall()]
            print(f"Current enum values: {current_values}")
            
            # Check if we need to add missing values
            required_values = ['USER', 'ASSISTANT', 'SYSTEM']
            missing_values = [v for v in required_values if v not in current_values]
            
            if missing_values:
                print(f"Adding missing enum values: {missing_values}")
                for value in missing_values:
                    try:
                        cur.execute(f"ALTER TYPE conversationrole ADD VALUE '{value}';")
                        print(f"Added enum value: {value}")
                    except Exception as e:
                        print(f"Error adding {value}: {e}")
            
            # Update existing data to use uppercase values
            print("Updating existing data to use uppercase enum values...")
            cur.execute("UPDATE conversation_messages SET role = 'USER' WHERE role = 'user';")
            user_updated = cur.rowcount
            
            cur.execute("UPDATE conversation_messages SET role = 'ASSISTANT' WHERE role = 'assistant';")
            assistant_updated = cur.rowcount
            
            cur.execute("UPDATE conversation_messages SET role = 'SYSTEM' WHERE role = 'system';")
            system_updated = cur.rowcount
            
            print(f"Updated {user_updated} user messages, {assistant_updated} assistant messages, {system_updated} system messages")
            
            conn.commit()
            print("✅ Enum issue fixed successfully!")
            
        else:
            print("ConversationRole enum does not exist")
            
    except Exception as e:
        print(f"Error fixing enum: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("🔍 Checking enum types...")
    check_enum_types()
    
    print("\n🔧 Fixing enum issue...")
    fix_enum_issue()
    
    print("\n🔍 Checking again after fix...")
    check_enum_types() 