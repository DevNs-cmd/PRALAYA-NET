"""
WebSocket Manager for real-time streaming
"""

import asyncio
import json
from typing import Dict, List, Set, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict

class WebSocketManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        # Store active connections by stream type
        self.connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        # Store connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, stream_type: str = "general"):
        """Connect a WebSocket client"""
        await websocket.accept()
        
        self.connections[stream_type].add(websocket)
        self.connection_metadata[websocket] = {
            "stream_type": stream_type,
            "connected_at": datetime.now(),
            "client_id": f"client_{len(self.connection_metadata)}"
        }
        
        # Send welcome message
        await self.send_to_client(websocket, {
            "type": "connection",
            "message": f"Connected to {stream_type} stream",
            "client_id": self.connection_metadata[websocket]["client_id"],
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"WebSocket client connected to {stream_type} stream")
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        # Find and remove from all streams
        for stream_type, connections in self.connections.items():
            if websocket in connections:
                connections.remove(websocket)
        
        # Remove metadata
        if websocket in self.connection_metadata:
            metadata = self.connection_metadata[websocket]
            print(f"WebSocket client disconnected from {metadata.get('stream_type', 'unknown')} stream")
            del self.connection_metadata[websocket]
    
    async def send_to_client(self, websocket: WebSocket, data: Dict[str, Any]):
        """Send data to a specific client"""
        try:
            await websocket.send_text(json.dumps(data))
        except Exception as e:
            print(f"Error sending to WebSocket client: {str(e)}")
            self.disconnect(websocket)
    
    async def broadcast_to_stream(self, stream_type: str, data: Dict[str, Any]):
        """Broadcast data to all clients in a stream"""
        if stream_type not in self.connections:
            return
        
        disconnected_clients = []
        
        for websocket in self.connections[stream_type]:
            try:
                await websocket.send_text(json.dumps(data))
            except Exception as e:
                print(f"Error broadcasting to client: {str(e)}")
                disconnected_clients.append(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected_clients:
            self.disconnect(websocket)
    
    async def broadcast_risk_stream(self, data: Dict[str, Any]):
        """Broadcast to risk stream"""
        await self.broadcast_to_stream("risk", data)
    
    async def broadcast_stability_stream(self, data: Dict[str, Any]):
        """Broadcast to stability stream"""
        await self.broadcast_to_stream("stability", data)
    
    async def broadcast_actions_stream(self, data: Dict[str, Any]):
        """Broadcast to actions stream"""
        await self.broadcast_to_stream("actions", data)
    
    async def broadcast_timeline_stream(self, data: Dict[str, Any]):
        """Broadcast to timeline stream"""
        await self.broadcast_to_stream("timeline", data)
    
    async def broadcast_general(self, data: Dict[str, Any]):
        """Broadcast to all clients"""
        for stream_type in self.connections:
            await self.broadcast_to_stream(stream_type, data)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        stats = {
            "total_connections": len(self.connection_metadata),
            "streams": {}
        }
        
        for stream_type, connections in self.connections.items():
            stats["streams"][stream_type] = len(connections)
        
        return stats

# Global WebSocket manager
ws_manager = WebSocketManager()
