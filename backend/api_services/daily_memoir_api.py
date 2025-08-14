"""
API endpoints for Daily Memoir Extraction management
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel

from services.daily_memoir_scheduler import daily_memoir_scheduler

# Create router
router = APIRouter(prefix="/api/memoir", tags=["Daily Memoir"])

class MemoirExtractionRequest(BaseModel):
    user_id: Optional[str] = None
    target_date: Optional[str] = None  # YYYY-MM-DD format

class MemoirExtractionResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

@router.get("/scheduler/status", response_model=dict)
async def get_scheduler_status():
    """Get current status of the daily memoir scheduler"""
    try:
        status = daily_memoir_scheduler.get_scheduler_status()
        return {
            "success": True,
            "data": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting scheduler status: {str(e)}")

@router.post("/extract/manual", response_model=MemoirExtractionResponse)
async def manual_memoir_extraction(request: MemoirExtractionRequest):
    """Manually trigger memoir extraction for a specific date or user"""
    try:
        # Parse target date if provided
        target_date = None
        if request.target_date:
            try:
                target_date = datetime.strptime(request.target_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Trigger manual extraction
        result = await daily_memoir_scheduler.manual_memoir_extraction(
            target_date=target_date,
            user_id=request.user_id
        )
        
        return MemoirExtractionResponse(
            success=result.get("success", False),
            message=result.get("message", "Unknown result"),
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in manual extraction: {str(e)}")

@router.post("/extract/test", response_model=MemoirExtractionResponse)
async def test_memoir_extraction(
    user_id: Optional[str] = Query(None, description="Specific user ID to test"),
    days_back: int = Query(1, description="Number of days back to test", ge=1, le=30)
):
    """Test memoir extraction for debugging purposes"""
    try:
        result = await daily_memoir_scheduler.test_memoir_extraction(
            user_id=user_id,
            days_back=days_back
        )
        
        return MemoirExtractionResponse(
            success=result.get("success", False),
            message=result.get("message", "Test completed"),
            data=result
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in test extraction: {str(e)}")

@router.get("/extract/history", response_model=dict)
async def get_extraction_history(
    days_back: int = Query(7, description="Number of days to look back", ge=1, le=30)
):
    """Get history of memoir extractions for the past N days"""
    try:
        from db.db_config import get_db
        from db.models import LifeMemoir
        from sqlalchemy import and_, func
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        with get_db() as db:
            # Get memoir counts by date
            results = db.query(
                LifeMemoir.date_of_memory,
                func.count(LifeMemoir.id).label('memoir_count'),
                func.count(func.distinct(LifeMemoir.user_id)).label('user_count')
            ).filter(
                and_(
                    LifeMemoir.date_of_memory >= start_date,
                    LifeMemoir.date_of_memory <= end_date
                )
            ).group_by(LifeMemoir.date_of_memory).order_by(LifeMemoir.date_of_memory.desc()).all()
            
            history = []
            for result in results:
                history.append({
                    "date": result.date_of_memory.isoformat(),
                    "memoir_count": result.memoir_count,
                    "user_count": result.user_count
                })
            
            return {
                "success": True,
                "data": {
                    "date_range": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat()
                    },
                    "history": history,
                    "total_memoirs": sum(h["memoir_count"] for h in history),
                    "total_users": len(set(h["user_count"] for h in history))
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting extraction history: {str(e)}")

@router.get("/users/{user_id}/memoirs", response_model=dict)
async def get_user_memoirs(
    user_id: str,
    limit: int = Query(20, description="Number of memoirs to return", ge=1, le=100),
    offset: int = Query(0, description="Number of memoirs to skip", ge=0)
):
    """Get memoirs for a specific user"""
    try:
        from db.db_services.memoir_service import MemoirDBService
        
        memoir_service = MemoirDBService()
        memoirs = await memoir_service.get_user_memoirs(
            user_id=user_id,
            limit=limit,
            offset=offset,
            order_by="date_of_memory"
        )
        
        memoir_data = []
        for memoir in memoirs:
            memoir_data.append({
                "id": str(memoir.id),
                "title": memoir.title,
                "content": memoir.content[:200] + "..." if len(memoir.content) > 200 else memoir.content,
                "date_of_memory": memoir.date_of_memory.isoformat() if memoir.date_of_memory else None,
                "extracted_at": memoir.extracted_at.isoformat(),
                "categories": memoir.categories,
                "importance_score": memoir.importance_score
            })
        
        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "memoirs": memoir_data,
                "count": len(memoir_data),
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user memoirs: {str(e)}")

@router.get("/stats", response_model=dict)
async def get_memoir_stats():
    """Get overall memoir extraction statistics"""
    try:
        from db.db_config import get_db
        from db.models import LifeMemoir, User
        from sqlalchemy import func, and_
        
        with get_db() as db:
            # Total memoirs
            total_memoirs = db.query(func.count(LifeMemoir.id)).scalar()
            
            # Total users with memoirs
            users_with_memoirs = db.query(func.count(func.distinct(LifeMemoir.user_id))).scalar()
            
            # Memoirs in last 7 days
            week_ago = date.today() - timedelta(days=7)
            recent_memoirs = db.query(func.count(LifeMemoir.id)).filter(
                LifeMemoir.extracted_at >= week_ago
            ).scalar()
            
            # Average importance score
            avg_importance = db.query(func.avg(LifeMemoir.importance_score)).scalar() or 0.0
            
            # Most common categories
            category_results = db.query(
                func.unnest(LifeMemoir.categories).label('category'),
                func.count('*').label('count')
            ).group_by('category').order_by(func.count('*').desc()).limit(10).all()
            
            categories = [{"category": r.category, "count": r.count} for r in category_results]
            
            return {
                "success": True,
                "data": {
                    "total_memoirs": total_memoirs,
                    "users_with_memoirs": users_with_memoirs,
                    "recent_memoirs_7_days": recent_memoirs,
                    "average_importance_score": float(avg_importance),
                    "top_categories": categories,
                    "last_updated": datetime.now().isoformat()
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting memoir stats: {str(e)}")

# Function to add routes to main app
def add_daily_memoir_endpoints(app):
    """Add daily memoir API endpoints to the FastAPI app"""
    app.include_router(router) 