import asyncio
from typing import Dict

class UserEventManager:
    def __init__(self):
        self.user_connections: Dict[str, asyncio.Queue] = {}

    async def connect(self, user_id: str):
        queue = asyncio.Queue()
        self.user_connections[user_id] = queue
        return queue

    async def disconnect(self, user_id: str):
        self.user_connections.pop(user_id, None)

    async def publish(self, user_id: str, event_type: str, data: str):
        queue = self.user_connections.get(user_id)
        if queue:
            # Format SSE message with event type + JSON payload
            message = f"event: {event_type}\ndata: {data}\n\n"
            await queue.put(message)

event_manager = UserEventManager()
