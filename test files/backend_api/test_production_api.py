#!/usr/bin/env python3
"""
Test script for production API endpoint
"""
import asyncio
import base64
import json
import logging
import httpx
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_production_api():
    """Test the production API endpoint with real image."""
    
    logger.info("🧪 Testing Production API Endpoint")
    
    # Production API URL
    api_url = "https://backend.vcaremind.io.vn/api/analyze-medicine-gemini"
    
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
            
            # Prepare request data
            request_data = {
                "input": base64_image
            }
            
            # Test API
            logger.info(f"📡 Calling production API: {api_url}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    api_url,
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )
                
                logger.info(f"📊 Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        logger.info("✅ Production API call successful!")
                        logger.info(f"📄 Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                        
                        if response_data.get("success"):
                            result = response_data.get("result", "")
                            logger.info(f"📋 Analysis result length: {len(result)}")
                            logger.info("📋 Analysis result:")
                            print("-" * 50)
                            print(result)
                            print("-" * 50)
                        else:
                            logger.error(f"❌ API returned success=false: {response_data.get('result', 'Unknown error')}")
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ Failed to parse JSON response: {e}")
                        logger.info(f"📄 Raw response: {response.text}")
                else:
                    logger.error(f"❌ API call failed with status {response.status_code}")
                    logger.info(f"📄 Error response: {response.text}")
                    
        except Exception as e:
            logger.error(f"❌ Error during API test: {e}")
    else:
        logger.warning("⚠️ No test image found. Testing with dummy base64...")
        
        # Test with dummy data
        try:
            request_data = {
                "input": "dGVzdA=="  # base64 for "test"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )
                
                logger.info(f"📊 Response Status: {response.status_code}")
                logger.info(f"📄 Response: {response.text}")
                
        except Exception as e:
            logger.error(f"Error with dummy test: {e}")

if __name__ == "__main__":
    logger.info("🚀 Starting Production API Test")
    asyncio.run(test_production_api())
    logger.info("�� Test completed") 