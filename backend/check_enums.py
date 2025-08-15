#!/usr/bin/env python3
import psycopg2
from db.db_config import DB_CONFIG

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Check user_type enum values
    cur.execute("SELECT unnest(enum_range(NULL::user_type_enum))")
    print('UserType enum values:')
    for row in cur.fetchall():
        print(f'  {row[0]}')

    # Check conversation_role enum values  
    cur.execute("SELECT unnest(enum_range(NULL::conversation_role_enum))")
    print('\nConversationRole enum values:')
    for row in cur.fetchall():
        print(f'  {row[0]}')

    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    # Try alternative method
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Check if enums exist
        cur.execute("""
            SELECT t.typname, e.enumlabel 
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid 
            WHERE t.typname IN ('user_type_enum', 'conversation_role_enum')
            ORDER BY t.typname, e.enumsortorder
        """)
        
        current_type = None
        for row in cur.fetchall():
            if row[0] != current_type:
                print(f'\n{row[0]} values:')
                current_type = row[0]
            print(f'  {row[1]}')
            
        conn.close()
    except Exception as e2:
        print(f"Alternative method also failed: {e2}") 