"""
Memoir API endpoints for Android app integration
Provides access to life memoirs extracted from conversations
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from datetime import date
import logging

from db.db_services.memoir_service import MemoirDBService
from db.db_services.user_service import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/memoirs", tags=["memoirs"])

# Initialize services
memoir_service = MemoirDBService()
user_service = UserService()

@router.get("/{user_id}")
async def get_user_memoirs(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: str = Query("extracted_at", regex="^(extracted_at|date_of_memory|importance)$")
) -> Dict[str, Any]:
    """Get all memoirs for a user"""
    try:
        # Verify user exists
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get memoirs from database
        memoirs = await memoir_service.get_user_memoirs(
            user_id=user_id,
            limit=limit,
            offset=offset,
            order_by=order_by
        )
        
        logger.info(f"Retrieved {len(memoirs)} memoirs for user {user_id}")
        
        return {
            "success": True,
            "memoirs": memoirs,
            "total_count": len(memoirs),
            "limit": limit,
            "offset": offset,
            "order_by": order_by
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting memoirs for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{user_id}/{memoir_id}")
async def get_memoir_detail(
    user_id: str,
    memoir_id: str
) -> Dict[str, Any]:
    """Get detailed information about a specific memoir"""
    try:
        # Verify user exists
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get memoir detail
        memoir = await memoir_service.get_memoir(memoir_id)
        if not memoir:
            raise HTTPException(status_code=404, detail="Memoir not found")
        
        # Verify memoir belongs to user
        if str(memoir['user_id']) != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Memoir is already a dictionary
        memoir_dict = memoir
        
        logger.info(f"Retrieved memoir {memoir_id} for user {user_id}")
        
        return {
            "success": True,
            "memoir": memoir_dict
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting memoir {memoir_id} for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{user_id}/search")
async def search_memoirs(
    user_id: str,
    search_request: Dict[str, Any]
) -> Dict[str, Any]:
    """Search memoirs by content, categories, or other attributes"""
    try:
        # Verify user exists
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Extract search parameters
        query = search_request.get("query", "")
        categories = search_request.get("categories", [])
        time_period = search_request.get("time_period")
        emotional_tone = search_request.get("emotional_tone")
        limit = search_request.get("limit", 20)
        
        if not query and not categories and not time_period and not emotional_tone:
            raise HTTPException(status_code=400, detail="At least one search parameter is required")
        
        # Search memoirs
        memoirs = await memoir_service.search_memoirs(
            user_id=user_id,
            query=query,
            categories=categories,
            time_period=time_period,
            emotional_tone=emotional_tone,
            limit=limit
        )
        
        logger.info(f"Search returned {len(memoirs)} memoirs for user {user_id}")
        
        return {
            "success": True,
            "memoirs": memoirs,
            "search_params": search_request,
            "total_count": len(memoirs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching memoirs for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{user_id}/timeline")
async def get_memoir_timeline(
    user_id: str
) -> Dict[str, Any]:
    """Get memoirs organized by timeline/chronological order"""
    try:
        # Verify user exists
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get memoir timeline
        timeline = await memoir_service.get_memoir_timeline(user_id)
        
        logger.info(f"Retrieved timeline for user {user_id} with {len(timeline)} entries")
        
        return {
            "success": True,
            "timeline": timeline
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting timeline for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{user_id}/categories")
async def get_memoir_categories(
    user_id: str
) -> Dict[str, Any]:
    """Get all categories used in user's memoirs"""
    try:
        # Verify user exists
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get categories
        categories = await memoir_service.get_memoir_categories(user_id)
        
        logger.info(f"Retrieved {len(categories)} categories for user {user_id}")
        
        return {
            "success": True,
            "categories": categories
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting categories for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{user_id}/people")
async def get_memoir_people(
    user_id: str
) -> Dict[str, Any]:
    """Get all people mentioned in user's memoirs"""
    try:
        # Verify user exists
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get people
        people = await memoir_service.get_memoir_people(user_id)
        
        logger.info(f"Retrieved {len(people)} people for user {user_id}")
        
        return {
            "success": True,
            "people": people
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting people for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{user_id}/places")
async def get_memoir_places(
    user_id: str
) -> Dict[str, Any]:
    """Get all places mentioned in user's memoirs"""
    try:
        # Verify user exists
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get places
        places = await memoir_service.get_memoir_places(user_id)
        
        logger.info(f"Retrieved {len(places)} places for user {user_id}")
        
        return {
            "success": True,
            "places": places
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting places for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{user_id}/stats")
async def get_memoir_stats(
    user_id: str
) -> Dict[str, Any]:
    """Get statistics about user's memoirs"""
    try:
        # Verify user exists
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get memoir stats
        stats = await memoir_service.get_memoir_stats(user_id)
        
        logger.info(f"Retrieved stats for user {user_id}")
        
        return {
            "success": True,
            "memoir_stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{user_id}/export")
async def export_memoirs(
    user_id: str,
    export_request: Dict[str, Any]
) -> Dict[str, Any]:
    """Export memoirs in various formats for family sharing"""
    try:
        # Verify user exists
        user = user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Extract export parameters
        format_type = export_request.get("format_type", "text")
        
        # Export memoirs
        export_data = await memoir_service.export_memoirs_for_family(
            user_id=user_id,
            format_type=format_type
        )
        
        if not export_data:
            raise HTTPException(status_code=404, detail="No memoirs found to export")
        
        logger.info(f"Exported memoirs for user {user_id} in {format_type} format")
        
        return {
            "success": True,
            "export_data": export_data,
            "format_type": format_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting memoirs for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 