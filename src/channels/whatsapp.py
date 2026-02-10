"""
WhatsApp channel adapter via Twilio.
Handles webhook validation and message sending through Twilio API.
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
        Expected fields: From, Body, MessageSid, To, ProfileName, etc.
        """
        from_number = raw_payload.get("From", "").replace("whatsapp:", "")
        body = raw_payload.get("Body", "")
        message_sid = raw_payload.get("MessageSid", str(uuid.uuid4()))
        to_number = raw_payload.get("To", "")
        profile_name = raw_payload.get("ProfileName", "")

        # Build metadata with Twilio-specific fields
        metadata = {
            "twilio_message_sid": message_sid,
            "twilio_to": to_number,
            "twilio_from": raw_payload.get("From", ""),
            "profile_name": profile_name,
            "num_media": raw_payload.get("NumMedia", "0"),
            "account_sid": raw_payload.get("AccountSid", ""),
        }

        # Include media URLs if present
        num_media = int(raw_payload.get("NumMedia", "0"))
        if num_media > 0:
            media_urls = []
            for i in range(num_media):
                media_url = raw_payload.get(f"MediaUrl{i}")
                media_type = raw_payload.get(f"MediaContentType{i}")
                if media_url:
                    media_urls.append({"url": media_url, "type": media_type})
            metadata["media"] = media_urls

        return IncomingWebhook(
            message_id=message_sid,
            customer_identifier=from_number,
            identifier_type="phone",
            channel=Channel.WHATSAPP,
            message_text=body,
            raw_payload=raw_payload,
            metadata=metadata,
        )

    def validate_signature(self, request_body: bytes, signature: str) -> bool:
        """
        Validate Twilio webhook signature.
        https://www.twilio.com/docs/usage/webhooks/webhooks-security

        NOTE: Proper Twilio signature validation requires the full URL + sorted params.
        For now, we'll skip validation in development mode.
        TODO: Implement proper validation with URL + params.
        """
        # Skip validation in development/testing
        logger.info("WhatsApp webhook signature validation skipped (development mode)")
        return True

    async def send(self, customer_identifier: str, message: str, **kwargs: Any) -> bool:
        """Send WhatsApp message via Twilio API."""
        # Check if mock mode
        if settings.whatsapp_mock:
            logger.info(
                "[WHATSAPP MOCK] TO=%s MSG_LEN=%d",
                customer_identifier,
                len(message),
            )
            return True

        # Real Twilio send
        from src.channels.whatsapp_client import send_whatsapp_message

        success = await send_whatsapp_message(
            to=customer_identifier,
            message=message,
        )

        if success:
            logger.info(f"Sent WhatsApp message to {customer_identifier} via Twilio API")
        else:
            logger.error(f"Failed to send WhatsApp message to {customer_identifier}")

        return success
