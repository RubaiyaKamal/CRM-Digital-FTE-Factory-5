"""
Kafka producer/consumer helpers using aiokafka.
"""
from __future__ import annotations

import json
import logging
from typing import Any, AsyncGenerator, Dict, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from src.config import settings

logger = logging.getLogger(__name__)

_producer: Optional[AIOKafkaProducer] = None


async def get_producer() -> AIOKafkaProducer:
    """Return (or create) the global Kafka producer."""
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka_brokers,
            value_serializer=lambda v: json.dumps(v).encode(),
        )
        await _producer.start()
        logger.info("Kafka producer started: %s", settings.kafka_brokers)
    return _producer


async def stop_producer() -> None:
    global _producer
    if _producer:
        await _producer.stop()
        _producer = None
        logger.info("Kafka producer stopped")


async def publish(topic: str, payload: Dict[str, Any], key: str | None = None) -> None:
    """Publish a JSON payload to a Kafka topic."""
    producer = await get_producer()
    key_bytes = key.encode() if key else None
    await producer.send_and_wait(topic, value=payload, key=key_bytes)
    logger.debug("Published to %s: %s", topic, list(payload.keys()))


def create_consumer(topics: list[str], group_id: str | None = None) -> AIOKafkaConsumer:
    """Create a new Kafka consumer for the given topics."""
    return AIOKafkaConsumer(
        *topics,
        bootstrap_servers=settings.kafka_brokers,
        group_id=group_id or settings.kafka_consumer_group,
        value_deserializer=lambda v: json.loads(v.decode()),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
