import os, json, asyncio
from aiokafka import AIOKafkaConsumer
from matching import find_nearest_driver
from kafka_producer import publish_match_result

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
TRIP_REQUESTS_TOPIC = "trip_requests"

async def consume_trip_requests(stop_event: asyncio.Event):
    consumer = AIOKafkaConsumer(
        TRIP_REQUESTS_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id="ride_match_group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    await consumer.start()
    print("[Ride-Match] Listening for trip requests...")

    try:
        while not stop_event.is_set():
            msg = await consumer.getone()
            trip = msg.value
            trip_id = trip.get("trip_id")
            rider_id = trip.get("rider_id")
            pickup_lat = float(trip.get("pickup_lat"))
            pickup_lng = float(trip.get("pickup_lng"))

            print(f"[Ride-Match] Trip request received → trip {trip_id}, rider {rider_id}")

            driver_id, dist = await find_nearest_driver(pickup_lat, pickup_lng)
            if driver_id:
                print(f"[Ride-Match] Found driver {driver_id} at distance {dist:.2f}")
                payload = {
                    "trip_id": trip_id,
                    "rider_id": rider_id,
                    "driver_id": driver_id,
                    "distance_km": dist
                }
                await publish_match_result(payload)
            else:
                print("[Ride-Match] No drivers available")

    except asyncio.CancelledError:
        print("[Ride-Match] Consumer cancelled, shutting down...")
    finally:
        await consumer.stop()

