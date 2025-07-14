from fastapi import WebSocket
from typing import Dict, Set, Any

class ConnectionManager:
    def __init__(self):
        # 存储每个房间的WebSocket连接
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_name: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][user_name] = websocket

    def disconnect(self, room_id: str, user_name: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].pop(user_name, None)
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast_to_room(self, room_id: str, message: Any):
        if room_id in self.active_connections:
            for connection in self.active_connections[room_id].values():
                await connection.send_json(message)

    def get_active_users(self, room_id: str) -> Set[str]:
        if room_id in self.active_connections:
            return set(self.active_connections[room_id].keys())
        return set()