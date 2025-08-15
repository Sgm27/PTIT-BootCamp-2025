"""
Schedule Notification Service
Automatically sends voice notifications when schedules are due
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List
import json

logger = logging.getLogger(__name__)

class ScheduleNotificationService:
    """Service for automatically sending schedule notifications"""
    
    def __init__(self, notification_db_service, notification_voice_service, websocket_manager):
        self.notification_db_service = notification_db_service
        self.notification_voice_service = notification_voice_service
        self.websocket_manager = websocket_manager
        self.is_running = False
        self.check_interval = 60  # Check every minute
        
    async def start_service(self):
        """Start the schedule notification service"""
        if self.is_running:
            logger.warning("Schedule notification service is already running")
            return
        
        self.is_running = True
        logger.info("Starting schedule notification service")
        
        try:
            while self.is_running:
                await self.check_due_schedules()
                await asyncio.sleep(self.check_interval)
        except Exception as e:
            logger.error(f"Error in schedule notification service: {e}")
            self.is_running = False
        finally:
            logger.info("Schedule notification service stopped")
    
    async def stop_service(self):
        """Stop the schedule notification service"""
        self.is_running = False
        logger.info("Stopping schedule notification service")
    
    async def check_due_schedules(self):
        """Check for schedules that are due and send notifications"""
        try:
            # Get current time
            now = datetime.now()
            
            # Get notifications that are due (within the last 5 minutes to avoid missing any)
            due_time = now - timedelta(minutes=5)
            
            # Get due notifications from database
            due_notifications = await self.get_due_notifications(due_time)
            
            for notification in due_notifications:
                try:
                    await self.send_schedule_notification(notification)
                    
                    # Mark notification as sent
                    await self.notification_db_service.update_notification_status(
                        str(notification.id),
                        is_sent=True,
                        sent_at=now
                    )
                    
                    logger.info(f"Sent schedule notification: {notification.title}")
                    
                except Exception as e:
                    logger.error(f"Failed to send notification {notification.id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error checking due schedules: {e}")
    
    async def get_due_notifications(self, due_time: datetime) -> List:
        """Get notifications that are due for sending"""
        try:
            # This would need to be implemented in the notification service
            # For now, we'll return an empty list
            # TODO: Implement get_due_notifications method
            return []
        except Exception as e:
            logger.error(f"Error getting due notifications: {e}")
            return []
    
    async def send_schedule_notification(self, notification):
        """Send a schedule notification via voice and WebSocket"""
        try:
            # Generate voice notification text
            voice_text = self.generate_notification_text(notification)
            
            # Generate voice audio
            audio_base64 = await self.notification_voice_service.generate_voice_notification_base64(voice_text)
            
            if audio_base64:
                # Prepare notification data for WebSocket broadcast
                notification_data = {
                    "type": "schedule_notification",
                    "schedule_id": str(notification.id),
                    "title": notification.title,
                    "message": notification.message,
                    "category": notification.category or "other",
                    "audio_base64": audio_base64,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Broadcast to all connected WebSocket clients
                await self.websocket_manager.broadcast_voice_notification(notification_data)
                
                logger.info(f"Broadcasted schedule notification: {notification.title}")
            else:
                logger.warning(f"Failed to generate voice for notification: {notification.title}")
                
        except Exception as e:
            logger.error(f"Error sending schedule notification: {e}")
    
    def generate_notification_text(self, notification) -> str:
        """Generate appropriate voice notification text"""
        time_str = datetime.now().strftime("%H:%M")
        
        if notification.category == "medicine":
            return f"Đã đến giờ {time_str}. {notification.title}. {notification.message}"
        elif notification.category == "appointment":
            return f"Đã đến giờ {time_str}. {notification.title}. {notification.message}"
        elif notification.category == "exercise":
            return f"Đã đến giờ {time_str}. {notification.title}. {notification.message}"
        elif notification.category == "meal":
            return f"Đã đến giờ {time_str}. {notification.title}. {notification.message}"
        else:
            return f"Đã đến giờ {time_str}. {notification.title}. {notification.message}"
    
    def get_service_status(self) -> dict:
        """Get the current status of the service"""
        return {
            "running": self.is_running,
            "check_interval": self.check_interval,
            "last_check": datetime.now().isoformat() if self.is_running else None
        }

# Global instance
schedule_notification_service: Optional[ScheduleNotificationService] = None

def get_schedule_notification_service(
    notification_db_service,
    notification_voice_service,
    websocket_manager
) -> ScheduleNotificationService:
    """Get or create the global schedule notification service instance"""
    global schedule_notification_service
    
    if schedule_notification_service is None:
        schedule_notification_service = ScheduleNotificationService(
            notification_db_service,
            notification_voice_service,
            websocket_manager
        )
    
    return schedule_notification_service 