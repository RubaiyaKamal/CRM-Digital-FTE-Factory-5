"""
WhatsApp Client Module via Twilio API

Provides functions for sending WhatsApp messages through Twilio's WhatsApp Business API.

Key features:
- Send text messages to WhatsApp numbers
- Automatic phone number formatting (E.164)
- Message length validation (1600 character limit)
- Error handling with detailed logging
"""
from __future__ import annotations

import logging
import re
from typing import Optional

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from src.config import settings

logger = logging.getLogger(__name__)


def _format_phone_number(phone: str) -> str:
    """
    Format phone number to E.164 format (+[country_code][number]).

    Args:
        phone: Phone number (with or without + or whatsapp: prefix)

    Returns:
        Formatted phone number with whatsapp: prefix

    Examples:
        "+14155551234" -> "whatsapp:+14155551234"
        "whatsapp:+14155551234" -> "whatsapp:+14155551234"
        "14155551234" -> "whatsapp:+14155551234"
    """
    # Remove existing whatsapp: prefix
    phone = phone.replace("whatsapp:", "").strip()

    # Remove any non-digit characters except +
    phone = re.sub(r"[^\d+]", "", phone)

    # Add + if not present
    if not phone.startswith("+"):
        phone = "+" + phone

    # Add whatsapp: prefix
    return f"whatsapp:{phone}"


def _get_twilio_client() -> Client:
    """
    Get authenticated Twilio client.

    Returns:
        Twilio Client instance

    Raises:
        RuntimeError: If Twilio credentials are not configured
    """
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        raise RuntimeError(
            "Twilio credentials not configured. Set TWILIO_ACCOUNT_SID and "
            "TWILIO_AUTH_TOKEN in environment variables."
        )

    return Client(settings.twilio_account_sid, settings.twilio_auth_token)


async def send_whatsapp_message(
    to: str,
    message: str,
    from_number: Optional[str] = None,
) -> bool:
    """
    Send a WhatsApp message via Twilio API.

    Args:
        to: Recipient phone number (will be formatted to E.164)
        message: Message text (max 1600 characters)
        from_number: Sender WhatsApp number (defaults to WHATSAPP_PHONE_NUMBER)

    Returns:
        True if sent successfully, False otherwise

    Note:
        Twilio WhatsApp has a 1600 character limit per message.
        Messages longer than this will be truncated with a warning.
    """
    try:
        # Validate message length
        max_length = 1600
        if len(message) > max_length:
            logger.warning(
                f"Message length {len(message)} exceeds WhatsApp limit {max_length}, "
                f"truncating..."
            )
            message = message[:max_length - 50] + "\n\n[Message truncated due to length]"

        # Format phone numbers
        to_formatted = _format_phone_number(to)
        from_formatted = _format_phone_number(
            from_number or settings.whatsapp_phone_number
        )

        # Get Twilio client
        client = _get_twilio_client()

        # Send message
        twilio_message = client.messages.create(
            body=message,
            from_=from_formatted,
            to=to_formatted,
        )

        logger.info(
            f"WhatsApp message sent to {to_formatted}, "
            f"SID={twilio_message.sid}, status={twilio_message.status}"
        )

        return True

    except TwilioRestException as e:
        logger.error(
            f"Twilio API error sending to {to}: [{e.code}] {e.msg}",
            exc_info=True
        )

        # Common error codes
        if e.code == 21211:
            logger.error("Invalid 'To' phone number. Ensure it's E.164 format.")
        elif e.code == 21408:
            logger.error(
                "Permission denied. Ensure the recipient has opted-in to receive "
                "messages from your Twilio WhatsApp number."
            )
        elif e.code == 21610:
            logger.error(
                "WhatsApp message undeliverable. The recipient may have blocked "
                "your number or their WhatsApp is not active."
            )
        elif e.code == 63007:
            logger.error(
                "Message body exceeds maximum length. Already truncated but still "
                "too long - check for encoding issues."
            )

        return False

    except Exception as e:
        logger.error(f"Error sending WhatsApp message to {to}: {e}", exc_info=True)
        return False


async def send_whatsapp_template(
    to: str,
    template_sid: str,
    content_variables: dict,
    from_number: Optional[str] = None,
) -> bool:
    """
    Send a WhatsApp template message via Twilio API.

    Template messages are required for the first message to a user in a 24-hour
    window. After that, freeform messages can be sent.

    Args:
        to: Recipient phone number
        template_sid: Twilio Content Template SID (starts with HX...)
        content_variables: Variables to fill in the template
        from_number: Sender WhatsApp number (defaults to WHATSAPP_PHONE_NUMBER)

    Returns:
        True if sent successfully, False otherwise

    Example:
        await send_whatsapp_template(
            to="+14155551234",
            template_sid="HXa1b2c3d4e5f6g7h8i9j0k1l2m3n4o5",
            content_variables={"1": "John", "2": "Support Team"}
        )
    """
    try:
        # Format phone numbers
        to_formatted = _format_phone_number(to)
        from_formatted = _format_phone_number(
            from_number or settings.whatsapp_phone_number
        )

        # Get Twilio client
        client = _get_twilio_client()

        # Send template message
        twilio_message = client.messages.create(
            from_=from_formatted,
            to=to_formatted,
            content_sid=template_sid,
            content_variables=content_variables,
        )

        logger.info(
            f"WhatsApp template sent to {to_formatted}, "
            f"SID={twilio_message.sid}, template={template_sid}"
        )

        return True

    except TwilioRestException as e:
        logger.error(
            f"Twilio template error for {to}: [{e.code}] {e.msg}",
            exc_info=True
        )
        return False

    except Exception as e:
        logger.error(f"Error sending WhatsApp template to {to}: {e}", exc_info=True)
        return False


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        True if valid E.164 format, False otherwise

    Example:
        validate_phone_number("+14155551234")  # True
        validate_phone_number("4155551234")     # False (missing +)
        validate_phone_number("+1234")          # False (too short)
    """
    # Remove whatsapp: prefix if present
    phone = phone.replace("whatsapp:", "").strip()

    # E.164 format: +[1-15 digits]
    pattern = r"^\+[1-9]\d{1,14}$"

    return bool(re.match(pattern, phone))
