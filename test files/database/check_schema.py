#!/usr/bin/env python3
"""
Check database schema for notifications table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_config import get_db
from sqlalchemy import inspect

def check_schema():
    """Check database schema"""
    
    print("=== Database Schema Check ===")
    
    try:
        with get_db() as db:
            inspector = inspect(db.bind)
            
            print("Tables:")
            tables = inspector.get_table_names()
            for table in tables:
                print(f"  - {table}")
            
            print("\nNotification table columns:")
            if 'notifications' in tables:
                columns = inspector.get_columns('notifications')
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
                
                print("\nNotification table foreign keys:")
                fks = inspector.get_foreign_keys('notifications')
                for fk in fks:
                    print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
                
                print("\nNotification table indexes:")
                indexes = inspector.get_indexes('notifications')
                for idx in indexes:
                    print(f"  - {idx['name']}: {idx['column_names']}")
            else:
                print("  ❌ Notifications table not found!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_schema() 