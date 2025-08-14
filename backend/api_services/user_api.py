"""
User API endpoints for Android app integration
Provides user profile, authentication, and statistics
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import date
import logging

from db.db_services.user_service import UserService
from db.db_services.conversation_service import ConversationService
from db.db_services.memoir_service import MemoirDBService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Initialize services
user_service = UserService()
conversation_service = ConversationService()
memoir_service = MemoirDBService()

@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get user profile information"""
    try:
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Convert user object to dictionary
        user_dict = {
            'id': str(user.id),
            'user_type': user.user_type,
            'full_name': user.full_name,
            'email': user.email,
            'phone': user.phone,
            'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
            'gender': user.gender,
            'address': user.address,
            'city': user.city,
            'country': user.country,
            'preferred_language': user.preferred_language,
            'timezone': user.timezone,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
        
        logger.info(f"Retrieved profile for user {user_id}")
        
        return {
            "success": True,
            "user": user_dict
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/stats/{user_id}")
async def get_user_stats(user_id: str) -> Dict[str, Any]:
    """Get comprehensive user statistics including conversations and memoirs"""
    try:
        # Verify user exists
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get conversation stats
        conversation_stats = await conversation_service.get_conversation_stats(user_id)
        
        # Get memoir stats
        memoir_stats = await memoir_service.get_memoir_stats(user_id)
        
        # Combine all stats
        combined_stats = {
            "conversation_stats": conversation_stats,
            "memoir_stats": memoir_stats,
            "user_info": {
                "user_id": user_id,
                "full_name": user.full_name,
                "user_type": user.user_type
            }
        }
        
        logger.info(f"Retrieved stats for user {user_id}")
        
        return {
            "success": True,
            "stats": combined_stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/family-members/{elderly_user_id}")
async def get_family_members(elderly_user_id: str) -> Dict[str, Any]:
    """Get family members for an elderly user"""
    try:
        family_members = user_service.get_family_members(elderly_user_id)
        
        logger.info(f"Retrieved {len(family_members)} family members for elderly user {elderly_user_id}")
        
        return {
            "success": True,
            "family_members": family_members
        }
        
    except Exception as e:
        logger.error(f"Error getting family members for elderly user {elderly_user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/elderly-patients/{family_user_id}")
async def get_elderly_patients(family_user_id: str) -> Dict[str, Any]:
    """Get elderly patients for a family member"""
    try:
        elderly_patients = user_service.get_elderly_patients(family_user_id)
        
        logger.info(f"Retrieved {len(elderly_patients)} elderly patients for family member {family_user_id}")
        
        return {
            "success": True,
            "elderly_patients": elderly_patients
        }
        
    except Exception as e:
        logger.error(f"Error getting elderly patients for family member {family_user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 