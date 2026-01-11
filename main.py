from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from typing import Dict
# Comment this import when using test-sse.py
from pipeline import run_pipeline
from sse_manager import event_manager
from dotenv import load_dotenv

from upstash_redis import Redis
import uuid
import json
import asyncio
import os
import uvicorn


app = FastAPI()

load_dotenv()

@app.middleware("http")
async def set_scheme_to_https(request: Request, call_next):
    # This tells FastAPI to treat the request as HTTPS
    # which prevents it from generating 'http' redirects
    request.scope['scheme'] = 'https'
    response = await call_next(request)
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, dict] = {}

redis_url = os.getenv("REDIS_URL") or ""
redis_token = os.getenv("REDIS_TOKEN") or ""
redis_client = Redis(url=redis_url, token=redis_token)

# # uncomment this function when using test-see.py
# # --- Test Pipeline Logic ---
# async def run_pipeline(payload: dict, user_id: str):
#     """
#     Simulates a long-running task and publishes events to the specific user.
#     """
#     print(f"\n[PIPELINE] ▶️  Started for user_id: {user_id}")
#     print(f"[PIPELINE] Payload: {payload}")
    
#     try:
#         # Step 1: Notify start
#         print(f"[PIPELINE] Step 1: Publishing 'status' event...")
#         await event_manager.publish(
#             user_id, 
#             event_type="status", 
#             data="Pipeline started. Initializing..."
#         )
#         print(f"[PIPELINE] Step 1: Sleeping 1 second...")
#         await asyncio.sleep(1)

#         # Step 2: Process payload data
#         data_name = payload.get("name", "Unknown Data")
#         print(f"[PIPELINE] Step 2: Publishing 'log' event...")
#         await event_manager.publish(
#             user_id, 
#             event_type="log", 
#             data=f"Processing payload for: {data_name}"
#         )
#         print(f"[PIPELINE] Step 2: Sleeping 2 seconds...")
#         await asyncio.sleep(2)

#         # Step 3: Progress update
#         print(f"[PIPELINE] Step 3: Publishing 'progress' event...")
#         await event_manager.publish(
#             user_id, 
#             event_type="progress", 
#             data=json.dumps({"percent": 50, "message": "Halfway there"})
#         )
#         print(f"[PIPELINE] Step 3: Sleeping 1 second...")
#         await asyncio.sleep(1)

#         # Step 4: Completion
#         print(f"[PIPELINE] Step 4: Publishing 'result' event...")
#         result = {"result_id": str(uuid.uuid4()), "status": "success"}
#         await event_manager.publish(
#             user_id, 
#             event_type="result", 
#             data=json.dumps(result)
#         )
        
#         print(f"[PIPELINE] ✅ Completed successfully for user_id: {user_id}\n")

#     except Exception as e:
#         print(f"[PIPELINE] ❌ Exception caught: {type(e).__name__}: {e}")
#         import traceback
#         traceback.print_exc()
        
#         # Handle crashes gracefully so the frontend knows it failed
#         await event_manager.publish(
#             user_id, 
#             event_type="error", 
#             data=str(e)
#         )

async def event_stream(queue: asyncio.Queue):
    try:
        while True:
            message = await queue.get()
            yield message
    except asyncio.CancelledError:
        pass

@app.post("/save")
async def save(request: Request):
    payload = await request.json()

    user_id = payload["user_id"]

    if user_id == "":
        user_id = str(uuid.uuid4())

    if (type(payload) == dict):
        payload = json.dumps(payload)

    redis_client.set(user_id, payload)
    
    return {"user_id": user_id}

@app.get("/events/{user_id}")
async def sse(user_id: str):
    print(f"\n{'='*60}")
    print(f"[SSE ENDPOINT] New connection request for user_id: {user_id}")
    print(f"{'='*60}\n")
    
    payload = redis_client.get(user_id)

    if payload is None:
        raise HTTPException(status_code=404, detail="User ID not found")
        
    payload = json.loads(payload)

    # Connect queue first
    queue = await event_manager.connect(user_id)
    
    # Send initial connection event through queue
    await event_manager.publish(
        user_id,
        event_type="connected",
        data=json.dumps({"user_id": user_id, "status": "connected"})
    )
    
    # Start pipeline
    asyncio.create_task(run_pipeline(payload, user_id))
    
    async def stream():
        try:
            print(f"[STREAM] Starting event loop for user {user_id}")
            chunk_count = 0
            
            # This loop should run indefinitely until client disconnects
            while True:
                print(f"[STREAM] Waiting for next message from queue...")
                message = await queue.get()
                chunk_count += 1
                print(f"[STREAM] Chunk #{chunk_count} received")
                print(f"[STREAM] Content: {message[:100]}")
                yield message
                
        except asyncio.CancelledError:
            print(f"[STREAM] ⚠️  Client disconnected (CancelledError)")
        except Exception as e:
            print(f"[STREAM] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print(f"[STREAM] Cleanup: Disconnecting user {user_id}")
            await event_manager.disconnect(user_id)
    
    return StreamingResponse(
        stream(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@app.post("/notify/{user_id}")
async def notify(user_id: str, msg: str):
    await event_manager.publish(user_id, event_type="normal", data=msg)
    return {"status": "sent"}

@app.get("/hello")
def read_hello(name: str = "World"):
   return {"message": f"Hello, {name}!"}

@app.get("/")
def root():
   return {"data": "Heath Check Sucessfull"}

if __name__  == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app=app, host="0.0.0.0", port=port, proxy_headers=True, forwarded_allow_ips="*")