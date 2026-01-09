# import pytest
# import pytest_asyncio
# import json
# from httpx import AsyncClient
# from typing import AsyncGenerator


# # 1. Fixture configured for Real Server
# @pytest_asyncio.fixture
# async def client() -> AsyncGenerator[AsyncClient, None]:
#     # We remove 'transport=...' and 'app=...'
#     # We set base_url to your actual running server
#     async with AsyncClient(base_url="http://localhost:8000") as ac:
#         yield ac

# @pytest.mark.asyncio
# async def test_sse_stream(client: AsyncClient):
        
#     # 1. Create the session data on the real server
#     # Note: Ensure your server code allows this (GET vs POST issue discussed earlier)
#     save_response = await client.post("/save", json={"name": "Real Network Test", "user_id": "test_user"})
#     assert save_response.status_code == 200
    
#     # Grab the user_id if the server returns a different one
#     user_id = save_response.json()["user_id"]

#     print(f"\nConnecting to SSE stream for user: {user_id}...")

#     # 2. Connect to the real SSE stream over the network
#     async with client.stream("GET", f"/events/{user_id}") as response:
#         assert response.status_code == 200
        
#         count = 0
#         async for line in response.aiter_lines():
#             if line:
#                 print(f"Network Received: {line}")
#                 count += 1

#             # STOP CONDITION
#             # Wait for 'result' or max 5 messages to avoid hanging indefinitely
#             if "result" in line or count >= 5:
#                 break

# #NOTE: Ensure to comment necessasary parts of main.py when running this file