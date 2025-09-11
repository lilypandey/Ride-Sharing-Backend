import redis.asyncio as aioredis
from fastapi import Depends

REDIS_URL = "redis://redis:6379"

# Creating global Redis pool once
redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)

async def get_redis():
    try:
        yield redis_client
    finally:
        pass
