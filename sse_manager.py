import asyncio
from typing import Dict

class UserEventManager:
    def __init__(self):
        self.user_connections: Dict[str, asyncio.Queue] = {}

    async def connect(self, user_id: str):
        print(f"[SSE_MANAGER] connect() called for user_id: {user_id}")
        queue = asyncio.Queue()
        self.user_connections[user_id] = queue
        print(f"[SSE_MANAGER] Queue created. Active connections: {list(self.user_connections.keys())}")
        return queue

    async def disconnect(self, user_id: str):
        print(f"[SSE_MANAGER] disconnect() called for user_id: {user_id}")
        self.user_connections.pop(user_id, None)
        print(f"[SSE_MANAGER] Active connections: {list(self.user_connections.keys())}")

    async def publish(self, user_id: str, event_type: str, data: str):
        print(f"[SSE_MANAGER] publish() called - user_id: {user_id}, event_type: {event_type}")
        print(f"[SSE_MANAGER] Current connections: {list(self.user_connections.keys())}")
        
        queue = self.user_connections.get(user_id)
        if queue:
            # Format SSE message with event type + JSON payload
            message = f"event: {event_type}\ndata: {data}\n\n"
            print(f"[SSE_MANAGER] Formatted message (first 100 chars): {message[:100]}")
            try:
                await queue.put(message)
                print(f"[SSE_MANAGER] ✅ Message successfully added to queue")
            except Exception as e:
                print(f"[SSE_MANAGER] ❌ Unable to publish event. Event: {event_type} Error: {e}")
        else:
            print(f"[SSE_MANAGER] ❌ No queue found for user_id: {user_id}")

event_manager = UserEventManager()