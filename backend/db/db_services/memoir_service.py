"""
Life Memoir Management Service
Replaces text file storage for life stories with database storage
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_, or_

from db.db_config import get_db
from db.models import LifeMemoir, User, Conversation

logger = logging.getLogger(__name__)

class MemoirDBService:
    """Service for managing life stories and important memories"""
    
    def __init__(self):
        self.logger = logger
    
    async def create_memoir(
        self,
        user_id: str,
        title: str,
        content: str,
        conversation_id: Optional[str] = None,
        date_of_memory: Optional[date] = None,
        categories: Optional[List[str]] = None,
        people_mentioned: Optional[List[str]] = None,
        places_mentioned: Optional[List[str]] = None,
        time_period: Optional[str] = None,
        emotional_tone: Optional[str] = None,
        importance_score: float = 0.0
    ) -> Optional[LifeMemoir]:
        """Create a new life memoir entry"""
        try:
            with get_db() as db:
                memoir = LifeMemoir(
                    user_id=user_id,
                    conversation_id=conversation_id,
                    title=title,
                    content=content,
                    date_of_memory=date_of_memory,
                    categories=categories or [],
                    people_mentioned=people_mentioned or [],
                    places_mentioned=places_mentioned or [],
                    time_period=time_period,
                    emotional_tone=emotional_tone,
                    importance_score=importance_score
                )
                
                db.add(memoir)
                db.commit()
                db.refresh(memoir)
                
                self.logger.info(f"Created memoir {memoir.id} for user {user_id}")
                return memoir
                
        except Exception as e:
            self.logger.error(f"Failed to create memoir: {e}")
            return None
    
    async def get_memoir(self, memoir_id: str) -> Optional[LifeMemoir]:
        """Get a specific memoir by ID"""
        try:
            with get_db() as db:
                memoir = db.query(LifeMemoir).filter(
                    LifeMemoir.id == memoir_id
                ).first()
                return memoir
        except Exception as e:
            self.logger.error(f"Failed to get memoir {memoir_id}: {e}")
            return None
    
    async def get_user_memoirs(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        order_by: str = "extracted_at"
    ) -> List[LifeMemoir]:
        """Get all memoirs for a user"""
        try:
            with get_db() as db:
                query = db.query(LifeMemoir).filter(LifeMemoir.user_id == user_id)
                
                # Order by different fields
                if order_by == "date_of_memory":
                    query = query.order_by(desc(LifeMemoir.date_of_memory))
                elif order_by == "importance":
                    query = query.order_by(desc(LifeMemoir.importance_score))
                else:  # Default to extracted_at
                    query = query.order_by(desc(LifeMemoir.extracted_at))
                
                memoirs = query.offset(offset).limit(limit).all()
                return memoirs
                
        except Exception as e:
            self.logger.error(f"Failed to get memoirs for user {user_id}: {e}")
            return []
    
    async def search_memoirs(
        self,
        user_id: str,
        query: str,
        categories: Optional[List[str]] = None,
        time_period: Optional[str] = None,
        emotional_tone: Optional[str] = None,
        limit: int = 20
    ) -> List[LifeMemoir]:
        """Search memoirs by content, categories, or other attributes"""
        try:
            with get_db() as db:
                db_query = db.query(LifeMemoir).filter(
                    and_(
                        LifeMemoir.user_id == user_id,
                        or_(
                            LifeMemoir.title.ilike(f"%{query}%"),
                            LifeMemoir.content.ilike(f"%{query}%")
                        )
                    )
                )
                
                if categories:
                    db_query = db_query.filter(
                        LifeMemoir.categories.overlap(categories)
                    )
                
                if time_period:
                    db_query = db_query.filter(LifeMemoir.time_period == time_period)
                
                if emotional_tone:
                    db_query = db_query.filter(LifeMemoir.emotional_tone == emotional_tone)
                
                memoirs = db_query.order_by(
                    desc(LifeMemoir.importance_score),
                    desc(LifeMemoir.extracted_at)
                ).limit(limit).all()
                
                return memoirs
                
        except Exception as e:
            self.logger.error(f"Failed to search memoirs for user {user_id}: {e}")
            return []
    
    async def get_memoirs_by_category(
        self,
        user_id: str,
        category: str,
        limit: int = 50
    ) -> List[LifeMemoir]:
        """Get memoirs by specific category"""
        try:
            with get_db() as db:
                memoirs = db.query(LifeMemoir).filter(
                    and_(
                        LifeMemoir.user_id == user_id,
                        LifeMemoir.categories.any(category)
                    )
                ).order_by(desc(LifeMemoir.extracted_at)).limit(limit).all()
                
                return memoirs
                
        except Exception as e:
            self.logger.error(f"Failed to get memoirs by category {category} for user {user_id}: {e}")
            return []
    
    async def get_memoirs_by_time_period(
        self,
        user_id: str,
        time_period: str,
        limit: int = 50
    ) -> List[LifeMemoir]:
        """Get memoirs by time period"""
        try:
            with get_db() as db:
                memoirs = db.query(LifeMemoir).filter(
                    and_(
                        LifeMemoir.user_id == user_id,
                        LifeMemoir.time_period == time_period
                    )
                ).order_by(desc(LifeMemoir.date_of_memory)).limit(limit).all()
                
                return memoirs
                
        except Exception as e:
            self.logger.error(f"Failed to get memoirs by time period {time_period} for user {user_id}: {e}")
            return []
    
    async def get_memoirs_by_people(
        self,
        user_id: str,
        person_name: str,
        limit: int = 50
    ) -> List[LifeMemoir]:
        """Get memoirs that mention a specific person"""
        try:
            with get_db() as db:
                memoirs = db.query(LifeMemoir).filter(
                    and_(
                        LifeMemoir.user_id == user_id,
                        LifeMemoir.people_mentioned.any(person_name)
                    )
                ).order_by(desc(LifeMemoir.extracted_at)).limit(limit).all()
                
                return memoirs
                
        except Exception as e:
            self.logger.error(f"Failed to get memoirs mentioning {person_name} for user {user_id}: {e}")
            return []
    
    async def get_important_memoirs(
        self,
        user_id: str,
        min_importance: float = 0.7,
        limit: int = 20
    ) -> List[LifeMemoir]:
        """Get memoirs with high importance scores"""
        try:
            with get_db() as db:
                memoirs = db.query(LifeMemoir).filter(
                    and_(
                        LifeMemoir.user_id == user_id,
                        LifeMemoir.importance_score >= min_importance
                    )
                ).order_by(desc(LifeMemoir.importance_score)).limit(limit).all()
                
                return memoirs
                
        except Exception as e:
            self.logger.error(f"Failed to get important memoirs for user {user_id}: {e}")
            return []
    
    async def update_memoir(
        self,
        memoir_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        categories: Optional[List[str]] = None,
        people_mentioned: Optional[List[str]] = None,
        places_mentioned: Optional[List[str]] = None,
        time_period: Optional[str] = None,
        emotional_tone: Optional[str] = None,
        importance_score: Optional[float] = None
    ) -> bool:
        """Update memoir information"""
        try:
            with get_db() as db:
                memoir = db.query(LifeMemoir).filter(
                    LifeMemoir.id == memoir_id
                ).first()
                
                if not memoir:
                    return False
                
                updates = {
                    'title': title,
                    'content': content,
                    'categories': categories,
                    'people_mentioned': people_mentioned,
                    'places_mentioned': places_mentioned,
                    'time_period': time_period,
                    'emotional_tone': emotional_tone,
                    'importance_score': importance_score
                }
                
                for key, value in updates.items():
                    if value is not None:
                        setattr(memoir, key, value)
                
                db.commit()
                self.logger.info(f"Updated memoir {memoir_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update memoir {memoir_id}: {e}")
            return False
    
    async def delete_memoir(self, memoir_id: str) -> bool:
        """Delete a memoir"""
        try:
            with get_db() as db:
                memoir = db.query(LifeMemoir).filter(
                    LifeMemoir.id == memoir_id
                ).first()
                
                if not memoir:
                    return False
                
                db.delete(memoir)
                db.commit()
                
                self.logger.info(f"Deleted memoir {memoir_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to delete memoir {memoir_id}: {e}")
            return False
    
    async def get_memoir_categories(self, user_id: str) -> List[str]:
        """Get all unique categories used by a user"""
        try:
            with get_db() as db:
                memoirs = db.query(LifeMemoir.categories).filter(
                    LifeMemoir.user_id == user_id
                ).all()
                
                # Flatten and deduplicate categories
                categories = set()
                for memoir in memoirs:
                    if memoir.categories:
                        categories.update(memoir.categories)
                
                return sorted(list(categories))
                
        except Exception as e:
            self.logger.error(f"Failed to get categories for user {user_id}: {e}")
            return []
    
    async def get_memoir_people(self, user_id: str) -> List[str]:
        """Get all people mentioned in memoirs"""
        try:
            with get_db() as db:
                memoirs = db.query(LifeMemoir.people_mentioned).filter(
                    LifeMemoir.user_id == user_id
                ).all()
                
                # Flatten and deduplicate people
                people = set()
                for memoir in memoirs:
                    if memoir.people_mentioned:
                        people.update(memoir.people_mentioned)
                
                return sorted(list(people))
                
        except Exception as e:
            self.logger.error(f"Failed to get people mentioned for user {user_id}: {e}")
            return []
    
    async def get_memoir_places(self, user_id: str) -> List[str]:
        """Get all places mentioned in memoirs"""
        try:
            with get_db() as db:
                memoirs = db.query(LifeMemoir.places_mentioned).filter(
                    LifeMemoir.user_id == user_id
                ).all()
                
                # Flatten and deduplicate places
                places = set()
                for memoir in memoirs:
                    if memoir.places_mentioned:
                        places.update(memoir.places_mentioned)
                
                return sorted(list(places))
                
        except Exception as e:
            self.logger.error(f"Failed to get places mentioned for user {user_id}: {e}")
            return []
    
    async def get_memoir_timeline(self, user_id: str) -> List[Dict]:
        """Get memoirs organized by time periods"""
        try:
            with get_db() as db:
                memoirs = db.query(LifeMemoir).filter(
                    LifeMemoir.user_id == user_id
                ).order_by(LifeMemoir.date_of_memory).all()
                
                timeline = {}
                for memoir in memoirs:
                    period = memoir.time_period or "Unknown Period"
                    if period not in timeline:
                        timeline[period] = []
                    
                    timeline[period].append({
                        'id': str(memoir.id),
                        'title': memoir.title,
                        'date_of_memory': memoir.date_of_memory.isoformat() if memoir.date_of_memory else None,
                        'importance_score': memoir.importance_score,
                        'emotional_tone': memoir.emotional_tone,
                        'categories': memoir.categories
                    })
                
                # Convert to sorted list
                sorted_timeline = []
                for period, stories in timeline.items():
                    sorted_timeline.append({
                        'time_period': period,
                        'story_count': len(stories),
                        'stories': stories
                    })
                
                return sorted_timeline
                
        except Exception as e:
            self.logger.error(f"Failed to get memoir timeline for user {user_id}: {e}")
            return []
    
    async def export_memoirs_for_family(
        self,
        user_id: str,
        format_type: str = "text"
    ) -> Optional[str]:
        """Export all memoirs in a format suitable for sharing with family"""
        try:
            with get_db() as db:
                memoirs = db.query(LifeMemoir).filter(
                    LifeMemoir.user_id == user_id
                ).order_by(LifeMemoir.date_of_memory).all()
                
                if format_type == "text":
                    export_content = []
                    export_content.append("=== NHỮNG CÂU CHUYỆN ĐỜI CỦA TÔI ===\n")
                    
                    for memoir in memoirs:
                        export_content.append(f"\n{'='*50}")
                        export_content.append(f"Tiêu đề: {memoir.title}")
                        if memoir.date_of_memory:
                            export_content.append(f"Thời gian: {memoir.date_of_memory}")
                        if memoir.time_period:
                            export_content.append(f"Giai đoạn: {memoir.time_period}")
                        if memoir.categories:
                            export_content.append(f"Chủ đề: {', '.join(memoir.categories)}")
                        export_content.append(f"{'='*50}\n")
                        export_content.append(memoir.content)
                        export_content.append("\n")
                    
                    return "\n".join(export_content)
                
                # Can add other formats like JSON, HTML, etc.
                
        except Exception as e:
            self.logger.error(f"Failed to export memoirs for user {user_id}: {e}")
            return None
    
    async def get_memoir_stats(self, user_id: str) -> Dict[str, Any]:
        """Get memoir statistics for a user"""
        try:
            with get_db() as db:
                # Total memoirs
                total_memoirs = db.query(LifeMemoir).filter(
                    LifeMemoir.user_id == user_id
                ).count()
                
                # Most recent memoir
                latest_memoir = db.query(LifeMemoir).filter(
                    LifeMemoir.user_id == user_id
                ).order_by(desc(LifeMemoir.extracted_at)).first()
                
                # Category distribution
                memoirs = db.query(LifeMemoir.categories).filter(
                    LifeMemoir.user_id == user_id
                ).all()
                
                category_count = {}
                for memoir in memoirs:
                    if memoir.categories:
                        for cat in memoir.categories:
                            category_count[cat] = category_count.get(cat, 0) + 1
                
                # Average importance score
                avg_importance = db.query(
                    db.func.avg(LifeMemoir.importance_score)
                ).filter(LifeMemoir.user_id == user_id).scalar() or 0.0
                
                return {
                    'total_memoirs': total_memoirs,
                    'latest_memoir_date': latest_memoir.extracted_at.isoformat() if latest_memoir else None,
                    'category_distribution': category_count,
                    'average_importance_score': float(avg_importance),
                    'categories_count': len(category_count)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get memoir stats for user {user_id}: {e}")
            return {
                'total_memoirs': 0,
                'latest_memoir_date': None,
                'category_distribution': {},
                'average_importance_score': 0.0,
                'categories_count': 0
            } 