#!/usr/bin/env python3
"""
Debug API endpoint directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_services.schedule_service import add_schedule_endpoints
from db.db_services.notification_service import NotificationDBService
from fastapi import FastAPI
from fastapi.testclient import TestClient

def debug_api_endpoint():
    """Debug API endpoint directly"""
    
    print("=== Debug API Endpoint Directly ===")
    
    try:
        # Create test app
        app = FastAPI()
        
        # Initialize services
        notification_db_service = NotificationDBService()
        
        # Add endpoints
        add_schedule_endpoints(app, notification_db_service, None, None)
        
        # Create test client
        client = TestClient(app)
        
        # Test notification ID
        notification_id = "27f31895-7e79-4f3d-9ac3-a3c0411859f8"
        user_id = "6dbbe787-9645-4203-94c1-3e5b1e9ca54c"
        
        print(f"1. Testing delete endpoint with:")
        print(f"   - Notification ID: {notification_id}")
        print(f"   - User ID: {user_id}")
        
        # Test delete endpoint
        response = client.delete(f"/api/schedules/{notification_id}?user_id={user_id}")
        
        print(f"\n2. Delete endpoint response:")
        print(f"   - Status: {response.status_code}")
        print(f"   - Body: {response.json()}")
        
        if response.status_code == 200:
            print(f"   ✅ Delete endpoint returned success")
        else:
            print(f"   ❌ Delete endpoint failed")
            return
        
        print(f"\n3. Checking if notification still exists...")
        
        # Check if notification still exists
        from db.db_config import get_db
        from db.models import Notification
        
        with get_db() as db:
            notification_after = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification_after:
                print(f"   ❌ Still exists: {notification_after.title}")
                print(f"   - ID: {notification_after.id}")
                print(f"   - User ID: {notification_after.user_id}")
            else:
                print(f"   ✅ Successfully deleted!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api_endpoint() 