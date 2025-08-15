#!/usr/bin/env python3
"""
Test script for medicine analysis using OpenAI Vision Model
"""
import asyncio
import base64
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import medicine service
from services.medicine_service import MedicineService
from config.settings import settings

async def test_medicine_analysis():
    """Test medicine analysis with OpenAI Vision Model."""
    
    logger.info("🧪 Testing Medicine Analysis with OpenAI Vision Model")
    logger.info(f"Model: {settings.OPENAI_VISION_MODEL}")
    logger.info(f"API Key configured: {'Yes' if settings.OPENAI_API_KEY else 'No'}")
    
    # Initialize medicine service
    medicine_service = MedicineService()
    
    # Test with a sample image (if available)
    test_image_path = Path("thuoc-panadol.jpg")
    
    if test_image_path.exists():
        logger.info(f"📸 Found test image: {test_image_path}")
        
        try:
            # Encode image to base64
            with open(test_image_path, "rb") as f:
                image_data = f.read()
                base64_image = base64.b64encode(image_data).decode("utf-8")
            
            logger.info(f"📊 Image encoded: {len(base64_image)} characters")
            
            # Analyze medicine
            logger.info("🔍 Analyzing medicine...")
            result = await medicine_service.scan_medicine(base64_image)
            
            if result.get("success"):
                logger.info("✅ Medicine analysis successful!")
                logger.info("📋 Analysis result:")
                print("-" * 50)
                print(result.get("result", ""))
                print("-" * 50)
            else:
                logger.error(f"❌ Medicine analysis failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"❌ Error during analysis: {e}")
    else:
        logger.warning("⚠️ No test image found. Testing with base64 string...")
        
        # Test with a dummy base64 string
        try:
            result = await medicine_service.scan_medicine("dummy_base64_string")
            logger.info(f"Test result: {result}")
        except Exception as e:
            logger.error(f"Error with dummy test: {e}")

async def test_api_endpoint():
    """Test the API endpoint directly."""
    
    logger.info("🌐 Testing API endpoint...")
    
    try:
        import httpx
        
        # Test with a dummy request
        test_data = {
            "input": "dummy_base64_string"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/analyze-medicine-gemini",
                json=test_data,
                timeout=30.0
            )
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response body: {response.text}")
            
    except Exception as e:
        logger.error(f"Error testing API endpoint: {e}")

if __name__ == "__main__":
    logger.info("🚀 Starting Medicine Analysis Tests")
    
    # Run tests
    asyncio.run(test_medicine_analysis())
    
    # Uncomment to test API endpoint (requires server running)
    # asyncio.run(test_api_endpoint())
    
    logger.info("🏁 Tests completed") 