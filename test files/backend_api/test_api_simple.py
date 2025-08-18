#!/usr/bin/env python3
"""
Simple test script for the medicine analysis API endpoint
"""
import asyncio
import httpx
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_api_endpoint():
    """Test the API endpoint with a simple request."""
    
    logger.info("🧪 Testing Medicine Analysis API Endpoint")
    
    # Test data - a simple base64 string (not a real image)
    test_data = {
        "input": "dGVzdA=="  # base64 for "test"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info("📡 Sending request to /api/analyze-medicine-gemini")
            
            response = await client.post(
                "http://localhost:8000/api/analyze-medicine-gemini",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            logger.info(f"📊 Response Status: {response.status_code}")
            logger.info(f"📋 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    logger.info("✅ API call successful!")
                    logger.info(f"📄 Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Failed to parse JSON response: {e}")
                    logger.info(f"📄 Raw response: {response.text}")
            else:
                logger.error(f"❌ API call failed with status {response.status_code}")
                logger.info(f"📄 Error response: {response.text}")
                
    except httpx.ConnectError:
        logger.error("❌ Could not connect to server. Make sure the server is running on localhost:8000")
    except httpx.TimeoutException:
        logger.error("❌ Request timed out")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    logger.info("🚀 Starting API Test")
    asyncio.run(test_api_endpoint())
    logger.info("�� Test completed") 