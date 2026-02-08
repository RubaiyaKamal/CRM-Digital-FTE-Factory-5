"""
Kafka consumer: fte.tickets.incoming → runs OpenAI agent → publishes fte.responses.outgoing
"""
from __future__ import annotations

import asyncio
import json
import logging

from src.agent.customer_success_agent import CustomerSuccessAgent
from src.agent.models import AgentTask, Channel
from src.config import settings
from src.database.connection import create_pool, apply_schema
from src.kafka_client import create_consumer, get_producer, publish

logger = logging.getLogger(__name__)


async def run():
    """Main consumer loop."""
    logging.basicConfig(level=settings.log_level)
    logger.info("Message processor starting...")

    # Init DB
    from src.database import connection as db_module
    db_module._pool = await create_pool()
    await apply_schema(db_module._pool)

    # Init Kafka producer (for outgoing)
    await get_producer()

    # Init agent
    agent = CustomerSuccessAgent()

    consumer = create_consumer(
        [settings.kafka_topic_incoming],
        group_id=f"{settings.kafka_consumer_group}-processor",
    )
    await consumer.start()
    logger.info("Consuming from %s", settings.kafka_topic_incoming)

    try:
        async for msg in consumer:
            try:
                await _process_message(agent, msg.value)
            except Exception as exc:
                logger.error("Failed to process message: %s", exc, exc_info=True)
    finally:
        await consumer.stop()
        logger.info("Consumer stopped")


async def _process_message(agent: CustomerSuccessAgent, payload: dict):
    """Process a single Kafka message."""
    logger.info("Processing ticket %s", payload.get("ticket_id"))

    # Load conversation history from DB
    from src.database.connection import get_db_pool
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        history_rows = await conn.fetch(
            """
            SELECT role, content FROM messages
            WHERE conversation_id = $1
            ORDER BY created_at ASC
            LIMIT 10
            """,
            payload["conversation_id"],
        )
    history = [{"role": r["role"], "content": r["content"]} for r in history_rows]

    task = AgentTask(
        ticket_id=payload["ticket_id"],
        conversation_id=payload["conversation_id"],
        customer_id=payload["customer_id"],
        customer_identifier=payload["customer_identifier"],
        channel=Channel(payload["channel"]),
        message_text=payload["message_text"],
        subject=payload.get("subject"),
        conversation_history=history,
    )

    result = await agent.process(task)

    # Publish result to outgoing topic
    outgoing = {
        "ticket_id": result.ticket_id,
        "customer_id": result.customer_id,
        "customer_identifier": payload["customer_identifier"],
        "channel": result.channel.value,
        "response_text": result.response_text,
        "should_escalate": result.should_escalate,
        "escalation_reason": result.escalation_reason,
        "escalation_priority": result.escalation_priority.value if result.escalation_priority else None,
        "sentiment_score": result.sentiment_score,
        "latency_ms": result.latency_ms,
        "conversation_id": payload["conversation_id"],
    }
    await publish(settings.kafka_topic_outgoing, outgoing, key=result.customer_id)
    logger.info("Published response for ticket %s (escalate=%s)", result.ticket_id, result.should_escalate)


if __name__ == "__main__":
    asyncio.run(run())
