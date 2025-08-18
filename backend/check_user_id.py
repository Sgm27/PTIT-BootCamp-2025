#!/usr/bin/env python3
"""
Simple script to check user ID
"""
from db.db_config import get_db
from db.models import User

def check_user_id():
    with get_db() as session:
        try:
            # Check elderly user
            elderly_user = session.query(User).filter(User.email == "son123@gmail.com").first()
            if elderly_user:
                print(f"Elderly User:")
                print(f"  ID: {elderly_user.id}")
                print(f"  Email: {elderly_user.email}")
                print(f"  Name: {elderly_user.full_name}")
                print(f"  Type: {elderly_user.user_type}")
            else:
                print("Elderly user not found")
            
            # Check family user
            family_user = session.query(User).filter(User.email == "son12345@gmail.com").first()
            if family_user:
                print(f"\nFamily User:")
                print(f"  ID: {family_user.id}")
                print(f"  Email: {family_user.email}")
                print(f"  Name: {family_user.full_name}")
                print(f"  Type: {family_user.user_type}")
            else:
                print("Family user not found")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check_user_id() 