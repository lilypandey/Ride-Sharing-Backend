from fastapi import FastAPI, Depends, HTTPException
from redis_client import get_redis
from schemas import LocationUpdate, StatusUpdate
from oauth2 import get_current_user

app = FastAPI(title="driver-location")

@app.post("/update_location")
async def update_location(
    location: LocationUpdate,
    current_user=Depends(get_current_user),
    redis = Depends(get_redis),
):
    if current_user["role"] != "driver":
        raise HTTPException(status_code=403, detail="Only drivers can update location")

    driver_id = str(current_user["user_id"])

    # Update location in GEOSET
    await redis.geoadd("drivers:geo", (location.longitude, location.latitude, driver_id))

    # If driver not marked busy, assume available
    current_status = await redis.hget("driver_status", driver_id)
    if current_status != "busy":
        await redis.hset("driver_status", driver_id, "available")

    return {"message": "Location updated successfully"}


@app.post("/update_status")
async def update_status(
    status: StatusUpdate,
    current_user=Depends(get_current_user),
    redis = Depends(get_redis),
):
    if current_user["role"] != "driver":
        raise HTTPException(status_code=403, detail="Only drivers can update status")

    driver_id = str(current_user["user_id"])
    await redis.hset("driver_status", driver_id, status.status)

    return {"driver_id": driver_id, "new_status": status.status}


@app.get("/nearby_drivers")
async def nearby_drivers(
    lat: float,
    lng: float,
    radius: float,
    current_user=Depends(get_current_user),
    redis = Depends(get_redis),
):
    if current_user["role"] != "rider":
        raise HTTPException(status_code=403, detail="Only riders can search for drivers")

    drivers = await redis.geosearch(
        "drivers:geo",
        longitude=lng,
        latitude=lat,
        radius=radius,
        unit="km",
        withdist=True
    )

    available = []
    for driver_id, dist in [(d[0], d[1]) for d in drivers]:
        status = await redis.hget("driver_status", driver_id)
        if status == "available":
            available.append({"driver_id": driver_id, "distance_km": float(dist)})

    return {"drivers": available}
