"""
WebSocket connection manager để broadcast voice notifications
"""
import asyncio
import json
import logging
from typing import Set
from fastapi import WebSocket
import datetime

logger = logging.getLogger(__name__)

class WebSocketConnectionManager:
    """Manager để quản lý WebSocket connections và broadcast messages"""
    
    def __init__(self):
        # Set để lưu trữ active WebSocket connections
        self.active_connections: Set[WebSocket] = set()
    
    def add_connection(self, websocket: WebSocket):
        """Thêm WebSocket connection vào danh sách active"""
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connection added. Total connections: {len(self.active_connections)}")
    
    def remove_connection(self, websocket: WebSocket):
        """Xóa WebSocket connection khỏi danh sách active"""
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket connection removed. Total connections: {len(self.active_connections)}")
    
    async def broadcast_voice_notification(self, notification_data: dict):
        """
        Broadcast voice notification tới tất cả connected clients
        
        Args:
            notification_data: Dictionary chứa voice notification data
        """
        if not self.active_connections:
            logger.warning("No active WebSocket connections to broadcast to")
            return
        
        message = {
            "type": "voice_notification_response",
            "success": True,
            "data": notification_data,
            "broadcast": True  # Flag để client biết đây là broadcast message
        }
        
        # List để track failed connections
        failed_connections = []
        
        logger.info(f"Broadcasting voice notification to {len(self.active_connections)} connections")
        
        # Send message to all active connections with better error handling
        for connection in list(self.active_connections):  # Create a copy to avoid modification during iteration
            try:
                # Check connection state before sending safely
                if hasattr(connection, 'client_state') and connection.client_state.name == 'CONNECTED':
                    await asyncio.wait_for(
                        connection.send_text(json.dumps(message)),
                        timeout=10.0  # 10 second timeout for send
                    )
                    logger.debug(f"Voice notification sent to WebSocket connection")
                else:
                    logger.warning("WebSocket not connected, marking for removal")
                    failed_connections.append(connection)
            except asyncio.TimeoutError:
                logger.error("Timeout sending voice notification to WebSocket")
                failed_connections.append(connection)
            except Exception as e:
                logger.error(f"Failed to send voice notification to WebSocket: {e}")
                failed_connections.append(connection)
        
        # Remove failed connections
        for connection in failed_connections:
            self.remove_connection(connection)
        
        logger.info(f"Voice notification broadcast completed. Sent to {len(self.active_connections)} clients")
    
    async def send_to_connection(self, websocket: WebSocket, data: dict):
        """
        Gửi message tới một WebSocket connection cụ thể
        
        Args:
            websocket: WebSocket connection
            data: Data để gửi
        """
        try:
            await websocket.send_text(json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to send data to WebSocket: {e}")
            self.remove_connection(websocket)
            raise
    
    def get_connection_count(self) -> int:
        """Trả về số lượng active connections"""
        return len(self.active_connections)
    
    async def cleanup_dead_connections(self):
        """Cleanup dead or invalid WebSocket connections"""
        dead_connections = []
        
        for connection in list(self.active_connections):
            try:
                # Check if connection is still alive
                if connection.client_state.name != 'CONNECTED':
                    dead_connections.append(connection)
                    continue
                
                # Try to send a ping to check connection health
                try:
                    await asyncio.wait_for(
                        connection.send_text(json.dumps({"type": "ping"})),
                        timeout=5.0
                    )
                except (asyncio.TimeoutError, Exception):
                    dead_connections.append(connection)
                    
            except Exception as e:
                logger.warning(f"Error checking connection health: {e}")
                dead_connections.append(connection)
        
        # Remove dead connections
        for connection in dead_connections:
            self.remove_connection(connection)
        
        if dead_connections:
            logger.info(f"Cleaned up {len(dead_connections)} dead WebSocket connections")
        
        return len(dead_connections)
    
    def get_connection_stats(self) -> dict:
        """Get detailed connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "healthy" if self.active_connections else "no_connections"
        }
    
    async def broadcast_keepalive(self):
        """Send keepalive messages to all connections to maintain stability"""
        if not self.active_connections:
            return
        
        keepalive_message = {
            "type": "keepalive",
            "timestamp": datetime.datetime.now().isoformat(),
            "connection_count": len(self.active_connections)
        }
        
        failed_connections = []
        
        for connection in list(self.active_connections):
            try:
                if connection.client_state.name == 'CONNECTED':
                    await asyncio.wait_for(
                        connection.send_text(json.dumps(keepalive_message)),
                        timeout=5.0
                    )
                else:
                    failed_connections.append(connection)
            except Exception:
                failed_connections.append(connection)
        
        # Remove failed connections
        for connection in failed_connections:
            self.remove_connection(connection)


# Global instance để sử dụng trong toàn bộ application
websocket_manager = WebSocketConnectionManager()
