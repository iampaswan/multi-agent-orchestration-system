# from backend.mayor.mayor import create_convoy
# from workers.task import execute_convoy


from fastapi import FastAPI, WebSocket
app = FastAPI()


import redis
import asyncio
import time
r = redis.Redis(host="localhost", port=6379, db=0)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



r = redis.Redis(host="localhost", port=6379, db=0)

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()

    pubsub = r.pubsub()
    pubsub.subscribe(f"stream:{task_id}")

    while True:
        message = pubsub.get_message()
        print(f"Redis message: {message}")

        if message and message["type"] == "message":
            data = message["data"].decode("utf-8")

            await websocket.send_text(data)

            if data == "[DONE]":
                break;
    
    
        await asyncio.sleep(0.1)


import uuid
from backend.mayor.mayor import create_convoy
from backend.mayor.mayor import execute_convoy



@app.post("/research")
def research(query: str):

    convoy = create_convoy(query)  
    task_id = str(uuid.uuid4())

    execute_convoy(task_id, convoy)   

    return {
        "task_id": task_id,
        "plan": convoy,
    }




