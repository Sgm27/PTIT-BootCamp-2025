"""
Schedule API Service
Handles schedule creation, management, and notifications
"""
from fastapi import FastAPI, HTTPException, Depends, Body, Query
from typing import Optional, List
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from db.db_config import get_db
from db.db_services.notification_service import NotificationDBService
from db.models import NotificationType, User
from api_services.auth_service import get_current_user

def get_user_for_schedule(user_id: Optional[str] = Query(None), current_user: User = Depends(get_current_user)):
    """Get user for schedule operations with authentication bypass support"""
    if user_id:
        # Create a mock user object for authentication bypass
        class MockUser:
            def __init__(self, user_id: str):
                self.id = user_id
        return MockUser(user_id)
    return current_user

logger = logging.getLogger(__name__)

def add_schedule_endpoints(app: FastAPI, notification_db_service, notification_voice_service, websocket_manager):
    """Add schedule-related endpoints to the FastAPI app
    
    Args:
        app: FastAPI application instance
        notification_db_service: Service instance for database notifications
        notification_voice_service: Service instance for voice notifications
        websocket_manager: WebSocket manager for broadcasting
    """
    
    # Public endpoint for testing family connection (no auth required)
    @app.get("/api/public/schedules/{user_id}")
    async def get_public_user_schedules(user_id: str):
        """Get schedules for a user (public endpoint for testing)"""
        try:
            # Get user notifications (schedules) as serialized data
            notifications = await notification_db_service.get_user_notifications_serialized(
                user_id=user_id,
                limit=100  # Get more schedules
            )
            
            schedules = []
            for notification in notifications:
                # Convert notification_type enum to string safely
                notification_type_str = notification["notification_type"].value if hasattr(notification["notification_type"], 'value') else str(notification["notification_type"])
                
                schedules.append({
                    "id": notification["id"],
                    "title": notification["title"],
                    "message": notification["message"],
                    "scheduled_at": notification["scheduled_at"].isoformat(),
                    "notification_type": notification_type_str,
                    "category": notification["category"],
                    "priority": notification["priority"],
                    "is_sent": notification["is_sent"],
                    "is_read": notification["is_read"],
                    "created_at": notification["created_at"].isoformat()
                })
            
            return {
                "success": True,
                "schedules": schedules,
                "total": len(schedules)
            }
            
        except Exception as e:
            logger.error(f"Error getting public user schedules: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/schedules")
    async def create_schedule(
        payload: dict = Body(...),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Create a new schedule/reminder
        
        Args:
            title: Schedule title
            message: Schedule description
            scheduled_at: Scheduled datetime in ISO format
            notification_type: Type of notification
            category: Schedule category
            priority: Priority level
            current_user: Current authenticated user
            db: Database session
            
        Returns:
            Response with created schedule data
        """
        try:
            # Extract fields from JSON body (Android client sends this format)
            title = payload.get("title")
            message = payload.get("message")
            category = payload.get("category")
            priority = payload.get("priority", "normal")
            notification_type = payload.get("notification_type")

            # scheduled_at may be ISO string or Unix timestamp
            scheduled_at = payload.get("scheduled_at")

            if not title or not notification_type or not scheduled_at:
                raise HTTPException(status_code=400, detail="Missing required fields: title, notification_type, scheduled_at")

            # Parse scheduled_at datetime
            try:
                if isinstance(scheduled_at, (int, float)):
                    # Unix timestamp seconds
                    scheduled_datetime = datetime.utcfromtimestamp(float(scheduled_at))
                elif isinstance(scheduled_at, str):
                    scheduled_datetime = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
                else:
                    raise ValueError("Invalid type for scheduled_at")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
            
            # Validate notification type
            try:
                notification_type_enum = NotificationType(notification_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid notification type. Must be one of: {[t.value for t in NotificationType]}")
            
            # Create the schedule/notification using the provided service
            target_user_id = str(payload.get("elderly_id") or current_user.id)

            notification = await notification_db_service.create_notification(
                user_id=target_user_id,
                notification_type=notification_type_enum,
                title=title,
                message=message,
                scheduled_at=scheduled_datetime,
                priority=priority,
                category=category,
                has_voice=True
            )
            
            if not notification:
                raise HTTPException(status_code=500, detail="Failed to create schedule")
            
            logger.info(f"Schedule created successfully: {title} (scheduled for {scheduled_datetime})")
            
            return {
                "success": True,
                "message": "Schedule created successfully",
                "schedule": {
                    "id": notification["id"],
                    "title": notification["title"],
                    "message": notification["message"],
                    "scheduled_at": notification["scheduled_at"].isoformat(),
                    "notification_type": notification["notification_type"],
                    "category": notification["category"],
                    "priority": notification["priority"],
                    "created_at": notification["created_at"].isoformat()
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/schedules")
    async def get_user_schedules(
        user_id: Optional[str] = None,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Get schedules for a user
        
        Args:
            user_id: User ID to get schedules for (defaults to current user)
            current_user: Current authenticated user
            db: Database session
            
        Returns:
            Response with user schedules
        """
        try:
            # Use provided user_id or current user's ID
            target_user_id = user_id if user_id else str(current_user.id)
            
            # Get user notifications (schedules)
            notifications = await notification_db_service.get_user_notifications(
                user_id=target_user_id,
                limit=100  # Get more schedules
            )
            
            schedules = []
            for notification in notifications:
                schedules.append({
                    "id": notification["id"],
                    "title": notification["title"],
                    "message": notification["message"],
                    "scheduled_at": notification["scheduled_at"].isoformat(),
                    "notification_type": notification["notification_type"],
                    "category": notification["category"],
                    "priority": notification["priority"],
                    "is_sent": notification["is_sent"],
                    "is_read": notification["is_read"],
                    "created_at": notification["created_at"].isoformat()
                })
            
            return {
                "success": True,
                "schedules": schedules,
                "total": len(schedules)
            }
            
        except Exception as e:
            logger.error(f"Error getting user schedules: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.put("/api/schedules/{schedule_id}")
    async def update_schedule(
        schedule_id: str,
        title: Optional[str] = None,
        message: Optional[str] = None,
        scheduled_at: Optional[str] = None,
        notification_type: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Update an existing schedule
        
        Args:
            schedule_id: ID of schedule to update
            title: New title (optional)
            message: New message (optional)
            scheduled_at: New scheduled datetime (optional)
            notification_type: New notification type (optional)
            category: New category (optional)
            priority: New priority (optional)
            current_user: Current authenticated user
            db: Database session
            
        Returns:
            Response with updated schedule data
        """
        try:
            # Get existing notification
            notification = await notification_db_service.get_notification(schedule_id)
            if not notification:
                raise HTTPException(status_code=404, detail="Schedule not found")
            
            # Check if user owns this schedule
            if str(notification.user_id) != str(current_user.id):
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Prepare update data
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if message is not None:
                update_data["message"] = message
            if scheduled_at is not None:
                try:
                    scheduled_datetime = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
                    update_data["scheduled_at"] = scheduled_datetime
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid datetime format")
            if notification_type is not None:
                try:
                    notification_type_enum = NotificationType(notification_type)
                    update_data["notification_type"] = notification_type_enum
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid notification type")
            if category is not None:
                update_data["category"] = category
            if priority is not None:
                update_data["priority"] = priority
            
            # Update the notification
            updated_notification = await notification_db_service.update_notification(
                notification_id=schedule_id,
                update_data=update_data
            )
            
            if not updated_notification:
                raise HTTPException(status_code=500, detail="Failed to update schedule")
            
            return {
                "success": True,
                "message": "Schedule updated successfully",
                "schedule": {
                    "id": str(updated_notification.id),
                    "title": updated_notification.title,
                    "message": updated_notification.message,
                    "scheduled_at": updated_notification.scheduled_at.isoformat(),
                    "notification_type": updated_notification.notification_type.value,
                    "category": updated_notification.category,
                    "priority": updated_notification.priority,
                    "updated_at": updated_notification.updated_at.isoformat()
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating schedule: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/api/schedules/{schedule_id}")
    async def delete_schedule(
        schedule_id: str,
        current_user: User = Depends(get_user_for_schedule)
    ):
        """Delete a schedule
        
        Args:
            schedule_id: ID of schedule to delete
            current_user: Current authenticated user
            
        Returns:
            Response with deletion status
        """
        try:
            logger.info(f"Attempting to delete schedule: {schedule_id} for user: {current_user.id}")
            
            # Get existing notification using direct database query
            from db.db_config import get_db
            from db.models import Notification
            
            # Use explicit transaction management
            from sqlalchemy.orm import sessionmaker
            from db.db_config import engine
            
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            
            try:
                notification = db.query(Notification).filter(
                    Notification.id == schedule_id
                ).first()
                
                if not notification:
                    logger.warning(f"Schedule not found: {schedule_id}")
                    raise HTTPException(status_code=404, detail="Schedule not found")
                
                logger.info(f"Found schedule: {notification.title} (ID: {notification.id}) for user: {notification.user_id}")
                
                # Check if user owns this schedule
                if str(notification.user_id) != str(current_user.id):
                    logger.warning(f"Access denied: user {current_user.id} trying to delete schedule owned by {notification.user_id}")
                    raise HTTPException(status_code=403, detail="Access denied")
                
                # Delete the notification directly
                logger.info(f"Marking notification for deletion: {notification.id}")
                db.delete(notification)
                logger.info(f"Committing transaction...")
                db.commit()
                logger.info(f"Transaction committed successfully")
                
                # Verify deletion immediately
                notification_verify = db.query(Notification).filter(
                    Notification.id == schedule_id
                ).first()
                
                if notification_verify:
                    logger.error(f"❌ Notification still exists after commit: {notification_verify.title}")
                    db.rollback()
                    raise HTTPException(status_code=500, detail="Failed to delete schedule - still exists after commit")
                else:
                    logger.info(f"✅ Successfully deleted schedule: {schedule_id}")
                    
            except Exception as e:
                logger.error(f"Error in transaction: {e}")
                db.rollback()
                raise
            finally:
                db.close()
            
            return {
                "success": True,
                "message": "Schedule deleted successfully"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting schedule: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/schedules/{schedule_id}/complete")
    async def mark_schedule_complete(
        schedule_id: str,
        current_user: User = Depends(get_user_for_schedule)
    ):
        """Mark a schedule as completed
        
        Args:
            schedule_id: ID of schedule to mark as complete
            current_user: Current authenticated user
            
        Returns:
            Response with completion status
        """
        try:
            logger.info(f"Attempting to mark schedule as complete: {schedule_id} for user: {current_user.id}")
            
            # Get existing notification using direct database query
            from db.db_config import get_db
            from db.models import Notification
            
            # Use explicit transaction management
            from sqlalchemy.orm import sessionmaker
            from db.db_config import engine
            
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            db = SessionLocal()
            
            try:
                notification = db.query(Notification).filter(
                    Notification.id == schedule_id
                ).first()
                
                if not notification:
                    logger.warning(f"Schedule not found: {schedule_id}")
                    raise HTTPException(status_code=404, detail="Schedule not found")
                
                logger.info(f"Found schedule: {notification.title} (ID: {notification.id}) for user: {notification.user_id}")
                
                # Check if user owns this schedule
                if str(notification.user_id) != str(current_user.id):
                    logger.warning(f"Access denied: user {current_user.id} trying to mark schedule owned by {notification.user_id}")
                    raise HTTPException(status_code=403, detail="Access denied")
                
                # Mark as sent (completed) directly
                notification.is_sent = True
                db.commit()
                
                logger.info(f"Successfully marked schedule as complete: {schedule_id}")
                
            except Exception as e:
                logger.error(f"Error in transaction: {e}")
                db.rollback()
                raise
            finally:
                db.close()
            
            return {
                "success": True,
                "message": "Schedule marked as complete"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error marking schedule complete: {e}")
            raise HTTPException(status_code=500, detail=str(e)) 