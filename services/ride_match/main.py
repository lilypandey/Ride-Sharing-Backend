from fastapi import FastAPI
import asyncio
from kafka_consumer import consume_trip_requests
from kafka_producer import stop_producer

app = FastAPI(title="ride-match-service")

stop_event = asyncio.Event()
consumer_task: asyncio.Task | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    global consumer_task
    consumer_task = asyncio.create_task(consume_trip_requests(stop_event))

@app.on_event("shutdown")
async def shutdown_event():
    global consumer_task
    stop_event.set()
    if consumer_task:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
    await stop_producer()
