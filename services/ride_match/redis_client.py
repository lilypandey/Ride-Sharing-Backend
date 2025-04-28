import redis.asyncio as aioredis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

async def get_redis():
    redis = await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    return redis

async def get_active_drivers():
    redis = await get_redis()
    drivers = await redis.hgetall("drivers:location", encoding="utf-8")
    await redis.close()
    return drivers
