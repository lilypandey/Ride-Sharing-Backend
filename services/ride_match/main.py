import asyncio
from fastapi import FastAPI
from kafka_client import get_consumer, get_producer
from redis_client import get_redis
from schemas import MatchResult
import logging

app = FastAPI(title="ride-match")

TRIP_REQUEST_TOPIC = "trip_requests"
MATCH_RESULT_TOPIC = "trip_matches"

logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()

    # Start Kafka consumer background task
    loop.create_task(consume_trip_requests())


async def consume_trip_requests():
    consumer = get_consumer(TRIP_REQUEST_TOPIC, group_id="ride_match_group")
    await consumer.start()
    try:
        async for msg in consumer:
            trip_request = msg.value
            await handle_trip_request(trip_request)
    finally:
        await consumer.stop()


async def handle_trip_request(trip_request):
    """
    trip_request = {
        "trip_id": 101,
        "rider_id": "7",
        "origin_lat": 19.07,
        "origin_lng": 72.87,
        "destination": "Bandra"
    }
    """
    from redis_client import get_redis
    from kafka_client import get_producer

    # Redis connection
    async for redis in get_redis():
        # Find nearby drivers (within 5km for example)
        drivers = await redis.geosearch(
            "drivers:geo",
            longitude=trip_request["origin_lng"],
            latitude=trip_request["origin_lat"],
            radius=5,
            unit="km",
            withdist=True
        )

        chosen_driver = None
        chosen_dist = None

        for driver_id, dist in [(d[0], d[1]) for d in drivers]:
            status = await redis.hget("driver_status", driver_id)
            if status == "available":
                chosen_driver = driver_id
                chosen_dist = float(dist)
                break  # pick first available driver
       
        if not chosen_driver:
            logger.warning(f"No drivers available for trip {trip_request['trip_id']}")
            return

        # Mark driver busy in Redis
        await redis.hset("driver_status", chosen_driver, "busy")

    # Publish match result to Kafka
    match = MatchResult(
        trip_id=trip_request["trip_id"],
        rider_id=trip_request["rider_id"],
        driver_id=chosen_driver,
        distance_km=chosen_dist
    )

    async for producer in get_producer():
        await producer.send_and_wait(MATCH_RESULT_TOPIC, match.dict())

    logger.info(f"Matched driver {chosen_driver} to trip {trip_request['trip_id']}")
