#!/usr/bin/env python3
"""
Test script for WebSocket connection stability
"""
import asyncio
import websockets
import json
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebSocketStabilityTester:
    def __init__(self, uri="ws://localhost:8000/gemini-live"):
        self.uri = uri
        self.websocket = None
        self.connection_start_time = None
        self.keepalive_count = 0
        self.message_count = 0
        self.last_activity = None
        
    async def connect(self):
        """Establish WebSocket connection"""
        try:
            logger.info(f"🔌 Connecting to {self.uri}")
            self.websocket = await websockets.connect(self.uri)
            self.connection_start_time = time.time()
            self.last_activity = time.time()
            logger.info("✅ WebSocket connected successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            return False
    
    async def send_config(self):
        """Send initial configuration"""
        try:
            config = {
                "user_id": "test_user_123",
                "session_type": "conversation"
            }
            await self.websocket.send(json.dumps(config))
            logger.info("📤 Sent configuration")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send config: {e}")
            return False
    
    async def send_keepalive(self):
        """Send keepalive message"""
        try:
            keepalive_data = {
                "type": "keepalive",
                "timestamp": datetime.now().isoformat(),
                "count": self.keepalive_count
            }
            await self.websocket.send(json.dumps(keepalive_data))
            self.keepalive_count += 1
            self.last_activity = time.time()
            logger.debug(f"📤 Sent keepalive #{self.keepalive_count}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send keepalive: {e}")
            return False
    
    async def send_test_message(self):
        """Send a test message"""
        try:
            test_message = {
                "text": f"Test message #{self.message_count} at {datetime.now().strftime('%H:%M:%S')}"
            }
            await self.websocket.send(json.dumps(test_message))
            self.message_count += 1
            self.last_activity = time.time()
            logger.info(f"📤 Sent test message #{self.message_count}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send test message: {e}")
            return False
    
    async def listen_for_messages(self):
        """Listen for incoming messages"""
        try:
            while True:
                try:
                    # Set timeout for receiving messages
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=60  # 1 minute timeout
                    )
                    
                    data = json.loads(message)
                    self.last_activity = time.time()
                    
                    # Handle different message types
                    if "type" in data:
                        if data["type"] == "keepalive":
                            logger.debug(f"📥 Received keepalive from server")
                        elif data["type"] == "keepalive_response":
                            logger.debug(f"📥 Received keepalive response from server")
                        elif data["type"] == "transcription":
                            if data.get("text"):
                                logger.info(f"📥 Transcription: {data['text']}")
                        else:
                            logger.info(f"📥 Received message: {data['type']}")
                    elif "text" in data:
                        logger.info(f"📥 Text response: {data['text']}")
                    else:
                        logger.debug(f"📥 Received data: {str(data)[:100]}...")
                        
                except asyncio.TimeoutError:
                    logger.warning("⏰ Timeout waiting for message - connection may be idle")
                    # Don't break, just continue listening
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.error("🔌 WebSocket connection closed by server")
                    break
                except Exception as e:
                    logger.error(f"❌ Error receiving message: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"❌ Error in message listener: {e}")
    
    async def monitor_connection(self):
        """Monitor connection health"""
        try:
            while True:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                if not self.websocket or self.websocket.closed:
                    logger.error("🔌 WebSocket is closed")
                    break
                
                # Check if connection has been idle too long
                idle_time = time.time() - self.last_activity
                if idle_time > 300:  # 5 minutes
                    logger.warning(f"⚠️ Connection idle for {idle_time:.1f} seconds")
                
                # Log connection status
                uptime = time.time() - self.connection_start_time
                logger.info(f"📊 Connection status: {uptime:.1f}s uptime, {self.keepalive_count} keepalives, {self.message_count} messages")
                
        except Exception as e:
            logger.error(f"❌ Error in connection monitor: {e}")
    
    async def run_stability_test(self, duration_minutes=10):
        """Run comprehensive stability test"""
        logger.info(f"🚀 Starting WebSocket stability test for {duration_minutes} minutes")
        
        # Connect
        if not await self.connect():
            return False
        
        # Send initial config
        if not await self.send_config():
            return False
        
        # Start background tasks
        listener_task = asyncio.create_task(self.listen_for_messages())
        monitor_task = asyncio.create_task(self.monitor_connection())
        
        try:
            start_time = time.time()
            keepalive_interval = 20  # Send keepalive every 20 seconds
            message_interval = 60    # Send test message every 60 seconds
            
            while True:
                current_time = time.time()
                elapsed = current_time - start_time
                
                # Check if test duration exceeded
                if elapsed > duration_minutes * 60:
                    logger.info(f"⏰ Test duration ({duration_minutes} minutes) completed")
                    break
                
                # Send keepalive periodically
                if int(elapsed) % keepalive_interval == 0:
                    await self.send_keepalive()
                
                # Send test message periodically
                if int(elapsed) % message_interval == 0 and int(elapsed) > 0:
                    await self.send_test_message()
                
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("🛑 Test interrupted by user")
        except Exception as e:
            logger.error(f"❌ Test error: {e}")
        finally:
            # Cancel background tasks
            listener_task.cancel()
            monitor_task.cancel()
            
            # Close connection
            if self.websocket:
                await self.websocket.close()
                logger.info("🔌 WebSocket connection closed")
            
            # Log final statistics
            total_time = time.time() - self.connection_start_time
            logger.info(f"📈 Test completed:")
            logger.info(f"   - Total time: {total_time:.1f} seconds")
            logger.info(f"   - Keepalives sent: {self.keepalive_count}")
            logger.info(f"   - Messages sent: {self.message_count}")
            logger.info(f"   - Average keepalive interval: {total_time/max(1, self.keepalive_count):.1f}s")

async def main():
    """Main test function"""
    tester = WebSocketStabilityTester()
    await tester.run_stability_test(duration_minutes=15)  # Test for 15 minutes

if __name__ == "__main__":
    asyncio.run(main()) 