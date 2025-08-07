"""
Memoir API Service
Handles memoir extraction, conversation history, and background processing
"""
from fastapi import FastAPI, HTTPException
import datetime
import logging

logger = logging.getLogger(__name__)

def add_memoir_endpoints(app: FastAPI, memoir_extraction_service):
    """Add memoir-related endpoints to the FastAPI app
    
    Args:
        app: FastAPI application instance
        memoir_extraction_service: Service instance for memoir processing
    """
    
    @app.post("/api/memoir/extract-background")
    async def start_memoir_extraction_background():
        """Start background memoir extraction from conversation history.
        
        Returns:
            Status of background task initiation.
        """
        try:
            result = memoir_extraction_service.start_background_extraction()
            return {
                "success": True,
                "message": "Background memoir extraction initiated",
                "task_status": result,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to start background extraction: {str(e)}")

    @app.get("/api/memoir/status")
    async def get_memoir_extraction_status():
        """Get status of memoir extraction background task.
        
        Returns:
            Current status of background extraction task.
        """
        try:
            status = await memoir_extraction_service.get_background_task_status()
            return {
                "success": True,
                "task_status": status,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get extraction status: {str(e)}")

    @app.get("/api/memoir/file-info")
    async def get_memoir_file_info():
        """Get information about the memoir file.
        
        Returns:
            Information about memoir file including size, last modified, etc.
        """
        try:
            file_info = await memoir_extraction_service.get_memoir_file_info()
            return {
                "success": True,
                "file_info": file_info,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}")

    @app.post("/api/memoir/extract-manual")
    async def extract_memoir_manual():
        """Manually extract important information from current conversation history.
        
        Returns:
            Results of memoir extraction process.
        """
        try:
            result = await memoir_extraction_service.process_conversation_history_background()
            return {
                "success": True,
                "extraction_result": result,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to extract memoir information: {str(e)}")

    @app.get("/api/memoir/auto-settings")
    async def get_memoir_auto_settings():
        """Get current auto extraction settings.
        
        Returns:
            Current auto extraction configuration.
        """
        try:
            settings_info = memoir_extraction_service.get_auto_extraction_settings()
            return {
                "success": True,
                "auto_settings": settings_info,
                "timestamp": datetime.datetime.now().isoformat()
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get auto settings: {str(e)}")

    @app.post("/api/memoir/auto-settings")
    async def update_memoir_auto_settings(request: dict):
        """Update auto extraction settings.
        
        Args:
            request: Request containing new threshold value.
            
        Returns:
            Status of settings update.
        """
        try:
            threshold = request.get("threshold")
            if not threshold or not isinstance(threshold, int):
                raise HTTPException(status_code=400, detail="Valid threshold number is required")
            
            result = memoir_extraction_service.update_auto_extraction_threshold(threshold)
            return {
                "success": result["success"],
                "message": result.get("message", result.get("error")),
                "settings": memoir_extraction_service.get_auto_extraction_settings(),
                "timestamp": datetime.datetime.now().isoformat()
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update auto settings: {str(e)}")

    @app.post("/api/memoir/update-conversation")
    async def update_conversation_with_memoir(request: dict):
        """Update conversation history and potentially trigger auto extraction.
        
        Args:
            request: Request containing new message data.
            
        Returns:
            Status of conversation update and extraction.
        """
        try:
            # Validate required fields
            required_fields = ["role", "text"]
            for field in required_fields:
                if field not in request:
                    raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
            
            # Create message with timestamp
            new_message = {
                "role": request["role"],
                "text": request["text"], 
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            result = await memoir_extraction_service.update_conversation_and_extract(new_message)
            return {
                "success": result["success"],
                "message": result.get("message"),
                "conversation_info": {
                    "total_messages": result.get("total_messages"),
                    "auto_extract_triggered": result.get("auto_extract_triggered", False)
                },
                "timestamp": datetime.datetime.now().isoformat()
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update conversation: {str(e)}") 