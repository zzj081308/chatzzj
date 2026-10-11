from datetime import datetime, timezone
from fastapi import WebSocket
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class ConnectionManager:
    """Manages active WebSocket connections for the current process."""

    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}  # user_id -> websocket

    async def connect(self, websocket: WebSocket, user_id: int, db: AsyncSession):
        await websocket.accept()
        self.active_connections[user_id] = websocket

        # Mark user online
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_online = True
            await db.commit()

    async def disconnect(self, user_id: int, db: AsyncSession):
        self.active_connections.pop(user_id, None)

        # Mark user offline
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user:
            user.is_online = False
            user.last_seen_at = datetime.now(timezone.utc)
            await db.commit()

    def is_online(self, user_id: int) -> bool:
        return user_id in self.active_connections

    async def send_personal(self, message: dict, user_id: int):
        """Send JSON to a specific connected user."""
        ws = self.active_connections.get(user_id)
        if ws:
            try:
                await ws.send_json(message)
            except Exception:
                pass

    async def broadcast_to_friends(self, user_id: int, friend_ids: list[int], message: dict):
        """Broadcast message to all online friends."""
        for friend_id in friend_ids:
            await self.send_personal(message, friend_id)

    def get_online_friend_ids(self, friend_ids: list[int]) -> list[int]:
        """Return which of the given friend IDs are online."""
        return [fid for fid in friend_ids if fid in self.active_connections]


# Singleton
manager = ConnectionManager()
