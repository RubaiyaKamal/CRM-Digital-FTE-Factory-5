"""
Kafka consumer: fte.responses.outgoing → formats for channel → sends → updates DB
"""
from __future__ import annotations

import asyncio
import json
import logging

from src.agent.formatters import format_response
from src.agent.models import Channel
from src.channels.gmail import GmailAdapter
from src.channels.whatsapp import WhatsAppAdapter
from src.channels.web_form import WebFormAdapter
from src.config import settings
from src.database.connection import create_pool, get_db_pool
from src.kafka_client import create_consumer

logger = logging.getLogger(__name__)

_channel_adapters = {
    "email": GmailAdapter(),
    "whatsapp": WhatsAppAdapter(),
    "web_form": WebFormAdapter(),
}


async def run():
    """Main consumer loop for response handler."""
    logging.basicConfig(level=settings.log_level)
    logger.info("Response handler starting...")

    from src.database import connection as db_module
    db_module._pool = await create_pool()

    consumer = create_consumer(
        [settings.kafka_topic_outgoing],
        group_id=f"{settings.kafka_consumer_group}-response",
    )
    await consumer.start()
    logger.info("Consuming from %s", settings.kafka_topic_outgoing)

    try:
        async for msg in consumer:
            try:
                await _handle_response(msg.value)
            except Exception as exc:
                logger.error("Failed to handle response: %s", exc, exc_info=True)
    finally:
        await consumer.stop()


async def _handle_response(payload: dict):
    """Format and send a response via the appropriate channel."""
    channel_name = payload["channel"]
    channel = Channel(channel_name)
    customer_identifier = payload["customer_identifier"]
    response_text = payload["response_text"]
    ticket_id = payload["ticket_id"]
    conversation_id = payload["conversation_id"]

    # Format for channel
    formatted = format_response(response_text, channel, customer_identifier)

    # Send via channel adapter
    adapter = _channel_adapters.get(channel_name)
    if adapter:
        await adapter.send(customer_identifier, formatted, session_id=customer_identifier)

    # Record metrics in DB
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO agent_metrics (ticket_id, model, latency_ms, escalated)
            VALUES ($1, $2, $3, $4)
            """,
            ticket_id,
            settings.openai_model,
            payload.get("latency_ms", 0),
            payload.get("should_escalate", False),
        )

    logger.info(
        "Response delivered: channel=%s customer=%s ticket=%s escalated=%s",
        channel_name, customer_identifier, ticket_id, payload.get("should_escalate"),
    )


if __name__ == "__main__":
    asyncio.run(run())
