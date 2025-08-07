"""
Authentication API Service
Handles user registration, login, and profile management
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
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

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

def add_auth_endpoints(app: FastAPI):
    """Add authentication endpoints to the FastAPI app"""
    
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
            
            # Convert enum to database enum
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
                "user_type": user.user_type.value,
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
            user = None
            if "@" in request.identifier:
                user = user_service.get_user_by_contact(email=request.identifier)
            else:
                user = user_service.get_user_by_contact(phone=request.identifier)
            
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            # Check password
            hashed_password = hash_password(request.password)
            stored_hash = getattr(user, 'password_hash', None)
            
            if not stored_hash or stored_hash != hashed_password:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            if not user.is_active:
                raise HTTPException(status_code=401, detail="Account is deactivated")
            
            # Update last login
            user_service.update_user(str(user.id), last_login=datetime.utcnow())
            
            # Generate session token
            session_token = generate_session_token()
            
            # Create response
            user_response = UserResponse(
                user_id=str(user.id),
                user_type=user.user_type.value,
                full_name=user.full_name,
                email=user.email,
                phone=user.phone,
                date_of_birth=user.date_of_birth.isoformat() if user.date_of_birth else None,
                gender=user.gender,
                address=user.address,
                created_at=user.created_at.isoformat(),
                is_active=user.is_active
            )
            
            logger.info(f"User logged in successfully: {user.id}")
            
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
                user_type=user.user_type.value,
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
            
            if not elderly_user or elderly_user.user_type != UserType.ELDERLY:
                raise HTTPException(status_code=404, detail="Elderly user not found")
            
            # Convert enum
            relationship_type = getattr(RelationshipType, request.relationship_type.value.upper())
            
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
    
    @app.get("/api/auth/family-members/{elderly_user_id}")
    async def get_family_members(elderly_user_id: str):
        """Get family members for an elderly user"""
        if not DATABASE_AVAILABLE:
            raise HTTPException(status_code=503, detail="Database not available")
        
        try:
            user_service = UserService()
            family_members = user_service.get_family_members(elderly_user_id)
            return {"family_members": family_members}
            
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
            return {"elderly_patients": elderly_patients}
            
        except Exception as e:
            logger.error(f"Get elderly patients error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error") 