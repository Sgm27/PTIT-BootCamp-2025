"""
WebSocket connection manager để broadcast voice notifications
"""
import asyncio
import json
import logging
from typing import Set
from fastapi import WebSocket

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
        
        # Send message to all active connections
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
                logger.debug(f"Voice notification sent to WebSocket connection")
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


# Global instance để sử dụng trong toàn bộ application
websocket_manager = WebSocketConnectionManager()
