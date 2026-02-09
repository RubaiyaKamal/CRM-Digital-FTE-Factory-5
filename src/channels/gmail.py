"""
Gmail channel adapter.
Parses email webhook payloads and sends replies via Gmail API.
"""
from __future__ import annotations

import base64
import json
import logging
import uuid
from typing import Any, Dict

from src.agent.models import Channel, IncomingWebhook
from src.channels.base import ChannelAdapter
from src.config import settings

logger = logging.getLogger(__name__)


class GmailAdapter(ChannelAdapter):
    """Handles Email channel via Gmail webhook (mock send)."""

    channel_name = "email"

    def normalize(self, raw_payload: Dict[str, Any]) -> IncomingWebhook:
        """
        Parse email webhook payload.
        Expected from poller: {
            "email": "sender@example.com",
            "subject": "...",
            "message": "...",
            "session_id": "threadId",
            "metadata": {"gmail_message_id": "...", "gmail_thread_id": "..."}
        }
        Also supports legacy Gmail push notification format for backwards compatibility.
        """
        # Support poller webhook format (preferred)
        if "email" in raw_payload:
            sender = raw_payload["email"]
            subject = raw_payload.get("subject", "")
            body = raw_payload.get("message", "")
            metadata = raw_payload.get("metadata", {})
            message_id = metadata.get("gmail_message_id", str(uuid.uuid4()))
        # Support direct test payloads
        elif "from" in raw_payload:
            sender = raw_payload["from"]
            subject = raw_payload.get("subject", "")
            body = raw_payload.get("body", raw_payload.get("message", ""))
            message_id = raw_payload.get("message_id", str(uuid.uuid4()))
            metadata = raw_payload.get("metadata", {})
        # Gmail push notification format (legacy)
        else:
            data_b64 = raw_payload.get("message", {}).get("data", "")
            decoded = json.loads(base64.urlsafe_b64decode(data_b64 + "==").decode())
            sender = decoded.get("emailAddress", "unknown@example.com")
            subject = decoded.get("subject", "")
            body = decoded.get("snippet", "")
            message_id = raw_payload.get("message", {}).get("messageId", str(uuid.uuid4()))
            metadata = {}

        return IncomingWebhook(
            message_id=message_id,
            customer_identifier=sender,
            identifier_type="email",
            channel=Channel.EMAIL,
            subject=subject,
            message_text=body,
            raw_payload=raw_payload,
            metadata=metadata,
        )

    async def send(self, customer_identifier: str, message: str, **kwargs: Any) -> bool:
        """Send email reply via Gmail API with proper threading."""
        # Check if mock mode
        if settings.gmail_mock:
            subject = kwargs.get("subject", "Re: CloudFlow Support")
            logger.info(
                "[GMAIL MOCK] TO=%s SUBJECT=%s BODY_LEN=%d",
                customer_identifier,
                subject,
                len(message),
            )
            return True

        # Real Gmail send
        from src.channels.gmail_client import send_email

        thread_id = kwargs.get("gmail_thread_id")
        subject = kwargs.get("subject", "Re: Support Request")

        success = await send_email(
            to=customer_identifier, subject=subject, body=message, thread_id=thread_id
        )

        if success:
            logger.info(f"Sent email to {customer_identifier} via Gmail API")
        else:
            logger.error(f"Failed to send email to {customer_identifier}")

        return success
