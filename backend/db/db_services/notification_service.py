"""
Notification Management Service
Handles all types of notifications, reminders, and voice notifications
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_, or_

from db.db_config import get_db
from db.models import Notification, User, NotificationType

logger = logging.getLogger(__name__)

class NotificationDBService:
    """Service for managing notifications and reminders"""
    
    def __init__(self):
        self.logger = logger
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        scheduled_at: datetime,
        priority: str = "normal",
        category: Optional[str] = None,
        related_record_id: Optional[str] = None,
        has_voice: bool = False,
        voice_file_path: Optional[str] = None
    ) -> Optional[Notification]:
        """Create a new notification"""
        try:
            with get_db() as db:
                notification = Notification(
                    user_id=user_id,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    scheduled_at=scheduled_at,
                    priority=priority,
                    category=category,
                    related_record_id=related_record_id,
                    has_voice=has_voice,
                    voice_file_path=voice_file_path
                )
                
                db.add(notification)
                db.commit()
                db.refresh(notification)
                
                self.logger.info(f"Created notification {notification.id} for user {user_id}")
                return notification
                
        except Exception as e:
            self.logger.error(f"Failed to create notification: {e}")
            return None
    
    async def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get a specific notification"""
        try:
            with get_db() as db:
                notification = db.query(Notification).filter(
                    Notification.id == notification_id
                ).first()
                return notification
        except Exception as e:
            self.logger.error(f"Failed to get notification {notification_id}: {e}")
            return None
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
        notification_type: Optional[NotificationType] = None
    ) -> List[Notification]:
        """Get notifications for a user"""
        try:
            with get_db() as db:
                query = db.query(Notification).filter(Notification.user_id == user_id)
                
                if unread_only:
                    query = query.filter(Notification.is_read == False)
                
                if notification_type:
                    query = query.filter(Notification.notification_type == notification_type)
                
                notifications = query.order_by(
                    desc(Notification.scheduled_at)
                ).offset(offset).limit(limit).all()
                
                return notifications
                
        except Exception as e:
            self.logger.error(f"Failed to get notifications for user {user_id}: {e}")
            return []
    
    async def get_pending_notifications(
        self,
        user_id: Optional[str] = None,
        before_time: Optional[datetime] = None
    ) -> List[Notification]:
        """Get notifications that are scheduled but not yet sent"""
        try:
            with get_db() as db:
                query = db.query(Notification).filter(Notification.is_sent == False)
                
                if user_id:
                    query = query.filter(Notification.user_id == user_id)
                
                if before_time:
                    query = query.filter(Notification.scheduled_at <= before_time)
                else:
                    query = query.filter(Notification.scheduled_at <= datetime.utcnow())
                
                notifications = query.order_by(Notification.scheduled_at).all()
                return notifications
                
        except Exception as e:
            self.logger.error(f"Failed to get pending notifications: {e}")
            return []
    
    async def mark_notification_sent(
        self,
        notification_id: str,
        voice_file_path: Optional[str] = None
    ) -> bool:
        """Mark a notification as sent"""
        try:
            with get_db() as db:
                notification = db.query(Notification).filter(
                    Notification.id == notification_id
                ).first()
                
                if not notification:
                    return False
                
                notification.is_sent = True
                notification.sent_at = datetime.utcnow()
                
                if voice_file_path:
                    notification.voice_file_path = voice_file_path
                    notification.voice_generated_at = datetime.utcnow()
                    notification.has_voice = True
                
                db.commit()
                self.logger.info(f"Marked notification {notification_id} as sent")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to mark notification {notification_id} as sent: {e}")
            return False
    
    async def mark_notification_read(self, notification_id: str) -> bool:
        """Mark a notification as read"""
        try:
            with get_db() as db:
                notification = db.query(Notification).filter(
                    Notification.id == notification_id
                ).first()
                
                if not notification:
                    return False
                
                notification.is_read = True
                db.commit()
                
                self.logger.info(f"Marked notification {notification_id} as read")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to mark notification {notification_id} as read: {e}")
            return False
    
    async def mark_all_read(self, user_id: str) -> bool:
        """Mark all notifications as read for a user"""
        try:
            with get_db() as db:
                db.query(Notification).filter(
                    and_(
                        Notification.user_id == user_id,
                        Notification.is_read == False
                    )
                ).update({'is_read': True})
                
                db.commit()
                self.logger.info(f"Marked all notifications as read for user {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to mark all notifications as read for user {user_id}: {e}")
            return False
    
    async def create_medicine_reminder(
        self,
        user_id: str,
        medicine_name: str,
        dosage: str,
        scheduled_time: datetime,
        medicine_id: Optional[str] = None
    ) -> Optional[Notification]:
        """Create a medicine reminder notification"""
        try:
            title = f"Nhắc nhở uống thuốc: {medicine_name}"
            message = f"Đã đến giờ uống thuốc {medicine_name} - Liều dùng: {dosage}"
            
            return await self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.MEDICINE_REMINDER,
                title=title,
                message=message,
                scheduled_at=scheduled_time,
                priority="high",
                category="medicine",
                related_record_id=medicine_id,
                has_voice=True
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create medicine reminder: {e}")
            return None
    
    async def create_appointment_reminder(
        self,
        user_id: str,
        appointment_details: str,
        scheduled_time: datetime,
        appointment_id: Optional[str] = None
    ) -> Optional[Notification]:
        """Create an appointment reminder notification"""
        try:
            title = "Nhắc nhở lịch khám"
            message = f"Bạn có lịch khám: {appointment_details}"
            
            return await self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.APPOINTMENT_REMINDER,
                title=title,
                message=message,
                scheduled_at=scheduled_time,
                priority="high",
                category="appointment",
                related_record_id=appointment_id,
                has_voice=True
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create appointment reminder: {e}")
            return None
    
    async def create_health_check_reminder(
        self,
        user_id: str,
        check_type: str,
        scheduled_time: datetime
    ) -> Optional[Notification]:
        """Create a health check reminder"""
        try:
            title = f"Nhắc nhở kiểm tra sức khỏe: {check_type}"
            message = f"Đã đến giờ kiểm tra {check_type}. Hãy đo và ghi lại kết quả."
            
            return await self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.HEALTH_CHECK,
                title=title,
                message=message,
                scheduled_at=scheduled_time,
                priority="normal",
                category="health",
                has_voice=True
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create health check reminder: {e}")
            return None
    
    async def create_emergency_notification(
        self,
        user_id: str,
        emergency_message: str,
        contact_info: Optional[str] = None
    ) -> Optional[Notification]:
        """Create an emergency notification"""
        try:
            title = "CẢNH BÁO KHẨN CẤP"
            message = emergency_message
            if contact_info:
                message += f"\nLiên hệ ngay: {contact_info}"
            
            return await self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.EMERGENCY,
                title=title,
                message=message,
                scheduled_at=datetime.utcnow(),
                priority="urgent",
                category="emergency",
                has_voice=True
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create emergency notification: {e}")
            return None
    
    async def create_custom_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        scheduled_time: datetime,
        priority: str = "normal",
        has_voice: bool = False
    ) -> Optional[Notification]:
        """Create a custom notification"""
        try:
            return await self.create_notification(
                user_id=user_id,
                notification_type=NotificationType.CUSTOM,
                title=title,
                message=message,
                scheduled_at=scheduled_time,
                priority=priority,
                category="custom",
                has_voice=has_voice
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create custom notification: {e}")
            return None
    
    async def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification"""
        try:
            with get_db() as db:
                notification = db.query(Notification).filter(
                    Notification.id == notification_id
                ).first()
                
                if not notification:
                    return False
                
                db.delete(notification)
                db.commit()
                
                self.logger.info(f"Deleted notification {notification_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to delete notification {notification_id}: {e}")
            return False
    
    async def get_notifications_by_type(
        self,
        user_id: str,
        notification_type: NotificationType,
        limit: int = 20
    ) -> List[Notification]:
        """Get notifications by type"""
        try:
            with get_db() as db:
                notifications = db.query(Notification).filter(
                    and_(
                        Notification.user_id == user_id,
                        Notification.notification_type == notification_type
                    )
                ).order_by(desc(Notification.scheduled_at)).limit(limit).all()
                
                return notifications
                
        except Exception as e:
            self.logger.error(f"Failed to get notifications by type for user {user_id}: {e}")
            return []
    
    async def get_notifications_by_priority(
        self,
        user_id: str,
        priority: str,
        unread_only: bool = True
    ) -> List[Notification]:
        """Get notifications by priority level"""
        try:
            with get_db() as db:
                query = db.query(Notification).filter(
                    and_(
                        Notification.user_id == user_id,
                        Notification.priority == priority
                    )
                )
                
                if unread_only:
                    query = query.filter(Notification.is_read == False)
                
                notifications = query.order_by(
                    desc(Notification.scheduled_at)
                ).all()
                
                return notifications
                
        except Exception as e:
            self.logger.error(f"Failed to get notifications by priority for user {user_id}: {e}")
            return []
    
    async def update_notification(
        self,
        notification_id: str,
        **updates
    ) -> bool:
        """Update notification information"""
        try:
            with get_db() as db:
                notification = db.query(Notification).filter(
                    Notification.id == notification_id
                ).first()
                
                if not notification:
                    return False
                
                for key, value in updates.items():
                    if hasattr(notification, key) and value is not None:
                        setattr(notification, key, value)
                
                db.commit()
                self.logger.info(f"Updated notification {notification_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update notification {notification_id}: {e}")
            return False
    
    async def reschedule_notification(
        self,
        notification_id: str,
        new_scheduled_time: datetime
    ) -> bool:
        """Reschedule a notification"""
        try:
            return await self.update_notification(
                notification_id,
                scheduled_at=new_scheduled_time,
                is_sent=False,
                sent_at=None
            )
        except Exception as e:
            self.logger.error(f"Failed to reschedule notification {notification_id}: {e}")
            return False
    
    async def get_notification_stats(self, user_id: str) -> Dict[str, Any]:
        """Get notification statistics for a user"""
        try:
            with get_db() as db:
                # Total notifications
                total_notifications = db.query(Notification).filter(
                    Notification.user_id == user_id
                ).count()
                
                # Unread notifications
                unread_notifications = db.query(Notification).filter(
                    and_(
                        Notification.user_id == user_id,
                        Notification.is_read == False
                    )
                ).count()
                
                # Pending notifications
                pending_notifications = db.query(Notification).filter(
                    and_(
                        Notification.user_id == user_id,
                        Notification.is_sent == False,
                        Notification.scheduled_at > datetime.utcnow()
                    )
                ).count()
                
                # Notifications by type
                notification_types = {}
                for notification_type in NotificationType:
                    count = db.query(Notification).filter(
                        and_(
                            Notification.user_id == user_id,
                            Notification.notification_type == notification_type
                        )
                    ).count()
                    notification_types[notification_type.value] = count
                
                # Recent notifications
                recent_count = db.query(Notification).filter(
                    and_(
                        Notification.user_id == user_id,
                        Notification.created_at >= datetime.utcnow() - timedelta(days=7)
                    )
                ).count()
                
                return {
                    'total_notifications': total_notifications,
                    'unread_notifications': unread_notifications,
                    'pending_notifications': pending_notifications,
                    'notification_types': notification_types,
                    'recent_notifications_7_days': recent_count
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get notification stats for user {user_id}: {e}")
            return {
                'total_notifications': 0,
                'unread_notifications': 0,
                'pending_notifications': 0,
                'notification_types': {},
                'recent_notifications_7_days': 0
            }
    
    async def cleanup_old_notifications(
        self,
        user_id: str,
        days_old: int = 30,
        keep_unread: bool = True
    ) -> int:
        """Clean up old notifications"""
        try:
            with get_db() as db:
                cutoff_date = datetime.utcnow() - timedelta(days=days_old)
                
                query = db.query(Notification).filter(
                    and_(
                        Notification.user_id == user_id,
                        Notification.created_at < cutoff_date
                    )
                )
                
                if keep_unread:
                    query = query.filter(Notification.is_read == True)
                
                deleted_count = query.count()
                query.delete()
                db.commit()
                
                self.logger.info(f"Cleaned up {deleted_count} old notifications for user {user_id}")
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old notifications for user {user_id}: {e}")
            return 0 