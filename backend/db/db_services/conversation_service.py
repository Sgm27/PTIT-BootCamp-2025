"""
Conversation Management Service
Replaces JSON file storage for conversation history with database storage
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_

from db.db_config import get_db
from db.models import (
    Conversation, ConversationMessage, User, ConversationRole
)

logger = logging.getLogger(__name__)

class ConversationService:
    """Service for managing conversations and message history"""
    
    def __init__(self):
        self.logger = logger
    
    async def create_conversation(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        title: Optional[str] = None
    ) -> Optional[Conversation]:
        """Create a new conversation"""
        try:
            with get_db() as db:
                conversation = Conversation(
                    user_id=user_id,
                    session_id=session_id,
                    title=title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                
                db.add(conversation)
                db.commit()
                db.refresh(conversation)
                
                self.logger.info(f"Created conversation {conversation.id} for user {user_id}")
                return conversation
                
        except Exception as e:
            self.logger.error(f"Failed to create conversation: {e}")
            return None
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation with all messages"""
        try:
            with get_db() as db:
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
                
                if conversation:
                    # Detach from session to avoid session issues
                    db.expunge(conversation)
                
                return conversation
                
        except Exception as e:
            self.logger.error(f"Failed to get conversation {conversation_id}: {e}")
            return None
    
    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        include_inactive: bool = False
    ) -> List[Conversation]:
        """Get user's conversations"""
        try:
            with get_db() as db:
                query = db.query(Conversation).filter(Conversation.user_id == user_id)
                
                if not include_inactive:
                    query = query.filter(Conversation.is_active == True)
                
                conversations = query.order_by(
                    desc(Conversation.started_at)
                ).offset(offset).limit(limit).all()
                
                # Detach objects from session to avoid session issues
                for conv in conversations:
                    db.expunge(conv)
                
                return conversations
                
        except Exception as e:
            self.logger.error(f"Failed to get conversations for user {user_id}: {e}")
            return []
    
    async def get_active_conversation(
        self,
        user_id: str,
        session_id: Optional[str] = None
    ) -> Optional[Conversation]:
        """Get user's currently active conversation"""
        try:
            with get_db() as db:
                query = db.query(Conversation).filter(
                    and_(
                        Conversation.user_id == user_id,
                        Conversation.is_active == True,
                        Conversation.ended_at.is_(None)
                    )
                )
                
                if session_id:
                    query = query.filter(Conversation.session_id == session_id)
                
                conversation = query.order_by(
                    desc(Conversation.started_at)
                ).first()
                
                return conversation
                
        except Exception as e:
            self.logger.error(f"Failed to get active conversation for user {user_id}: {e}")
            return None
    
    async def add_message(
        self,
        conversation_id: str,
        role: ConversationRole,
        content: str,
        has_audio: bool = False,
        audio_file_path: Optional[str] = None,
        processing_time_ms: Optional[float] = None
    ) -> Optional[ConversationMessage]:
        """Add a message to conversation"""
        try:
            with get_db() as db:
                # Get conversation and current message count
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
                
                if not conversation:
                    return None
                
                # Get next message order
                last_message = db.query(ConversationMessage).filter(
                    ConversationMessage.conversation_id == conversation_id
                ).order_by(desc(ConversationMessage.message_order)).first()
                
                next_order = (last_message.message_order + 1) if last_message else 1
                
                # Create message
                message = ConversationMessage(
                    conversation_id=conversation_id,
                    role=role,
                    content=content,
                    message_order=next_order,
                    has_audio=has_audio,
                    audio_file_path=audio_file_path,
                    processing_time_ms=processing_time_ms
                )
                
                db.add(message)
                
                # Update conversation metadata
                conversation.total_messages = next_order
                
                db.commit()
                db.refresh(message)
                
                self.logger.info(f"Added message to conversation {conversation_id}")
                return message
                
        except Exception as e:
            self.logger.error(f"Failed to add message to conversation {conversation_id}: {e}")
            return None
    
    async def end_conversation(
        self,
        conversation_id: str,
        summary: Optional[str] = None,
        topics: Optional[List[str]] = None
    ) -> bool:
        """End a conversation and set summary"""
        try:
            with get_db() as db:
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
                
                if not conversation:
                    return False
                
                conversation.ended_at = datetime.utcnow()
                conversation.is_active = False
                
                if summary:
                    conversation.conversation_summary = summary
                
                if topics:
                    conversation.topics_discussed = topics
                
                db.commit()
                self.logger.info(f"Ended conversation {conversation_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to end conversation {conversation_id}: {e}")
            return False
    
    async def get_conversation_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[ConversationMessage]:
        """Get messages from a conversation"""
        try:
            with get_db() as db:
                query = db.query(ConversationMessage).filter(
                    ConversationMessage.conversation_id == conversation_id
                ).order_by(ConversationMessage.message_order)
                
                if limit:
                    query = query.offset(offset).limit(limit)
                
                messages = query.all()
                
                # Detach from session to avoid session issues
                for message in messages:
                    db.expunge(message)
                
                return messages
                
        except Exception as e:
            self.logger.error(f"Failed to get messages for conversation {conversation_id}: {e}")
            return []
    
    async def search_conversations(
        self,
        user_id: str,
        query: str,
        limit: int = 20
    ) -> List[Dict]:
        """Search conversations by content"""
        try:
            with get_db() as db:
                # Search in conversation summaries and message content
                conversations = db.query(Conversation).join(
                    ConversationMessage, Conversation.id == ConversationMessage.conversation_id
                ).filter(
                    and_(
                        Conversation.user_id == user_id,
                        ConversationMessage.content.contains(query)
                    )
                ).distinct().order_by(desc(Conversation.started_at)).limit(limit).all()
                
                results = []
                for conv in conversations:
                    results.append({
                        'conversation_id': str(conv.id),
                        'title': conv.title,
                        'started_at': conv.started_at.isoformat(),
                        'ended_at': conv.ended_at.isoformat() if conv.ended_at else None,
                        'summary': conv.conversation_summary,
                        'total_messages': conv.total_messages
                    })
                
                return results
                
        except Exception as e:
            self.logger.error(f"Failed to search conversations for user {user_id}: {e}")
            return []
    
    async def get_conversation_history_for_export(
        self,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> List[Dict]:
        """Get conversation history in format compatible with existing memoir extraction"""
        try:
            with get_db() as db:
                query = db.query(ConversationMessage).join(
                    Conversation, ConversationMessage.conversation_id == Conversation.id
                ).filter(Conversation.user_id == user_id)
                
                if conversation_id:
                    query = query.filter(Conversation.id == conversation_id)
                
                messages = query.order_by(
                    Conversation.started_at,
                    ConversationMessage.message_order
                ).all()
                
                # Convert to format expected by memoir extraction service
                history = []
                for message in messages:
                    history.append({
                        'role': message.role.value,
                        'text': message.content,
                        'timestamp': message.timestamp.isoformat()
                    })
                
                return history
                
        except Exception as e:
            self.logger.error(f"Failed to get conversation history for export: {e}")
            return []
    
    async def update_conversation_metadata(
        self,
        conversation_id: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        topics: Optional[List[str]] = None
    ) -> bool:
        """Update conversation metadata"""
        try:
            with get_db() as db:
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
                
                if not conversation:
                    return False
                
                if title:
                    conversation.title = title
                if summary:
                    conversation.conversation_summary = summary
                if topics:
                    conversation.topics_discussed = topics
                
                db.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update conversation metadata {conversation_id}: {e}")
            return False
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation and all its messages"""
        try:
            with get_db() as db:
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id
                ).first()
                
                if not conversation:
                    return False
                
                # Delete all messages first (cascade should handle this but being explicit)
                db.query(ConversationMessage).filter(
                    ConversationMessage.conversation_id == conversation_id
                ).delete()
                
                # Delete conversation
                db.delete(conversation)
                db.commit()
                
                self.logger.info(f"Deleted conversation {conversation_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to delete conversation {conversation_id}: {e}")
            return False
    
    async def get_conversation_stats(self, user_id: str) -> Dict[str, Any]:
        """Get conversation statistics for a user"""
        try:
            with get_db() as db:
                # Total conversations
                total_conversations = db.query(Conversation).filter(
                    Conversation.user_id == user_id
                ).count()
                
                # Active conversations
                active_conversations = db.query(Conversation).filter(
                    and_(
                        Conversation.user_id == user_id,
                        Conversation.is_active == True
                    )
                ).count()
                
                # Total messages
                total_messages = db.query(ConversationMessage).join(
                    Conversation, ConversationMessage.conversation_id == Conversation.id
                ).filter(Conversation.user_id == user_id).count()
                
                # Most recent conversation
                latest_conversation = db.query(Conversation).filter(
                    Conversation.user_id == user_id
                ).order_by(desc(Conversation.started_at)).first()
                
                return {
                    'total_conversations': total_conversations,
                    'active_conversations': active_conversations,
                    'total_messages': total_messages,
                    'latest_conversation_date': latest_conversation.started_at.isoformat() if latest_conversation else None
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get conversation stats for user {user_id}: {e}")
            return {
                'total_conversations': 0,
                'active_conversations': 0,
                'total_messages': 0,
                'latest_conversation_date': None
            } 