#!/usr/bin/env python3
"""
Fix enum column type mismatch in conversation_messages table
"""
import psycopg2
from db.db_config import DB_CONFIG

def fix_enum_column():
    """Fix the enum column type mismatch"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    try:
        print("🔧 Fixing enum column type mismatch...")
        
        # Step 1: Add a temporary column with the correct enum type
        print("Step 1: Adding temporary column with correct enum type...")
        cur.execute("""
        ALTER TABLE conversation_messages 
        ADD COLUMN role_temp conversationrole;
        """)
        
        # Step 2: Update the temporary column with mapped values
        print("Step 2: Mapping values to correct enum...")
        cur.execute("""
        UPDATE conversation_messages 
        SET role_temp = CASE 
            WHEN role = 'user' THEN 'USER'::conversationrole
            WHEN role = 'assistant' THEN 'ASSISTANT'::conversationrole
            WHEN role = 'system' THEN 'SYSTEM'::conversationrole
            ELSE 'USER'::conversationrole
        END;
        """)
        
        # Step 3: Drop the old column
        print("Step 3: Dropping old role column...")
        cur.execute("ALTER TABLE conversation_messages DROP COLUMN role;")
        
        # Step 4: Rename the temporary column
        print("Step 4: Renaming temporary column to role...")
        cur.execute("ALTER TABLE conversation_messages RENAME COLUMN role_temp TO role;")
        
        # Step 5: Add NOT NULL constraint
        print("Step 5: Adding NOT NULL constraint...")
        cur.execute("ALTER TABLE conversation_messages ALTER COLUMN role SET NOT NULL;")
        
        conn.commit()
        print("✅ Enum column fixed successfully!")
        
        # Verify the fix
        print("\n🔍 Verifying the fix...")
        cur.execute("""
        SELECT column_name, data_type, udt_name 
        FROM information_schema.columns 
        WHERE table_name = 'conversation_messages' AND column_name = 'role';
        """)
        
        column_info = cur.fetchone()
        print(f"New role column info: {column_info}")
        
        cur.execute('SELECT DISTINCT role FROM conversation_messages;')
        roles = cur.fetchall()
        print(f"Distinct roles after fix: {[r[0] for r in roles]}")
        
    except Exception as e:
        print(f"❌ Error fixing enum column: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_enum_column() 