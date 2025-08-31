"""
Test Memoir API Endpoints
Tests the memoir API endpoints for Android app integration
"""
import asyncio
import logging
import requests
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
BASE_URL = "https://backend.vcaremind.io.vn"
USER_ID = "dd8d892b-fa77-4a71-9520-71baf601c3ba"  # User from previous test

class MemoirAPITester:
    """Test class for memoir API endpoints"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.user_id = USER_ID
    
    def test_get_user_memoirs(self):
        """Test getting user memoirs"""
        try:
            url = f"{self.base_url}/api/memoirs/{self.user_id}"
            logger.info(f"Testing GET {url}")
            
            response = requests.get(url)
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Successfully retrieved user memoirs")
                logger.info(f"Response: {data}")
                
                if data.get("success") and "memoirs" in data:
                    memoirs = data["memoirs"]
                    logger.info(f"Found {len(memoirs)} memoirs")
                    
                    for memoir in memoirs:
                        logger.info(f"Memoir: {memoir.get('title', 'No title')} - {memoir.get('id', 'No ID')}")
                else:
                    logger.warning("Response format not as expected")
            else:
                logger.error(f"❌ Failed to get user memoirs: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Error testing get_user_memoirs: {e}")
    
    def test_get_memoir_detail(self):
        """Test getting memoir detail"""
        try:
            # First get memoirs to get an ID
            url = f"{self.base_url}/api/memoirs/{self.user_id}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "memoirs" in data and data["memoirs"]:
                    memoir_id = data["memoirs"][0]["id"]
                    
                    # Now test getting memoir detail
                    detail_url = f"{self.base_url}/api/memoirs/{self.user_id}/{memoir_id}"
                    logger.info(f"Testing GET {detail_url}")
                    
                    detail_response = requests.get(detail_url)
                    logger.info(f"Detail response status: {detail_response.status_code}")
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        logger.info("✅ Successfully retrieved memoir detail")
                        logger.info(f"Detail response: {detail_data}")
                    else:
                        logger.error(f"❌ Failed to get memoir detail: {detail_response.status_code}")
                        logger.error(f"Response: {detail_response.text}")
                else:
                    logger.warning("No memoirs found to test detail endpoint")
            else:
                logger.error("Failed to get memoirs for detail test")
                
        except Exception as e:
            logger.error(f"❌ Error testing get_memoir_detail: {e}")
    
    def test_get_memoir_stats(self):
        """Test getting memoir statistics"""
        try:
            url = f"{self.base_url}/api/memoirs/{self.user_id}/stats"
            logger.info(f"Testing GET {url}")
            
            response = requests.get(url)
            logger.info(f"Stats response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Successfully retrieved memoir stats")
                logger.info(f"Stats response: {data}")
            else:
                logger.error(f"❌ Failed to get memoir stats: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Error testing get_memoir_stats: {e}")
    
    def test_get_memoir_categories(self):
        """Test getting memoir categories"""
        try:
            url = f"{self.base_url}/api/memoirs/{self.user_id}/categories"
            logger.info(f"Testing GET {url}")
            
            response = requests.get(url)
            logger.info(f"Categories response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Successfully retrieved memoir categories")
                logger.info(f"Categories response: {data}")
            else:
                logger.error(f"❌ Failed to get memoir categories: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Error testing get_memoir_categories: {e}")
    
    def test_get_user_stats(self):
        """Test getting user statistics"""
        try:
            url = f"{self.base_url}/api/auth/stats/{self.user_id}"
            logger.info(f"Testing GET {url}")
            
            response = requests.get(url)
            logger.info(f"User stats response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Successfully retrieved user stats")
                logger.info(f"User stats response: {data}")
            else:
                logger.error(f"❌ Failed to get user stats: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Error testing get_user_stats: {e}")
    
    def test_search_memoirs(self):
        """Test searching memoirs"""
        try:
            url = f"{self.base_url}/api/memoirs/{self.user_id}/search"
            search_data = {
                "query": "chiến tranh",
                "limit": 10
            }
            logger.info(f"Testing POST {url}")
            logger.info(f"Search data: {search_data}")
            
            response = requests.post(url, json=search_data)
            logger.info(f"Search response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Successfully searched memoirs")
                logger.info(f"Search response: {data}")
            else:
                logger.error(f"❌ Failed to search memoirs: {response.status_code}")
                logger.error(f"Response: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Error testing search_memoirs: {e}")
    
    def run_all_tests(self):
        """Run all API tests"""
        logger.info("🚀 Starting Memoir API Tests...")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"User ID: {self.user_id}")
        logger.info("=" * 50)
        
        # Test basic endpoints
        self.test_get_user_memoirs()
        logger.info("-" * 30)
        
        self.test_get_memoir_detail()
        logger.info("-" * 30)
        
        self.test_get_memoir_stats()
        logger.info("-" * 30)
        
        self.test_get_memoir_categories()
        logger.info("-" * 30)
        
        self.test_get_user_stats()
        logger.info("-" * 30)
        
        self.test_search_memoirs()
        logger.info("-" * 30)
        
        logger.info("🎉 All API tests completed!")

def main():
    """Main test function"""
    tester = MemoirAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 