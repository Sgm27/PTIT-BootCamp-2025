"""
Authentication API Service
Handles user registration, login, and profile management
"""
from fastapi import FastAPI, HTTPException, Header, Query, Depends
from types import SimpleNamespace
from typing import Optional
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, timezone
import hashlib
import secrets
import logging
from enum import Enum

# Database imports
try:
    from db.db_services import UserService
    from db.models import UserType, RelationshipType
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class UserTypeEnum(str, Enum):
    ELDERLY = "elderly"
    FAMILY = "family"

class RelationshipTypeEnum(str, Enum):
    CHILD = "child"
    GRANDCHILD = "grandchild"
    SPOUSE = "spouse"
    SIBLING = "sibling"
    RELATIVE = "relative"
    CAREGIVER = "caregiver"

class RegisterRequest(BaseModel):
    user_type: UserTypeEnum
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    password: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None

class LoginRequest(BaseModel):
    identifier: str  # email or phone
    password: str

class UserResponse(BaseModel):
    user_id: str
    user_type: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    date_of_birth: Optional[str]
    gender: Optional[str]
    address: Optional[str]
    created_at: str
    is_active: bool

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None
    session_token: Optional[str] = None

class CreateRelationshipRequest(BaseModel):
    elderly_user_identifier: str  # email or phone of elderly user
    relationship_type: RelationshipTypeEnum
    permissions: Optional[dict] = None

class ProfileUpdateRequest(BaseModel):
    full_name: str
    email: str
    phone: str
    address: str
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

async def get_current_user(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    user_id: Optional[str] = Query(default=None)
):
    """Resolve current user from Authorization header or explicit user_id query param.
    This is intentionally permissive to support the Android demo client.
    """
    try:
        if user_id:
            return SimpleNamespace(id=user_id)
        if authorization:
            token = authorization.replace("Bearer ", "").strip()
            if token:
                return SimpleNamespace(id="00000000-0000-0000-0000-000000000000")
        raise HTTPException(status_code=401, detail="Unauthorized")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unauthorized: {str(e)}")


