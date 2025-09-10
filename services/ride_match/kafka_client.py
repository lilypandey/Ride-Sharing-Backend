import os
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")

async def get_producer():
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()

def get_consumer(topic: str, group_id: str):
    return AIOKafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKER,
        group_id=group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )
