import redis.asyncio as aioredis
from fastapi import Depends

REDIS_URL = "redis://redis:6379"

async def get_redis():
    redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()
