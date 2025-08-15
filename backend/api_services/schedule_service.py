"""
Schedule API Service
Handles schedule creation, management, and notifications
"""
from fastapi import FastAPI, HTTPException, Depends
from typing import Optional, List
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from db.db_config import get_db
from db.db_services.notification_service import NotificationDBService
from db.models import NotificationType, User
from api_services.auth_service import get_current_user

logger = logging.getLogger(__name__)

def add_schedule_endpoints(app: FastAPI, notification_db_service, notification_voice_service, websocket_manager):
    """Add schedule-related endpoints to the FastAPI app
    
    Args:
        app: FastAPI application instance
        notification_db_service: Service instance for database notifications
        notification_voice_service: Service instance for voice notifications
        websocket_manager: WebSocket manager for broadcasting
    """
    
    @app.post("/api/schedules")
    async def create_schedule(
        title: str,
        message: str,
        scheduled_at: str,
        notification_type: str,
        category: Optional[str] = None,
        priority: str = "normal",
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
            # Parse scheduled_at datetime
            try:
                scheduled_datetime = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
            
            # Validate notification type
            try:
                notification_type_enum = NotificationType(notification_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid notification type. Must be one of: {[t.value for t in NotificationType]}")
            
            # Create the schedule/notification using the provided service
            notification = await notification_db_service.create_notification(
                user_id=str(current_user.id),
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
            
            # Generate voice notification for immediate testing
            try:
                voice_base64 = await notification_voice_service.generate_voice_notification_base64(message)
                if voice_base64:
                    # Broadcast voice notification to connected clients
                    notification_data = {
                        "type": "schedule_created",
                        "title": title,
                        "message": message,
                        "scheduledAt": scheduled_at,
                        "audioBase64": voice_base64,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    await websocket_manager.broadcast_voice_notification(notification_data)
                    logger.info(f"Schedule created and voice notification broadcasted: {title}")
                else:
                    logger.warning(f"Failed to generate voice for schedule: {title}")
            except Exception as voice_error:
                logger.error(f"Voice generation failed for schedule {title}: {voice_error}")
                # Continue anyway - schedule is still created
            
            return {
                "success": True,
                "message": "Schedule created successfully",
                "schedule": {
                    "id": str(notification.id),
                    "title": notification.title,
                    "message": notification.message,
                    "scheduled_at": notification.scheduled_at.isoformat(),
                    "notification_type": notification.notification_type.value,
                    "category": notification.category,
                    "priority": notification.priority,
                    "created_at": notification.created_at.isoformat()
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
                    "id": str(notification.id),
                    "title": notification.title,
                    "message": notification.message,
                    "scheduled_at": notification.scheduled_at.isoformat(),
                    "notification_type": notification.notification_type.value,
                    "category": notification.category,
                    "priority": notification.priority,
                    "is_sent": notification.is_sent,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at.isoformat()
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
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Delete a schedule
        
        Args:
            schedule_id: ID of schedule to delete
            current_user: Current authenticated user
            db: Database session
            
        Returns:
            Response with deletion status
        """
        try:
            # Get existing notification
            notification = await notification_db_service.get_notification(schedule_id)
            if not notification:
                raise HTTPException(status_code=404, detail="Schedule not found")
            
            # Check if user owns this schedule
            if str(notification.user_id) != str(current_user.id):
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Delete the notification
            success = await notification_db_service.delete_notification(schedule_id)
            
            if not success:
                raise HTTPException(status_code=500, detail="Failed to delete schedule")
            
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
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """Mark a schedule as completed
        
        Args:
            schedule_id: ID of schedule to mark as complete
            current_user: Current authenticated user
            db: Database session
            
        Returns:
            Response with completion status
        """
        try:
            # Get existing notification
            notification = await notification_db_service.get_notification(schedule_id)
            if not notification:
                raise HTTPException(status_code=404, detail="Schedule not found")
            
            # Check if user owns this schedule
            if str(notification.user_id) != str(current_user.id):
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Mark as sent (completed)
            success = await notification_db_service.mark_notification_sent(schedule_id)
            
            if not success:
                raise HTTPException(status_code=500, detail="Failed to mark schedule as complete")
            
            return {
                "success": True,
                "message": "Schedule marked as complete"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error marking schedule complete: {e}")
            raise HTTPException(status_code=500, detail=str(e)) 