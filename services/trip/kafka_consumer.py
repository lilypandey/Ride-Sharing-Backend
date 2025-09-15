import asyncio, os, json
from aiokafka import AIOKafkaConsumer
from database import SessionLocal
import crud

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")  # use docker service name
MATCH_RESULT_TOPIC = "trip_matches"

async def consume_matches():
    consumer = AIOKafkaConsumer(
        MATCH_RESULT_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id="trip_service_group",
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
    await consumer.start()
    print("[Trip Service] Listening for trip match results...")

    try:
        async for msg in consumer:
            try:
                match = msg.value
                trip_id = match.get("trip_id")
                driver_id = match.get("driver_id")
                distance = match.get("distance_km", 0.0)

                print(f"[Trip Service] Match received → trip {trip_id}, driver {driver_id}")

                with SessionLocal() as db:
                    crud.assign_driver(db, trip_id, driver_id, distance)

            except Exception as e:
                print(f"[Trip Service] Error processing message: {e}")

    finally:
        await consumer.stop()

