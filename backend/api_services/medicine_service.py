"""
Medicine API Service
Handles medicine scanning, text extraction, and health-related endpoints
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from models.api_models import MedicineScanRequest, TextExtractRequest, HealthResponse
import logging

logger = logging.getLogger(__name__)

def add_medicine_endpoints(app: FastAPI, medicine_service, text_extraction_service):
    """Add medicine and health-related endpoints to the FastAPI app
    
    Args:
        app: FastAPI application instance
        medicine_service: Service instance for medicine scanning
        text_extraction_service: Service instance for text extraction
    """
    
    @app.post("/api/scan-medicine", response_model=HealthResponse)
    async def scan_medicine_endpoint(request: MedicineScanRequest):
        """Scan medicine from image URL or base64 string.
        
        Args:
            request: Request containing image URL or base64 string.
            
        Returns:
            HealthResponse with scan results.
            
        Raises:
            HTTPException: If scanning fails.
        """
        try:
            result = await medicine_service.scan_medicine(request.input)
            return HealthResponse(**result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/scan-medicine-file")
    async def scan_medicine_file_endpoint(file: UploadFile = File(...)):
        """Scan medicine from uploaded image file.
        
        Args:
            file: Uploaded image file.
            
        Returns:
            HealthResponse with scan results.
            
        Raises:
            HTTPException: If scanning fails.
        """
        try:
            # Read file content
            content = await file.read()
            
            # Scan medicine using service
            result = await medicine_service.scan_from_file_content(content)
            return HealthResponse(**result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/extract-memoir-info", response_model=HealthResponse)
    async def extract_memoir_info_endpoint(request: TextExtractRequest):
        """Extract information from text for memoir purposes.
        
        Args:
            request: Request containing text to extract information from.
            
        Returns:
            HealthResponse with extracted information.
            
        Raises:
            HTTPException: If extraction fails.
        """
        try:
            result = await text_extraction_service.extract_info_for_memoir(request.text)
            return HealthResponse(success=True, result=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) 