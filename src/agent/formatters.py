"""
Channel-specific response formatting (ported from prototype/channel_formatter.py).
"""
from __future__ import annotations

import re
from typing import List

from src.agent.models import Channel


LENGTH_LIMITS = {
    Channel.EMAIL: 2000,
    Channel.WHATSAPP: 1600,
    Channel.WEB_FORM: 1200,
}
WHATSAPP_PREFERRED = 300


def format_response(response: str, channel: Channel, customer_name: str | None = None) -> str:
    """Format a response string for the target channel."""
    if channel == Channel.EMAIL:
        return _format_email(response, customer_name)
    elif channel == Channel.WHATSAPP:
        return _format_whatsapp(response, customer_name)
    elif channel == Channel.WEB_FORM:
        return _format_web_form(response, customer_name)
    return response


def _extract_first_name(identifier: str | None) -> str:
    if not identifier:
        return "there"
    if "@" in identifier:
        username = identifier.split("@")[0]
        return username.split(".")[0].capitalize()
    if " " in identifier:
        return identifier.split()[0].capitalize()
    return identifier.capitalize()


def _simplify_for_whatsapp(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\*\s+", "• ", text, flags=re.MULTILINE)
    text = re.sub(r"^\-\s+", "• ", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _break_into_messages(text: str, max_length: int) -> List[str]:
    messages: List[str] = []
    current = ""
    for para in text.split("\n\n"):
        if len(current) + len(para) + 2 > max_length and current:
            messages.append(current.strip())
            current = para
        else:
            current = current + "\n\n" + para if current else para
    if current:
        messages.append(current.strip())
    return messages


def _format_email(response: str, customer_name: str | None) -> str:
    first_name = _extract_first_name(customer_name)
    parts = [
        f"Hi {first_name},\n",
        response.strip(),
        "\n\nLet me know if you have any other questions - I'm here to help!",
        "\nBest regards,",
        "CloudFlow Support Team",
    ]
    formatted = "\n".join(parts)
    limit = LENGTH_LIMITS[Channel.EMAIL]
    if len(formatted) > limit:
        formatted = formatted[: limit - 50] + "...\n\n[continued in next message]"
    return formatted


def _format_whatsapp(response: str, customer_name: str | None) -> str:
    first_name = _extract_first_name(customer_name)
    simplified = _simplify_for_whatsapp(response)
    if len(simplified) < 250:
        # No emoji in source; wave hand represented by unicode escape
        wave = "\U0001f44b"
        formatted = f"Hey {first_name}! {wave}\n\n{simplified}" if first_name != "there" else f"Hey! {wave}\n\n{simplified}"
    else:
        formatted = simplified
    if len(formatted) > WHATSAPP_PREFERRED:
        messages = _break_into_messages(formatted, WHATSAPP_PREFERRED)
        formatted = "\n\n---\n\n".join(messages)
    limit = LENGTH_LIMITS[Channel.WHATSAPP]
    if len(formatted) > limit:
        formatted = formatted[: limit - 50] + "..."
    return formatted


def _format_web_form(response: str, customer_name: str | None) -> str:
    first_name = _extract_first_name(customer_name)
    parts = [
        f"Hi {first_name},\n",
        response.strip(),
        "\n\nLet me know if you need more help!",
        "\n- CloudFlow Support",
    ]
    formatted = "\n".join(parts)
    limit = LENGTH_LIMITS[Channel.WEB_FORM]
    if len(formatted) > limit:
        formatted = formatted[: limit - 50] + "..."
    return formatted
