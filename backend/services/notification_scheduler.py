"""
Notification Scheduler Service
Handles scheduled notifications and sends them at the appropriate time
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from db.db_services.notification_service import NotificationDBService
from services.notification_voice_service import NotificationVoiceService
from services.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

class NotificationScheduler:
    """Scheduler for handling scheduled notifications"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.notification_service = NotificationDBService()
        self.voice_service = NotificationVoiceService()
        self.websocket_manager = WebSocketManager()
        self.logger = logger
        self.is_running = False
    
    async def check_and_send_scheduled_notifications(self):
        """Check for notifications that need to be sent and send them"""
        try:
            self.logger.info("🔔 Checking for scheduled notifications to send...")
            
            # Get all unsent notifications that are due
            current_time = datetime.utcnow()
            notifications = await self._get_due_notifications(current_time)
            
            if not notifications:
                self.logger.info("No notifications due for sending")
                return
            
            self.logger.info(f"Found {len(notifications)} notifications to send")
            
            for notification in notifications:
                await self._send_notification(notification)
                
        except Exception as e:
            self.logger.error(f"Error checking scheduled notifications: {e}")
    
    async def _get_due_notifications(self, current_time: datetime) -> List[dict]:
        """Get notifications that are due to be sent"""
        try:
            # Get all unsent notifications that are due
            notifications = await self.notification_service.get_due_notifications(current_time)
            
            # Convert to list of dictionaries
            due_notifications = []
            for notification in notifications:
                due_notifications.append({
                    "id": str(notification.id),
                    "user_id": str(notification.user_id),
                    "title": notification.title,
                    "message": notification.message,
                    "scheduled_at": notification.scheduled_at,
                    "notification_type": notification.notification_type,
                    "category": notification.category,
                    "priority": notification.priority,
                    "is_sent": notification.is_sent,
                    "is_read": notification.is_read,
                    "created_at": notification.created_at
                })
            
            return due_notifications
            
        except Exception as e:
            self.logger.error(f"Error getting due notifications: {e}")
            return []
    
    async def _send_notification(self, notification: dict):
        """Send a single notification"""
        try:
            notification_id = notification["id"]
            user_id = notification["user_id"]
            title = notification["title"]
            message = notification["message"]
            notification_type = notification["notification_type"]
            
            self.logger.info(f"Sending notification {notification_id} to user {user_id}: {title}")
            
            # Check if user has voice notifications enabled
            # For now, we'll generate voice for all notifications
            # TODO: Check user preferences for voice notifications
            
            # Generate voice notification
            try:
                voice_base64 = await self.voice_service.generate_voice_notification_base64(message)
                
                if voice_base64:
                    # Broadcast voice notification to connected clients
                    notification_data = {
                        "type": "scheduled_notification",
                        "notification_id": notification_id,
                        "title": title,
                        "message": message,
                        "notification_type": notification_type,
                        "audioBase64": voice_base64,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    await self.websocket_manager.broadcast_voice_notification(notification_data)
                    self.logger.info(f"Voice notification sent for {notification_id}")
                else:
                    self.logger.warning(f"Failed to generate voice for notification {notification_id}")
                    
            except Exception as voice_error:
                self.logger.error(f"Voice generation failed for notification {notification_id}: {voice_error}")
            
            # Mark notification as sent
            await self._mark_notification_sent(notification_id)
            
        except Exception as e:
            self.logger.error(f"Error sending notification {notification.get('id', 'unknown')}: {e}")
    
    async def _mark_notification_sent(self, notification_id: str):
        """Mark a notification as sent"""
        try:
            # Update notification in database
            success = await self.notification_service.update_notification_status(
                notification_id=notification_id,
                is_sent=True,
                sent_at=datetime.utcnow()
            )
            
            if success:
                self.logger.info(f"Marked notification {notification_id} as sent")
            else:
                self.logger.warning(f"Failed to mark notification {notification_id} as sent")
                
        except Exception as e:
            self.logger.error(f"Error marking notification {notification_id} as sent: {e}")
    
    def start_scheduler(self):
        """Start the notification scheduler"""
        try:
            if self.is_running:
                self.logger.warning("Notification scheduler is already running")
                return
            
            # Check for notifications every minute
            self.scheduler.add_job(
                self.check_and_send_scheduled_notifications,
                trigger=IntervalTrigger(minutes=1),
                id='check_scheduled_notifications',
                name='Check Scheduled Notifications',
                replace_existing=True,
                max_instances=1
            )
            
            self.scheduler.start()
            self.is_running = True
            self.logger.info("✅ Notification scheduler started successfully")
            
        except Exception as e:
            self.logger.error(f"Error starting notification scheduler: {e}")
    
    def stop_scheduler(self):
        """Stop the notification scheduler"""
        try:
            if not self.is_running:
                return
            
            self.scheduler.shutdown()
            self.is_running = False
            self.logger.info("Notification scheduler stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping notification scheduler: {e}")
    
    async def manual_check_notifications(self):
        """Manually trigger notification check"""
        try:
            self.logger.info("Manual notification check triggered")
            await self.check_and_send_scheduled_notifications()
            return {"success": True, "message": "Manual notification check completed"}
        except Exception as e:
            self.logger.error(f"Error in manual notification check: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}

# Global instance
notification_scheduler = NotificationScheduler() 