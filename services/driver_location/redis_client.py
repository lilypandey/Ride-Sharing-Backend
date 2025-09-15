import os
import redis.asyncio as aioredis
from fastapi import Depends
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

# Creating global Redis pool once
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

async def get_redis():
    try:
        yield redis_client
    finally:
        pass
