from fastapi import FastAPI, Depends
from models import LocationUpdate
from redis_client import get_redis
import json  

app = FastAPI()

@app.post("/update_location")
async def update_location(location: LocationUpdate, redis = Depends(get_redis)):
    
    value = json.dumps({"lat": location.latitude, "lng": location.longitude})
    await redis.hset("drivers:location", location.driver_id, value)
    return {"message": "Location updated successfully"}
