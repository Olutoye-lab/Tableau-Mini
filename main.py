from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio

from pipeline import run_pipline
from sse_manager import event_manager

app = FastAPI()

async def event_stream(queue: asyncio.Queue):
    try:
        while True:
            message = await queue.get()
            yield message
    except asyncio.CancelledError:
        pass

# user_id is a combination of credentials
@app.get("/events/{user_id}")
async def sse(user_id: str, request: Request):
    
   payload = await request.json()
   
   #asyncio.create_task(run_pipline(payload, user_id))

   queue = await event_manager.connect(user_id)

   async def stream():
        try:
            async for chunk in event_stream(queue):
                yield chunk
        finally:
            await event_manager.disconnect(user_id)

   return StreamingResponse(stream(), media_type="text/event-stream")


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