from typing import List, Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict):
        """Broadcasts a JSON message to all connected dashboard clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Silently fail if connection is stale, it will be cleaned up on close
                pass

ws_manager = ConnectionManager()