def add_auth_endpoints(app: FastAPI):
    """Add authentication endpoints to the FastAPI app"""

    # Ensure dependency is available to other routers if they import from app.dependency_overrides
    app.dependency_overrides[get_current_user] = get_current_user
    
    @app.post("/api/auth/register", response_model=LoginResponse)
    async def register_user(request: RegisterRequest):
        """Register a new user"""
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            # Check database connection first
            from db.db_config import check_database_connection
            if not check_database_connection():
                raise HTTPException(status_code=503, detail="Database connection failed")
                
            user_service = UserService()
            
            # Hash password
            hashed_password = hash_password(request.password)
            
            # Convert enum to database enum value
            user_type = UserType.ELDERLY if request.user_type == UserTypeEnum.ELDERLY else UserType.FAMILY_MEMBER
            
            # Create user
            user = user_service.create_user(
                user_type=user_type,
                full_name=request.full_name,
                email=request.email,
                phone=request.phone,
                date_of_birth=request.date_of_birth,
                gender=request.gender,
                address=request.address,
                password_hash=hashed_password
            )
            
            if not user:
                raise HTTPException(status_code=400, detail="Failed to create user. Email or phone may already exist.")
            
            # Generate session token
            session_token = generate_session_token()
            
            # Create response
            user_data = {
                "user_id": str(user.id),
                "user_type": user.user_type.lower() if isinstance(user.user_type, str) else user.user_type.value.lower(),  # Convert to lowercase for Android compatibility
                "full_name": user.full_name,
                "email": user.email,
                "phone": user.phone,
                "date_of_birth": user.date_of_birth.isoformat() if user.date_of_birth else None,
                "gender": user.gender,
                "address": user.address,
                "created_at": user.created_at.isoformat(),
                "is_active": user.is_active
            }
            
            user_response = UserResponse(**user_data)
            
            logger.info(f"User registered successfully: {user_data['user_id']}")
            
            return LoginResponse(
                success=True,
                message="User registered successfully",
                user=user_response,
                session_token=session_token
            )
            
        except ValueError as e:
            logger.error(f"Registration validation error: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Registration error: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    @app.post("/api/auth/login", response_model=LoginResponse)
    async def login_user(request: LoginRequest):
        """Login user with email/phone and password"""
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            # Check database connection first
            from db.db_config import check_database_connection
            if not check_database_connection():
                raise HTTPException(status_code=503, detail="Database connection failed")
                
            user_service = UserService()
            
            # Try to find user by email or phone
            user_data = None
            if "@" in request.identifier:
                user_data = user_service.get_user_by_contact(email=request.identifier)
            else:
                user_data = user_service.get_user_by_contact(phone=request.identifier)
            
            if not user_data:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Check password
            hashed_password = hash_password(request.password)
            stored_hash = user_data.get('password_hash')
            
            if not stored_hash or stored_hash != hashed_password:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            if not user_data.get('is_active', True):
                raise HTTPException(status_code=401, detail="Account is deactivated")
            
            # Update last login
            user_service.update_user(str(user_data['id']), last_login=datetime.now(timezone.utc))
            
            # Prepare user data for response
            try:
                user_type = user_data['user_type'].lower() if isinstance(user_data['user_type'], str) else user_data['user_type'].value.lower()
                created_at = user_data['created_at'].isoformat() if user_data['created_at'] else None
                date_of_birth = user_data['date_of_birth'].isoformat() if user_data['date_of_birth'] else None
            except Exception as e:
                logger.error(f"Error processing user data: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
            
            # Generate session token
            session_token = generate_session_token()
            
            # Create response
            user_response = UserResponse(
                user_id=str(user_data['id']),
                user_type=user_type,  # Use pre-loaded value
                full_name=user_data['full_name'],
                email=user_data['email'],
                phone=user_data['phone'],
                date_of_birth=date_of_birth,  # Use pre-loaded value
                gender=user_data['gender'],
                address=user_data['address'],
                created_at=created_at,  # Use pre-loaded value
                is_active=user_data['is_active']
            )
            
            logger.info(f"User logged in successfully: {user_data['id']}")
            
            return LoginResponse(
                success=True,
                message="Login successful",
                user=user_response,
                session_token=session_token
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.get("/api/auth/profile/{user_id}", response_model=UserResponse)
    async def get_user_profile(user_id: str):
        """Get user profile by ID"""
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            user_service = UserService()
            user = user_service.get_user_by_id(user_id)
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return UserResponse(
                user_id=str(user.id),
                user_type=user.user_type.lower() if isinstance(user.user_type, str) else user.user_type.value.lower(),  # Convert to lowercase for Android compatibility
                full_name=user.full_name,
                email=user.email,
                phone=user.phone,
                date_of_birth=user.date_of_birth.isoformat() if user.date_of_birth else None,
                gender=user.gender,
                address=user.address,
                created_at=user.created_at.isoformat(),
                is_active=user.is_active
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Get profile error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.post("/api/auth/create-relationship")
    async def create_family_relationship(request: CreateRelationshipRequest, family_user_id: str):
        """Create relationship between family member and elderly user"""
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            user_service = UserService()
            
            # Find elderly user by identifier
            elderly_user = None
            if "@" in request.elderly_user_identifier:
                elderly_user = user_service.get_user_by_contact(email=request.elderly_user_identifier)
            else:
                elderly_user = user_service.get_user_by_contact(phone=request.elderly_user_identifier)
            
            if not elderly_user or elderly_user.user_type != UserType.ELDERLY.value:
                raise HTTPException(status_code=404, detail="Elderly user not found")
            
            # Convert enum - the API enum value should match the database enum value
            # RelationshipTypeEnum has values like "child", "grandchild", etc.
            # The database expects string values, so we can use the value directly
            relationship_type = request.relationship_type.value
            
            # Create relationship
            success = user_service.create_family_relationship(
                elderly_user_id=str(elderly_user.id),
                family_member_id=family_user_id,
                relationship_type=relationship_type,
                permissions=request.permissions
            )
            
            if not success:
                raise HTTPException(status_code=400, detail="Failed to create relationship")
            
            return {"success": True, "message": "Relationship created successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Create relationship error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.get("/api/family/elderly-list")
    async def get_elderly_list():
        """Get list of elderly users for family members"""
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            user_service = UserService()
            # For now, return all elderly users (in production, filter by family relationship)
            elderly_users = user_service.get_users_by_type(UserType.ELDERLY.value)
            
            elderly_list = []
            for user in elderly_users:
                elderly_list.append({
                    "elderly_id": str(user.id),
                    "full_name": user.full_name,
                    "email": user.email,
                    "relationship_type": "family"  # Default relationship
                })
            
            return {
                "success": True,
                "elderly_list": elderly_list
            }
            
        except Exception as e:
            logger.error(f"Get elderly list error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.post("/api/family/send-notification")
    async def send_family_notification(notification_data: dict):
        """Send notification to elderly user from family member"""
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            # Extract notification data
            elderly_user_id = notification_data.get("elderly_user_id")
            notification_info = notification_data.get("notification_data", {})
            
            if not elderly_user_id:
                raise HTTPException(status_code=400, detail="Elderly user ID is required")
            
            # For now, just return success (in production, implement actual notification logic)
            logger.info(f"Family notification sent to elderly user {elderly_user_id}: {notification_info}")
            
            return {
                "success": True,
                "message": "Notification sent successfully",
                "notification_id": f"temp_{elderly_user_id}_{datetime.now(timezone.utc).timestamp()}"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Send family notification error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.get("/api/auth/family-members/{elderly_user_id}")
    async def get_family_members(elderly_user_id: str):
        """Get family members for an elderly user"""
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            user_service = UserService()
            family_members = user_service.get_family_members(elderly_user_id)
            return {
                "success": True,
                "family_members": family_members
            }
            
        except Exception as e:
            logger.error(f"Get family members error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.get("/api/auth/elderly-patients/{family_user_id}")
    async def get_elderly_patients(family_user_id: str):
        """Get elderly patients for a family member"""
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            user_service = UserService()
            elderly_patients = user_service.get_elderly_patients(family_user_id)
            return {
                "success": True,
                "elderly_patients": elderly_patients
            }
            
        except Exception as e:
            logger.error(f"Get elderly patients error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.put("/api/auth/profile/{user_id}")
    async def update_user_profile(user_id: str, request: ProfileUpdateRequest):
        """Update user profile information"""
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            user_service = UserService()
            
            # Check if user exists
            user = user_service.get_user_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Update user profile
            updated_user = user_service.update_user_profile(
                user_id=user_id,
                full_name=request.full_name,
                email=request.email,
                phone=request.phone,
                address=request.address,
                date_of_birth=request.date_of_birth,
                gender=request.gender
            )
            
            if not updated_user:
                raise HTTPException(status_code=400, detail="Failed to update profile")
            
            return {
                "success": True,
                "message": "Profile updated successfully",
                "user": {
                    "user_id": str(updated_user.id),
                    "user_type": updated_user.user_type.lower() if isinstance(updated_user.user_type, str) else updated_user.user_type.value.lower(),
                    "full_name": updated_user.full_name,
                    "email": updated_user.email,
                    "phone": updated_user.phone,
                    "date_of_birth": updated_user.date_of_birth.isoformat() if updated_user.date_of_birth else None,
                    "gender": updated_user.gender,
                    "address": updated_user.address,
                    "created_at": updated_user.created_at.isoformat(),
                    "is_active": updated_user.is_active
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Update profile error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.get("/api/family/reminders")
    async def get_user_reminders():
        """Get reminders for the current user"""
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            # For now, return empty reminders list
            # In production, this would fetch actual reminders from the database
            return {
                "success": True,
                "reminders": []
            }
            
        except Exception as e:
            logger.error(f"Get user reminders error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.get("/api/family/members")
    async def get_family_members_list():
        """Get family members list"""
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            # For now, return empty family members list
            # In production, this would fetch actual family members from the database
            return {
                "success": True,
                "family_members": []
            }
            
        except Exception as e:
            logger.error(f"Get family members list error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    # Schedule endpoints moved to schedule_service.py 