import asyncio
import json
from aiokafka import AIOKafkaConsumer
from redis_client import get_active_drivers
from utils import haversine_distance
from kafka_producer import publish_match
import os
from aiokafka.errors import KafkaConnectionError

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

async def consume_ride_requests():
    consumer = AIOKafkaConsumer(
        "ride_requests",
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id="ride-match-group",
        auto_offset_reset="earliest"
    )

    # Add Retry Logic for Kafka Startup
    for attempt in range(10):  # Retry 10 times
        try:
            await consumer.start()
            print("Kafka connected")
            break
        except KafkaConnectionError:
            print(f"Kafka not ready yet... retrying ({attempt + 1}/10)")
            await asyncio.sleep(15)
    else:
        print("Kafka connection failed after retries.")
        return  # Give up if Kafka not ready after retries
    

    try:
        async for msg in consumer:
            request = json.loads(msg.value.decode("utf-8"))
            print(f"Received ride request: {request}")
            await handle_request(request)
    finally:
        await consumer.stop()

async def handle_request(request):
    drivers = await get_active_drivers()
    rider_lat = request["pickup_lat"]
    rider_lng = request["pickup_lng"]

    min_distance = float('inf')
    selected_driver = None

    for driver_id, location_json in drivers.items():
        location = json.loads(location_json)
        distance = haversine_distance(rider_lat, rider_lng, location["lat"], location["lng"])
        if distance < min_distance:
            min_distance = distance
            selected_driver = driver_id

    if selected_driver:
        match_payload = {
            "rider_id": request["rider_id"],
            "driver_id": selected_driver,
            "pickup_lat": rider_lat,
            "pickup_lng": rider_lng,
            "estimated_distance_km": min_distance
        }
        await publish_match(match_payload)
    else:
        print("No drivers available!")
