"""
WhatsApp channel adapter via Twilio (mock send, real webhook validation).
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import uuid
from typing import Any, Dict
from urllib.parse import urlencode

from src.agent.models import Channel, IncomingWebhook
from src.channels.base import ChannelAdapter
from src.config import settings

logger = logging.getLogger(__name__)


class WhatsAppAdapter(ChannelAdapter):
    """Handles WhatsApp channel via Twilio webhook."""

    channel_name = "whatsapp"

    def normalize(self, raw_payload: Dict[str, Any]) -> IncomingWebhook:
        """
        Parse Twilio WhatsApp webhook payload.
        Expected fields: From, Body, MessageSid, To
        """
        from_number = raw_payload.get("From", "").replace("whatsapp:", "")
        body = raw_payload.get("Body", "")
        message_sid = raw_payload.get("MessageSid", str(uuid.uuid4()))

        return IncomingWebhook(
            message_id=message_sid,
            customer_identifier=from_number,
            identifier_type="phone",
            channel=Channel.WHATSAPP,
            message_text=body,
            raw_payload=raw_payload,
        )

    def validate_signature(self, request_body: bytes, signature: str) -> bool:
        """
        Validate Twilio webhook signature.
        https://www.twilio.com/docs/usage/webhooks/webhooks-security
        """
        if not settings.twilio_auth_token:
            # In mock/dev mode, skip validation
            return True
        expected = hmac.new(
            settings.twilio_auth_token.encode(),
            request_body,
            hashlib.sha1,
        ).hexdigest()
        return hmac.compare_digest(expected, signature or "")

    async def send(self, customer_identifier: str, message: str, **kwargs: Any) -> bool:
        """Mock send — logs the WhatsApp message that would be sent."""
        logger.info(
            "[WHATSAPP MOCK] TO=%s MSG_LEN=%d",
            customer_identifier, len(message)
        )
        return True
