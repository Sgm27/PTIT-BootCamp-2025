"""
Session Management Service
Replaces JSON file storage for user sessions with database storage
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from db.db_config import get_db
from db.models import UserSession, User

logger = logging.getLogger(__name__)

class SessionDBService:
    """Service for managing user sessions and WebSocket connections"""
    
    def __init__(self):
        self.logger = logger
    
    async def create_session(
        self,
        user_id: str,
        session_handle: str,
        websocket_session_id: Optional[str] = None,
        device_info: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[UserSession]:
        """Create a new user session"""
        try:
            with get_db() as db:
                # End any existing active sessions for this user
                await self.end_user_sessions(user_id)
                
                session = UserSession(
                    user_id=user_id,
                    session_handle=session_handle,
                    websocket_session_id=websocket_session_id,
                    device_info=device_info or {},
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                db.add(session)
                db.commit()
                db.refresh(session)
                
                self.logger.info(f"Created session {session.id} for user {user_id}")
                return session
                
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}")
            return None
    
    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get a session by ID"""
        try:
            with get_db() as db:
                session = db.query(UserSession).filter(
                    UserSession.id == session_id
                ).first()
                return session
        except Exception as e:
            self.logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    async def get_session_by_handle(self, session_handle: str) -> Optional[UserSession]:
        """Get a session by session handle"""
        try:
            with get_db() as db:
                session = db.query(UserSession).filter(
                    and_(
                        UserSession.session_handle == session_handle,
                        UserSession.is_active == True
                    )
                ).first()
                return session
        except Exception as e:
            self.logger.error(f"Failed to get session by handle {session_handle}: {e}")
            return None
    
    async def get_active_user_session(self, user_id: str) -> Optional[UserSession]:
        """Get the active session for a user"""
        try:
            with get_db() as db:
                session = db.query(UserSession).filter(
                    and_(
                        UserSession.user_id == user_id,
                        UserSession.is_active == True,
                        UserSession.ended_at.is_(None)
                    )
                ).order_by(desc(UserSession.started_at)).first()
                
                return session
        except Exception as e:
            self.logger.error(f"Failed to get active session for user {user_id}: {e}")
            return None
    
    async def update_session_activity(
        self,
        session_handle: str,
        websocket_session_id: Optional[str] = None
    ) -> bool:
        """Update session last activity timestamp"""
        try:
            with get_db() as db:
                session = db.query(UserSession).filter(
                    UserSession.session_handle == session_handle
                ).first()
                
                if not session:
                    return False
                
                session.last_activity = datetime.utcnow()
                
                if websocket_session_id:
                    session.websocket_session_id = websocket_session_id
                
                db.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update session activity {session_handle}: {e}")
            return False
    
    async def end_session(self, session_handle: str) -> bool:
        """End a specific session"""
        try:
            with get_db() as db:
                session = db.query(UserSession).filter(
                    UserSession.session_handle == session_handle
                ).first()
                
                if not session:
                    return False
                
                session.ended_at = datetime.utcnow()
                session.is_active = False
                
                db.commit()
                self.logger.info(f"Ended session {session.id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to end session {session_handle}: {e}")
            return False
    
    async def end_user_sessions(self, user_id: str) -> bool:
        """End all active sessions for a user"""
        try:
            with get_db() as db:
                active_sessions = db.query(UserSession).filter(
                    and_(
                        UserSession.user_id == user_id,
                        UserSession.is_active == True
                    )
                ).all()
                
                for session in active_sessions:
                    session.ended_at = datetime.utcnow()
                    session.is_active = False
                
                db.commit()
                self.logger.info(f"Ended {len(active_sessions)} sessions for user {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to end sessions for user {user_id}: {e}")
            return False
    
    async def get_user_sessions(
        self,
        user_id: str,
        active_only: bool = False,
        limit: int = 20
    ) -> List[UserSession]:
        """Get sessions for a user"""
        try:
            with get_db() as db:
                query = db.query(UserSession).filter(UserSession.user_id == user_id)
                
                if active_only:
                    query = query.filter(UserSession.is_active == True)
                
                sessions = query.order_by(
                    desc(UserSession.started_at)
                ).limit(limit).all()
                
                return sessions
                
        except Exception as e:
            self.logger.error(f"Failed to get sessions for user {user_id}: {e}")
            return []
    
    async def cleanup_expired_sessions(self, timeout_hours: int = 24) -> int:
        """Clean up expired sessions"""
        try:
            with get_db() as db:
                cutoff_time = datetime.utcnow() - timedelta(hours=timeout_hours)
                
                expired_sessions = db.query(UserSession).filter(
                    and_(
                        UserSession.is_active == True,
                        UserSession.last_activity < cutoff_time
                    )
                ).all()
                
                for session in expired_sessions:
                    session.ended_at = datetime.utcnow()
                    session.is_active = False
                
                db.commit()
                
                count = len(expired_sessions)
                self.logger.info(f"Cleaned up {count} expired sessions")
                return count
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0
    
    async def get_session_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get session statistics"""
        try:
            with get_db() as db:
                query = db.query(UserSession)
                
                if user_id:
                    query = query.filter(UserSession.user_id == user_id)
                
                # Total sessions
                total_sessions = query.count()
                
                # Active sessions
                active_sessions = query.filter(UserSession.is_active == True).count()
                
                # Recent sessions (last 7 days)
                recent_sessions = query.filter(
                    UserSession.started_at >= datetime.utcnow() - timedelta(days=7)
                ).count()
                
                # Average session duration for completed sessions
                completed_sessions = query.filter(
                    UserSession.ended_at.isnot(None)
                ).all()
                
                if completed_sessions:
                    durations = [
                        (session.ended_at - session.started_at).total_seconds() 
                        for session in completed_sessions
                    ]
                    avg_duration = sum(durations) / len(durations) / 60  # in minutes
                else:
                    avg_duration = 0
                
                return {
                    'total_sessions': total_sessions,
                    'active_sessions': active_sessions,
                    'recent_sessions_7_days': recent_sessions,
                    'average_duration_minutes': round(avg_duration, 2),
                    'completed_sessions': len(completed_sessions)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get session stats: {e}")
            return {
                'total_sessions': 0,
                'active_sessions': 0,
                'recent_sessions_7_days': 0,
                'average_duration_minutes': 0,
                'completed_sessions': 0
            }
    
    async def is_session_valid(self, session_handle: str, timeout_hours: int = 24) -> bool:
        """Check if a session is still valid"""
        try:
            session = await self.get_session_by_handle(session_handle)
            
            if not session or not session.is_active:
                return False
            
            # Check if session has timed out
            timeout_limit = datetime.utcnow() - timedelta(hours=timeout_hours)
            if session.last_activity < timeout_limit:
                # Auto-expire the session
                await self.end_session(session_handle)
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate session {session_handle}: {e}")
            return False
    
    async def get_active_sessions_count(self) -> int:
        """Get count of all active sessions"""
        try:
            with get_db() as db:
                count = db.query(UserSession).filter(
                    UserSession.is_active == True
                ).count()
                return count
        except Exception as e:
            self.logger.error(f"Failed to get active sessions count: {e}")
            return 0
    
    async def get_sessions_by_timeframe(
        self,
        start_time: datetime,
        end_time: datetime,
        user_id: Optional[str] = None
    ) -> List[UserSession]:
        """Get sessions within a specific timeframe"""
        try:
            with get_db() as db:
                query = db.query(UserSession).filter(
                    and_(
                        UserSession.started_at >= start_time,
                        UserSession.started_at <= end_time
                    )
                )
                
                if user_id:
                    query = query.filter(UserSession.user_id == user_id)
                
                sessions = query.order_by(UserSession.started_at).all()
                return sessions
                
        except Exception as e:
            self.logger.error(f"Failed to get sessions by timeframe: {e}")
            return []
    
    async def update_session_device_info(
        self,
        session_handle: str,
        device_info: Dict
    ) -> bool:
        """Update session device information"""
        try:
            with get_db() as db:
                session = db.query(UserSession).filter(
                    UserSession.session_handle == session_handle
                ).first()
                
                if not session:
                    return False
                
                session.device_info = device_info
                db.commit()
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update session device info {session_handle}: {e}")
            return False 