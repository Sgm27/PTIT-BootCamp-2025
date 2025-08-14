#!/usr/bin/env python3
"""
Test script để kiểm tra tính ổn định kết nối WebSocket và HTTP API
"""
import asyncio
import websockets
import json
import time
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "https://backend-bootcamp.sonktx.online"
WEBSOCKET_URL = "wss://backend-bootcamp.sonktx.online/gemini-live"
TEST_DURATION = 300  # 5 minutes
HEALTH_CHECK_INTERVAL = 30  # 30 seconds

class ConnectionTester:
    def __init__(self):
        self.websocket = None
        self.connection_stats = {
            "start_time": None,
            "end_time": None,
            "total_connections": 0,
            "successful_connections": 0,
            "failed_connections": 0,
            "total_messages_sent": 0,
            "total_messages_received": 0,
            "connection_durations": [],
            "errors": []
        }
    
    async def test_websocket_connection(self):
        """Test WebSocket connection stability"""
        logger.info("🔌 Starting WebSocket connection test...")
        
        try:
            # Test initial connection
            logger.info(f"Connecting to {WEBSOCKET_URL}")
            self.websocket = await websockets.connect(WEBSOCKET_URL)
            logger.info("✅ WebSocket connected successfully")
            
            # Send initial config with valid UUID
            config_message = {
                "user_id": "550e8400-e29b-41d4-a716-446655440000"  # Valid UUID format
            }
            await self.websocket.send(json.dumps(config_message))
            logger.info("📤 Sent initial config message")
            
            # Start connection monitoring
            start_time = time.time()
            self.connection_stats["start_time"] = datetime.now()
            
            while time.time() - start_time < TEST_DURATION:
                try:
                    # Send ping message
                    ping_message = {"type": "ping"}
                    await self.websocket.send(json.dumps(ping_message))
                    self.connection_stats["total_messages_sent"] += 1
                    
                    # Wait for response
                    response = await asyncio.wait_for(
                        self.websocket.recv(), 
                        timeout=10.0
                    )
                    self.connection_stats["total_messages_received"] += 1
                    
                    logger.info(f"📡 Ping successful - Messages: {self.connection_stats['total_messages_sent']} sent, {self.connection_stats['total_messages_received']} received")
                    
                    # Wait before next ping
                    await asyncio.sleep(HEALTH_CHECK_INTERVAL)
                    
                except asyncio.TimeoutError:
                    logger.warning("⚠️ Timeout waiting for response")
                    self.connection_stats["errors"].append({
                        "time": datetime.now().isoformat(),
                        "type": "timeout",
                        "message": "No response received within 10 seconds"
                    })
                except Exception as e:
                    logger.error(f"❌ Error during connection test: {e}")
                    self.connection_stats["errors"].append({
                        "time": datetime.now().isoformat(),
                        "type": "error",
                        "message": str(e)
                    })
                    break
            
            # Calculate connection duration
            connection_duration = time.time() - start_time
            self.connection_stats["connection_durations"].append(connection_duration)
            self.connection_stats["successful_connections"] += 1
            
            logger.info(f"✅ WebSocket test completed - Duration: {connection_duration:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to establish WebSocket connection: {e}")
            self.connection_stats["failed_connections"] += 1
            self.connection_stats["errors"].append({
                "time": datetime.now().isoformat(),
                "type": "connection_failed",
                "message": str(e)
            })
        finally:
            if self.websocket:
                await self.websocket.close()
                logger.info("🔌 WebSocket connection closed")
    
    def test_http_api(self):
        """Test HTTP API endpoints"""
        logger.info("🌐 Starting HTTP API test...")
        
        try:
            # Test health endpoint
            health_url = f"{BACKEND_URL}/health"
            response = requests.get(health_url, timeout=30)
            
            if response.status_code == 200:
                logger.info("✅ Health endpoint working")
                health_data = response.json()
                logger.info(f"📊 Health data: {health_data}")
            else:
                logger.error(f"❌ Health endpoint failed: {response.status_code}")
                self.connection_stats["errors"].append({
                    "time": datetime.now().isoformat(),
                    "type": "health_check_failed",
                    "message": f"Status code: {response.status_code}"
                })
                
        except requests.exceptions.Timeout:
            logger.error("❌ Health endpoint timeout")
            self.connection_stats["errors"].append({
                "time": datetime.now().isoformat(),
                "type": "health_timeout",
                "message": "Health check timed out after 30 seconds"
            })
        except Exception as e:
            logger.error(f"❌ HTTP API test failed: {e}")
            self.connection_stats["errors"].append({
                "time": datetime.now().isoformat(),
                "type": "http_error",
                "message": str(e)
            })
    
    def print_summary(self):
        """Print test summary"""
        self.connection_stats["end_time"] = datetime.now()
        
        logger.info("\n" + "="*60)
        logger.info("📊 CONNECTION STABILITY TEST SUMMARY")
        logger.info("="*60)
        
        # Test duration
        if self.connection_stats["start_time"] and self.connection_stats["end_time"]:
            duration = self.connection_stats["end_time"] - self.connection_stats["start_time"]
            logger.info(f"⏱️  Test Duration: {duration}")
        
        # Connection stats
        total_connections = self.connection_stats["successful_connections"] + self.connection_stats["failed_connections"]
        success_rate = (self.connection_stats["successful_connections"] / total_connections * 100) if total_connections > 0 else 0
        
        logger.info(f"🔌 Total Connection Attempts: {total_connections}")
        logger.info(f"✅ Successful Connections: {self.connection_stats['successful_connections']}")
        logger.info(f"❌ Failed Connections: {self.connection_stats['failed_connections']}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        
        # Message stats
        logger.info(f"📤 Messages Sent: {self.connection_stats['total_messages_sent']}")
        logger.info(f"📥 Messages Received: {self.connection_stats['total_messages_received']}")
        
        if self.connection_stats["total_messages_sent"] > 0:
            response_rate = (self.connection_stats["total_messages_received"] / self.connection_stats["total_messages_sent"] * 100)
            logger.info(f"📊 Response Rate: {response_rate:.1f}%")
        
        # Connection durations
        avg_duration = 0
        if self.connection_stats["connection_durations"]:
            avg_duration = sum(self.connection_stats["connection_durations"]) / len(self.connection_stats["connection_durations"])
            max_duration = max(self.connection_stats["connection_durations"])
            min_duration = min(self.connection_stats["connection_durations"])
            
            logger.info(f"⏱️  Average Connection Duration: {avg_duration:.2f}s")
            logger.info(f"⏱️  Max Connection Duration: {max_duration:.2f}s")
            logger.info(f"⏱️  Min Connection Duration: {min_duration:.2f}s")
        
        # Errors
        if self.connection_stats["errors"]:
            logger.info(f"⚠️  Total Errors: {len(self.connection_stats['errors'])}")
            error_types = {}
            for error in self.connection_stats["errors"]:
                error_type = error["type"]
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            logger.info("🔍 Error Breakdown:")
            for error_type, count in error_types.items():
                logger.info(f"   - {error_type}: {count}")
        else:
            logger.info("✅ No errors encountered")
        
        # Recommendations
        logger.info("\n💡 RECOMMENDATIONS:")
        
        if success_rate < 90:
            logger.info("   ⚠️  Connection success rate is low - check network stability")
        
        if self.connection_stats["errors"]:
            logger.info("   ⚠️  Errors detected - review error types above")
        
        if avg_duration > 0 and avg_duration < TEST_DURATION * 0.8:
            logger.info("   ⚠️  Connections are dropping early - check timeout settings")
        
        if response_rate < 90:
            logger.info("   ⚠️  Low response rate - check server responsiveness")
        
        logger.info("="*60)

async def main():
    """Main test function"""
    logger.info("🚀 Starting Connection Stability Test")
    logger.info(f"🎯 Target: {BACKEND_URL}")
    logger.info(f"⏱️  Duration: {TEST_DURATION} seconds")
    logger.info(f"📡 Health Check Interval: {HEALTH_CHECK_INTERVAL} seconds")
    
    tester = ConnectionTester()
    
    # Test HTTP API first
    tester.test_http_api()
    
    # Test WebSocket connection
    await tester.test_websocket_connection()
    
    # Print summary
    tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main()) 