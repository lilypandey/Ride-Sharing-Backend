import asyncio
from aiokafka import AIOKafkaConsumer
import os, json
from database import SessionLocal
import crud

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
MATCH_RESULT_TOPIC = "trip_matches"

async def consume_matches():
    consumer = AIOKafkaConsumer(
        MATCH_RESULT_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id="trip_service_group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    await consumer.start()
    try:
        async for msg in consumer:
            match = msg.value
            trip_id = match["trip_id"]
            driver_id = match["driver_id"]
            distance = match["distance_km"]

            print(f"[Trip Service] Received match for trip {trip_id}: driver {driver_id}")

            db = SessionLocal()
            crud.assign_driver(db, trip_id, driver_id, distance)
            db.close()
    finally:
        await consumer.stop()
