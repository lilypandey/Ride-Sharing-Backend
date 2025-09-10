import json
from aiokafka import AIOKafkaProducer
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
producer: AIOKafkaProducer | None = None

async def get_producer() -> AIOKafkaProducer:
    global producer
    if not producer:
        producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        await producer.start()
    return producer

async def publish_trip_request(payload: dict):
    prod = await get_producer()
    await prod.send_and_wait("trip_requests", payload)
