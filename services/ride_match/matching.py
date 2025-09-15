from redis_client import redis_client

async def find_nearest_driver(pickup_lat: float, pickup_lng: float, radius_km: int = 5):
    """
    Uses Redis GEO to find the nearest driver within radius_km.
    Returns (driver_id, distance_in_km) or (None, None) if none found.
    """
    results = await redis_client.geosearch(
        "drivers:locations",
        longitude=pickup_lng,   # Redis expects lng, lat
        latitude=pickup_lat,
        radius=radius_km,
        unit="km",
        withdist=True,
        sort="ASC",   # nearest first
        count=1
    )

    if not results:
        return None, None

    driver_id, distance = results[0]
    return driver_id, float(distance)
