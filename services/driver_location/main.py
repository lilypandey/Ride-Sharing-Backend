from fastapi import FastAPI, Depends, HTTPException
from models import LocationUpdate
from redis_client import get_redis

app = FastAPI()

@app.post("/update_location")
async def update_location(location: LocationUpdate, redis = Depends(get_redis)):
    key = f"driver:{location.driver_id}"
    value = {
        "latitude": location.latitude,
        "longitude": location.longitude
    }
    await redis.hset(key, mapping=value)
    return {"message": "Location updated successfully"}
