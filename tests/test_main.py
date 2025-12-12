
from .utils import build_test_payload
import httpx
import asyncio

async def run_request():
    payload = build_test_payload("csv", file_name='tests/sample_data/normal_data/finance.csv')

    print("Payload", payload)

    # Send payload to main via requests
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "http://localhost:8000/events/alice", json=payload) as response:
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    print("Received:", line[5:].strip())

#asyncio.run(run_request())