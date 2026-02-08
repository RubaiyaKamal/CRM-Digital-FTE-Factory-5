"""
Gmail channel adapter (mock implementation for dev/hackathon).
Parses Gmail Push Notification webhook payloads.
"""
from __future__ import annotations

import base64
import json
import logging
import uuid
from typing import Any, Dict

from src.agent.models import Channel, IncomingWebhook
from src.channels.base import ChannelAdapter

logger = logging.getLogger(__name__)


class GmailAdapter(ChannelAdapter):
    """Handles Email channel via Gmail webhook (mock send)."""

    channel_name = "email"

    def normalize(self, raw_payload: Dict[str, Any]) -> IncomingWebhook:
        """
        Parse Gmail Push Notification payload.
        Expected shape: {"message": {"data": "<base64>", "messageId": "..."}}
        Decoded data contains: {"emailAddress": ..., "historyId": ...}
        or direct test payload: {"from": ..., "subject": ..., "body": ...}
        """
        # Support both direct test payloads and Gmail push format
        if "from" in raw_payload:
            sender = raw_payload["from"]
            subject = raw_payload.get("subject", "")
            body = raw_payload.get("body", raw_payload.get("message", ""))
            message_id = raw_payload.get("message_id", str(uuid.uuid4()))
        else:
            # Gmail push notification format
            data_b64 = raw_payload.get("message", {}).get("data", "")
            decoded = json.loads(base64.urlsafe_b64decode(data_b64 + "==").decode())
            sender = decoded.get("emailAddress", "unknown@example.com")
            subject = decoded.get("subject", "")
            body = decoded.get("snippet", "")
            message_id = raw_payload.get("message", {}).get("messageId", str(uuid.uuid4()))

        return IncomingWebhook(
            message_id=message_id,
            customer_identifier=sender,
            identifier_type="email",
            channel=Channel.EMAIL,
            subject=subject,
            message_text=body,
            raw_payload=raw_payload,
        )

    async def send(self, customer_identifier: str, message: str, **kwargs: Any) -> bool:
        """Mock send — logs the email that would be sent."""
        subject = kwargs.get("subject", "Re: CloudFlow Support")
        logger.info(
            "[GMAIL MOCK] TO=%s SUBJECT=%s BODY_LEN=%d",
            customer_identifier, subject, len(message)
        )
        return True
