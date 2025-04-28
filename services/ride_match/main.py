from fastapi import FastAPI
import asyncio
from kafka_consumer import consume_ride_requests

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ride-match service running"}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_ride_requests())
