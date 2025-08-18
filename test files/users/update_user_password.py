#!/usr/bin/env python3
"""
Script to update password for user with email son12345@gmail.com
"""
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_services.user_service import UserService
from api_services.auth_service import hash_password

def update_user_password():
    """Update password for user with email son12345@gmail.com"""
    email = "son12345@gmail.com"
    new_password = "12345678"
    
    try:
        user_service = UserService()
        
        # Find user by email
        print(f"Searching for user with email: {email}")
        user = user_service.get_user_by_contact(email=email)
        
        if not user:
            print(f"❌ User with email {email} not found!")
            return False
        
        print(f"✅ Found user: {user['full_name']} (ID: {user['id']})")
        print(f"Current password hash: {user['password_hash']}")
        
        # Hash the new password
        new_password_hash = hash_password(new_password)
        print(f"New password hash: {new_password_hash}")
        
        # Update the password
        success = user_service.update_user(
            str(user['id']), 
            password_hash=new_password_hash
        )
        
        if success:
            print(f"✅ Successfully updated password for user {email}")
            print(f"New password: {new_password}")
            return True
        else:
            print(f"❌ Failed to update password for user {email}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating password: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔐 Updating user password...")
    print("=" * 50)
    
    success = update_user_password()
    
    print("=" * 50)
    if success:
        print("🎉 Password update completed successfully!")
    else:
        print("💥 Password update failed!")
        sys.exit(1) 