import json
from aiokafka import AIOKafkaProducer
import os

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")

producer = None

async def get_producer():
    global producer
    if not producer:
        producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP)
        await producer.start()
    return producer

async def publish_match(match_payload):
    producer = await get_producer()
    await producer.send_and_wait("ride_matches", json.dumps(match_payload).encode("utf-8"))
