from backend.mayor.mayor import create_convoy
from workers.task import execute_convoy


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
                break

        if time.time() - last_sent > 10:
            await websocket.send_text("__ping__")
            last_sent = time.time()
    

        await asyncio.sleep(0.1)


import uuid
from backend.mayor.mayor import create_convoy

@app.post("/research")
def research(query: str):
    convoy = create_convoy(query)  

    task_id = str(uuid.uuid4())

    execute_convoy.delay(task_id, convoy)   

    return {
        "task_id": task_id
    }








# @app.post("/research")
# def research(query: str):
#     task_id = str(uuid.uuid4())

#     print("Sending task to worker:", task_id)

#     execute_convoy.delay(task_id, query)

#     return {"task_id": task_id}


# @app.get("/result/{task_id}")
# def get_result(task_id: str):
    from workers.celery_app import celery
    result = celery.AsyncResult(task_id)

    print(f"Checking result for task {task_id}: status={result.status}")

    return {
        "status": result.status,
        "result": result.result
    }