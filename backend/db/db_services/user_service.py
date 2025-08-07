"""
User Management Service
Handles user registration, authentication, and profile management for both elderly users and family members
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_

from db.db_config import get_db
from db.models import (
    User, ElderlyProfile, FamilyProfile, FamilyRelationship,
    UserType, RelationshipType
)

logger = logging.getLogger(__name__)

class UserService:
    """Service for managing users and their relationships"""
    
    def __init__(self):
        self.logger = logger
    
    # User CRUD Operations
    def create_user(
        self,
        user_type: UserType,
        full_name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        date_of_birth: Optional[date] = None,
        gender: Optional[str] = None,
        address: Optional[str] = None,
        **kwargs
    ) -> Optional[User]:
        """
        Create a new user account
        
        Args:
            user_type: Whether this is an elderly user or family member
            full_name: User's full name
            email: Email address (optional)
            phone: Phone number (optional)
            date_of_birth: Date of birth
            gender: Gender
            address: Home address
            **kwargs: Additional user attributes
        
        Returns:
            Created User object or None if failed
        """
        try:
            with get_db() as db:
                # Check for existing user with same email/phone
                if email or phone:
                    existing = db.query(User).filter(
                        or_(User.email == email, User.phone == phone)
                    ).first()
                    if existing:
                        raise ValueError("User with this email or phone already exists")
                
                # Create user
                user_data = {
                    'user_type': user_type,
                    'full_name': full_name,
                    'email': email,
                    'phone': phone,
                    'date_of_birth': date_of_birth,
                    'gender': gender,
                    'address': address,
                    **kwargs
                }
                
                user = User(**user_data)
                db.add(user)
                db.flush()  # Get the user ID
                
                # Create type-specific profile
                if user_type == UserType.ELDERLY:
                    profile = ElderlyProfile(user_id=user.id)
                    db.add(profile)
                else:
                    profile = FamilyProfile(user_id=user.id)
                    db.add(profile)
                
                db.commit()
                
                # Return user data instead of object to avoid session issues
                user_data = {
                    'id': user.id,
                    'user_type': user.user_type,
                    'full_name': user.full_name,
                    'email': user.email,
                    'phone': user.phone,
                    'date_of_birth': user.date_of_birth,
                    'gender': user.gender,
                    'address': user.address,
                    'created_at': user.created_at,
                    'is_active': user.is_active
                }
                
                self.logger.info(f"Created {user_type.value} user: {user.id}")
                
                # Create a detached object with the data
                new_user = User(**user_data)
                new_user.id = user.id
                new_user.created_at = user.created_at
                return new_user
                
        except IntegrityError as e:
            self.logger.error(f"Failed to create user - integrity error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to create user: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID with all related profiles"""
        try:
            with get_db() as db:
                user = db.query(User).options(
                    joinedload(User.elderly_profiles),
                    joinedload(User.family_profiles)
                ).filter(User.id == user_id).first()
                return user
        except Exception as e:
            self.logger.error(f"Failed to get user {user_id}: {e}")
            return None
    
    def get_user_by_contact(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Optional[User]:
        """Get user by email or phone number"""
        try:
            with get_db() as db:
                query = db.query(User)
                if email:
                    query = query.filter(User.email == email)
                elif phone:
                    query = query.filter(User.phone == phone)
                else:
                    return None
                
                user = query.options(
                    joinedload(User.elderly_profiles),
                    joinedload(User.family_profiles)
                ).first()
                
                if not user:
                    return None
                
                # Create detached copy to avoid session issues
                user_data = {
                    'id': user.id,
                    'user_type': user.user_type,
                    'full_name': user.full_name,
                    'email': user.email,
                    'phone': user.phone,
                    'date_of_birth': user.date_of_birth,
                    'gender': user.gender,
                    'address': user.address,
                    'password_hash': user.password_hash,
                    'is_active': user.is_active,
                    'created_at': user.created_at,
                    'updated_at': user.updated_at,
                    'last_login': user.last_login
                }
                
                # Create detached user object
                detached_user = User(**user_data)
                detached_user.id = user.id
                detached_user.created_at = user.created_at
                detached_user.updated_at = user.updated_at
                return detached_user
                
        except Exception as e:
            self.logger.error(f"Failed to get user by contact: {e}")
            return None
    
    def update_user(self, user_id: str, **updates) -> bool:
        """Update user information"""
        try:
            with get_db() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    return False
                
                for key, value in updates.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                
                user.updated_at = datetime.utcnow()
                db.commit()
                self.logger.info(f"Updated user {user_id}")
                return True
        except Exception as e:
            self.logger.error(f"Failed to update user {user_id}: {e}")
            return False
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        return self.update_user(user_id, is_active=False)
    
    # Profile Management
    def update_elderly_profile(
        self,
        user_id: str,
        medical_conditions: Optional[List[str]] = None,
        current_medications: Optional[Dict] = None,
        allergies: Optional[List[str]] = None,
        emergency_contact: Optional[str] = None,
        doctor_info: Optional[Dict] = None,
        **kwargs
    ) -> bool:
        """Update elderly user's medical profile"""
        try:
            with get_db() as db:
                profile = db.query(ElderlyProfile).filter(
                    ElderlyProfile.user_id == user_id
                ).first()
                
                if not profile:
                    return False
                
                updates = {
                    'medical_conditions': medical_conditions,
                    'current_medications': current_medications,
                    'allergies': allergies,
                    'emergency_contact': emergency_contact,
                    'doctor_info': doctor_info,
                    **kwargs
                }
                
                for key, value in updates.items():
                    if value is not None and hasattr(profile, key):
                        setattr(profile, key, value)
                
                profile.updated_at = datetime.utcnow()
                db.commit()
                self.logger.info(f"Updated elderly profile for user {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update elderly profile {user_id}: {e}")
            return False
    
    def update_family_profile(
        self,
        user_id: str,
        occupation: Optional[str] = None,
        workplace: Optional[str] = None,
        is_primary_caregiver: Optional[bool] = None,
        care_responsibilities: Optional[List[str]] = None,
        availability_schedule: Optional[Dict] = None,
        **kwargs
    ) -> bool:
        """Update family member's profile"""
        try:
            with get_db() as db:
                profile = db.query(FamilyProfile).filter(
                    FamilyProfile.user_id == user_id
                ).first()
                
                if not profile:
                    return False
                
                updates = {
                    'occupation': occupation,
                    'workplace': workplace,
                    'is_primary_caregiver': is_primary_caregiver,
                    'care_responsibilities': care_responsibilities,
                    'availability_schedule': availability_schedule,
                    **kwargs
                }
                
                for key, value in updates.items():
                    if value is not None and hasattr(profile, key):
                        setattr(profile, key, value)
                
                profile.updated_at = datetime.utcnow()
                db.commit()
                self.logger.info(f"Updated family profile for user {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update family profile {user_id}: {e}")
            return False
    
    # Family Relationship Management
    def create_family_relationship(
        self,
        elderly_user_id: str,
        family_member_id: str,
        relationship_type: RelationshipType,
        permissions: Optional[Dict[str, bool]] = None
    ) -> bool:
        """Create relationship between elderly user and family member"""
        try:
            with get_db() as db:
                # Verify both users exist and have correct types
                elderly_user = db.query(User).filter(
                    and_(User.id == elderly_user_id, User.user_type == UserType.ELDERLY)
                ).first()
                
                family_user = db.query(User).filter(
                    and_(User.id == family_member_id, User.user_type == UserType.FAMILY_MEMBER)
                ).first()
                
                if not elderly_user or not family_user:
                    return False
                
                # Get profile IDs
                elderly_profile = db.query(ElderlyProfile).filter(
                    ElderlyProfile.user_id == elderly_user_id
                ).first()
                
                family_profile = db.query(FamilyProfile).filter(
                    FamilyProfile.user_id == family_member_id
                ).first()
                
                if not elderly_profile or not family_profile:
                    return False
                
                # Check if relationship already exists
                existing = db.query(FamilyRelationship).filter(
                    and_(
                        FamilyRelationship.elderly_id == elderly_profile.id,
                        FamilyRelationship.family_member_id == family_profile.id
                    )
                ).first()
                
                if existing:
                    return False
                
                # Set default permissions
                default_permissions = {
                    'can_view_health_data': True,
                    'can_receive_notifications': True,
                    'can_manage_medications': False,
                    'can_schedule_appointments': False
                }
                
                if permissions:
                    default_permissions.update(permissions)
                
                # Create relationship
                relationship = FamilyRelationship(
                    elderly_id=elderly_profile.id,
                    family_member_id=family_profile.id,
                    relationship_type=relationship_type,
                    **default_permissions
                )
                
                db.add(relationship)
                db.commit()
                self.logger.info(f"Created family relationship: {elderly_user_id} -> {family_member_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to create family relationship: {e}")
            return False
    
    def get_family_members(self, elderly_user_id: str) -> List[Dict]:
        """Get all family members connected to an elderly user"""
        try:
            with get_db() as db:
                relationships = db.query(FamilyRelationship).join(
                    ElderlyProfile, FamilyRelationship.elderly_id == ElderlyProfile.id
                ).join(
                    FamilyProfile, FamilyRelationship.family_member_id == FamilyProfile.id
                ).join(
                    User, FamilyProfile.user_id == User.id
                ).filter(
                    ElderlyProfile.user_id == elderly_user_id
                ).options(
                    joinedload(FamilyRelationship.family_member).joinedload(FamilyProfile.user)
                ).all()
                
                family_members = []
                for rel in relationships:
                    family_user = rel.family_member.user
                    family_members.append({
                        'user_id': str(family_user.id),
                        'full_name': family_user.full_name,
                        'email': family_user.email,
                        'phone': family_user.phone,
                        'relationship_type': rel.relationship_type.value,
                        'permissions': {
                            'can_view_health_data': rel.can_view_health_data,
                            'can_receive_notifications': rel.can_receive_notifications,
                            'can_manage_medications': rel.can_manage_medications,
                            'can_schedule_appointments': rel.can_schedule_appointments
                        },
                        'is_primary_caregiver': rel.family_member.is_primary_caregiver,
                        'occupation': rel.family_member.occupation
                    })
                
                return family_members
                
        except Exception as e:
            self.logger.error(f"Failed to get family members for {elderly_user_id}: {e}")
            return []
    
    def get_elderly_patients(self, family_member_id: str) -> List[Dict]:
        """Get all elderly users that a family member is connected to"""
        try:
            with get_db() as db:
                relationships = db.query(FamilyRelationship).join(
                    FamilyProfile, FamilyRelationship.family_member_id == FamilyProfile.id
                ).join(
                    ElderlyProfile, FamilyRelationship.elderly_id == ElderlyProfile.id
                ).join(
                    User, ElderlyProfile.user_id == User.id
                ).filter(
                    FamilyProfile.user_id == family_member_id
                ).options(
                    joinedload(FamilyRelationship.elderly_user).joinedload(ElderlyProfile.user)
                ).all()
                
                elderly_users = []
                for rel in relationships:
                    elderly_user = rel.elderly_user.user
                    elderly_users.append({
                        'user_id': str(elderly_user.id),
                        'full_name': elderly_user.full_name,
                        'email': elderly_user.email,
                        'phone': elderly_user.phone,
                        'relationship_type': rel.relationship_type.value,
                        'date_of_birth': elderly_user.date_of_birth.isoformat() if elderly_user.date_of_birth else None,
                        'permissions': {
                            'can_view_health_data': rel.can_view_health_data,
                            'can_receive_notifications': rel.can_receive_notifications,
                            'can_manage_medications': rel.can_manage_medications,
                            'can_schedule_appointments': rel.can_schedule_appointments
                        },
                        'medical_conditions': rel.elderly_user.medical_conditions,
                        'emergency_contact': rel.elderly_user.emergency_contact
                    })
                
                return elderly_users
                
        except Exception as e:
            self.logger.error(f"Failed to get elderly patients for {family_member_id}: {e}")
            return []
    
    def update_relationship_permissions(
        self,
        elderly_user_id: str,
        family_member_id: str,
        permissions: Dict[str, bool]
    ) -> bool:
        """Update permissions for a family relationship"""
        try:
            with get_db() as db:
                # Get profile IDs
                elderly_profile = db.query(ElderlyProfile).filter(
                    ElderlyProfile.user_id == elderly_user_id
                ).first()
                
                family_profile = db.query(FamilyProfile).filter(
                    FamilyProfile.user_id == family_member_id
                ).first()
                
                if not elderly_profile or not family_profile:
                    return False
                
                relationship = db.query(FamilyRelationship).filter(
                    and_(
                        FamilyRelationship.elderly_id == elderly_profile.id,
                        FamilyRelationship.family_member_id == family_profile.id
                    )
                ).first()
                
                if not relationship:
                    return False
                
                # Update permissions
                for key, value in permissions.items():
                    if hasattr(relationship, key):
                        setattr(relationship, key, value)
                
                db.commit()
                self.logger.info(f"Updated relationship permissions: {elderly_user_id} -> {family_member_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update relationship permissions: {e}")
            return False
    
    # User Search and Listing
    def search_users(
        self,
        query: str,
        user_type: Optional[UserType] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Search users by name, email, or phone"""
        try:
            with get_db() as db:
                db_query = db.query(User).filter(
                    or_(
                        User.full_name.ilike(f"%{query}%"),
                        User.email.ilike(f"%{query}%"),
                        User.phone.ilike(f"%{query}%")
                    ),
                    User.is_active == True
                )
                
                if user_type:
                    db_query = db_query.filter(User.user_type == user_type)
                
                users = db_query.limit(limit).all()
                
                return [
                    {
                        'user_id': str(user.id),
                        'full_name': user.full_name,
                        'email': user.email,
                        'phone': user.phone,
                        'user_type': user.user_type.value,
                        'created_at': user.created_at.isoformat()
                    }
                    for user in users
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to search users: {e}")
            return [] 