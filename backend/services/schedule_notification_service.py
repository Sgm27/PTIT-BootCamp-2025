"""
Schedule Notification Service
Automatically sends voice notifications when schedules are due
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from db.db_config import get_db
from db.db_services.notification_service import NotificationDBService
from db.models import NotificationType
from services.voice_notification_service import VoiceNotificationService

logger = logging.getLogger(__name__)

class ScheduleNotificationService:
    """Service for automatically sending schedule notifications"""
    
    def __init__(self, notification_db_service: NotificationDBService, voice_service: VoiceNotificationService):
        self.notification_db_service = notification_db_service
        self.voice_service = voice_service
        self.is_running = False
        self.check_interval = 60  # Check every 60 seconds
        
    async def start_service(self):
        """Start the schedule notification service"""
        if self.is_running:
            logger.warning("Schedule notification service is already running")
            return
            
        self.is_running = True
        logger.info("Starting schedule notification service")
        
        while self.is_running:
            try:
                await self.check_and_send_notifications()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in schedule notification service: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def stop_service(self):
        """Stop the schedule notification service"""
        self.is_running = False
        logger.info("Stopping schedule notification service")
    
    async def check_and_send_notifications(self):
        """Check for due notifications and send them"""
        try:
            # Get notifications that are due (within the next 5 minutes)
            now = datetime.utcnow()
            due_time = now + timedelta(minutes=5)
            
            # Get all pending notifications
            notifications = await self.notification_db_service.get_pending_notifications()
            
            for notification in notifications:
                try:
                    # Check if notification is due
                    if notification.scheduled_at <= due_time and not notification.is_sent:
                        await self.send_schedule_notification(notification)
                except Exception as e:
                    logger.error(f"Error processing notification {notification.id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error checking notifications: {e}")
    
    async def send_schedule_notification(self, notification):
        """Send a specific schedule notification"""
        try:
            logger.info(f"Sending schedule notification: {notification.title}")
            
            # Generate voice notification
            notification_text = f"Lịch trình: {notification.title}. {notification.message}"
            
            voice_base64 = await self.voice_service.generate_voice_notification_base64(notification_text)
            
            if voice_base64:
                # Mark notification as sent
                await self.notification_db_service.mark_notification_sent(str(notification.id))
                
                # Broadcast to connected clients (if WebSocket manager is available)
                # This would be handled by the main application
                logger.info(f"Voice notification generated and sent for: {notification.title}")
            else:
                logger.warning(f"Failed to generate voice for notification: {notification.title}")
                
        except Exception as e:
            logger.error(f"Error sending schedule notification {notification.id}: {e}")
    
    async def send_immediate_notification(self, user_id: str, title: str, message: str, notification_type: str = "custom"):
        """Send an immediate notification (for testing)"""
        try:
            logger.info(f"Sending immediate notification to user {user_id}: {title}")
            
            # Create notification in database
            notification = await self.notification_db_service.create_notification(
                user_id=user_id,
                notification_type=NotificationType(notification_type),
                title=title,
                message=message,
                scheduled_at=datetime.utcnow(),
                priority="high",
                category="immediate",
                has_voice=True
            )
            
            if notification:
                # Send immediately
                await self.send_schedule_notification(notification)
                return True
            else:
                logger.error("Failed to create immediate notification")
                return False
                
        except Exception as e:
            logger.error(f"Error sending immediate notification: {e}")
            return False

# Global instance
schedule_notification_service: Optional[ScheduleNotificationService] = None

def get_schedule_notification_service() -> Optional[ScheduleNotificationService]:
    """Get the global schedule notification service instance"""
    return schedule_notification_service

def initialize_schedule_notification_service(notification_db_service: NotificationDBService, voice_service: VoiceNotificationService):
    """Initialize the global schedule notification service"""
    global schedule_notification_service
    schedule_notification_service = ScheduleNotificationService(notification_db_service, voice_service)
    logger.info("Schedule notification service initialized")
    return schedule_notification_service 