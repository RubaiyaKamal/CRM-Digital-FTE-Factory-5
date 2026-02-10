"""
Webhook endpoints for all three channels.
POST /webhooks/{channel} → validate → DB → Kafka → 200 OK
"""
from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request, status

from src.agent.models import Channel
from src.channels.gmail import GmailAdapter
from src.channels.whatsapp import WhatsAppAdapter
from src.channels.web_form import WebFormAdapter
from src.config import settings
from src.database.connection import get_db_pool
from src.kafka_client import publish

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

_adapters = {
    "email": GmailAdapter(),
    "whatsapp": WhatsAppAdapter(),
    "web_form": WebFormAdapter(),
}


@router.post("/{channel}", status_code=status.HTTP_200_OK)
async def receive_webhook(channel: str, request: Request):
    """
    Receive a webhook from any channel.
    Validates → persists → publishes → returns 200 immediately.
    """
    if channel not in _adapters:
        raise HTTPException(status_code=404, detail=f"Unknown channel: {channel}")

    adapter = _adapters[channel]

    # Parse body (Twilio sends form data, not JSON)
    try:
        body = await request.body()
        if channel == "whatsapp":
            # Twilio sends form-encoded data
            form_data = await request.form()
            payload = dict(form_data)
        else:
            # Other channels send JSON
            payload = await request.json()
    except Exception as exc:
        logger.error(f"Failed to parse request body: {exc}")
        raise HTTPException(status_code=400, detail="Invalid request body")

    # Validate Twilio signature for WhatsApp
    if channel == "whatsapp":
        sig = request.headers.get("X-Twilio-Signature", "")
        if not adapter.validate_signature(body, sig):
            raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    # Normalize payload
    try:
        webhook = adapter.normalize(payload)
    except Exception as exc:
        logger.error("Payload normalization failed: %s", exc)
        raise HTTPException(status_code=422, detail="Cannot parse webhook payload")

    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Upsert customer
        customer_id = await _upsert_customer(conn, webhook.customer_identifier, webhook.identifier_type)

        # Create/find conversation
        conversation_id = await _get_or_create_conversation(
            conn, customer_id, webhook.channel.value, webhook.subject
        )

        # Store incoming message with metadata
        message_metadata = {
            "raw_message_id": webhook.message_id,
            "subject": webhook.subject,
        }
        # Add channel-specific metadata (e.g., gmail_thread_id for email)
        if hasattr(webhook, "metadata") and webhook.metadata:
            message_metadata.update(webhook.metadata)

        message_id = await conn.fetchval(
            """
            INSERT INTO messages (conversation_id, role, content, channel, metadata)
            VALUES ($1, 'customer', $2, $3, $4::jsonb)
            RETURNING id
            """,
            conversation_id,
            webhook.message_text,
            webhook.channel.value,
            json.dumps(message_metadata),
        )

    # Publish to Kafka
    kafka_payload = {
        "ticket_id": str(uuid.uuid4()),
        "conversation_id": str(conversation_id),
        "customer_id": str(customer_id),
        "customer_identifier": webhook.customer_identifier,
        "channel": webhook.channel.value,
        "message_text": webhook.message_text,
        "subject": webhook.subject,
        "message_id": str(message_id),
    }
    await publish(settings.kafka_topic_incoming, kafka_payload, key=str(customer_id))

    logger.info(
        "Webhook received: channel=%s customer=%s conversation=%s",
        channel, customer_id, conversation_id,
    )

    return {"status": "accepted", "conversation_id": str(conversation_id)}


async def _upsert_customer(conn, identifier: str, identifier_type: str) -> str:
    """Upsert customer and customer_identifier, return customer UUID."""
    # Check if identifier exists
    row = await conn.fetchrow(
        "SELECT customer_id FROM customer_identifiers WHERE identifier = $1 AND identifier_type = $2",
        identifier, identifier_type,
    )
    if row:
        return row["customer_id"]

    # Create new customer
    customer_id = await conn.fetchval(
        "INSERT INTO customers (email, phone) VALUES ($1, $2) RETURNING id",
        identifier if identifier_type == "email" else None,
        identifier if identifier_type == "phone" else None,
    )

    # Link identifier
    await conn.execute(
        """
        INSERT INTO customer_identifiers (customer_id, identifier, identifier_type, channel)
        VALUES ($1, $2, $3, $3)
        ON CONFLICT (identifier, identifier_type) DO NOTHING
        """,
        customer_id, identifier, identifier_type,
    )
    return str(customer_id)


async def _get_or_create_conversation(conn, customer_id: str, channel: str, subject: str | None) -> str:
    """Get an open conversation or create a new one."""
    row = await conn.fetchrow(
        """
        SELECT id FROM conversations
        WHERE customer_id = $1 AND channel = $2 AND status = 'open'
        ORDER BY created_at DESC LIMIT 1
        """,
        customer_id, channel,
    )
    if row:
        return row["id"]

    conv_id = await conn.fetchval(
        "INSERT INTO conversations (customer_id, channel, subject) VALUES ($1, $2, $3) RETURNING id",
        customer_id, channel, subject,
    )
    return str(conv_id)
