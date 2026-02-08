"""
Web Form channel adapter.
Real: receives POST from React form, streams response via SSE.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Any, AsyncGenerator, Dict

from src.agent.models import Channel, IncomingWebhook
from src.channels.base import ChannelAdapter

logger = logging.getLogger(__name__)

# In-memory SSE queue per session_id (keyed by customer_identifier / session token)
_sse_queues: Dict[str, asyncio.Queue] = {}


class WebFormAdapter(ChannelAdapter):
    """Handles Web Form channel with SSE for real-time responses."""

    channel_name = "web_form"

    def normalize(self, raw_payload: Dict[str, Any]) -> IncomingWebhook:
        """
        Parse web form POST payload.
        Expected fields: email, message, subject (optional), session_id (optional)
        """
        email = raw_payload.get("email", "anonymous@web.form")
        message = raw_payload.get("message", "")
        subject = raw_payload.get("subject")
        session_id = raw_payload.get("session_id", str(uuid.uuid4()))

        return IncomingWebhook(
            message_id=session_id,
            customer_identifier=email,
            identifier_type="email",
            channel=Channel.WEB_FORM,
            subject=subject,
            message_text=message,
            raw_payload=raw_payload,
        )

    async def send(self, customer_identifier: str, message: str, **kwargs: Any) -> bool:
        """Push response to SSE queue for the customer session."""
        session_id = kwargs.get("session_id", customer_identifier)
        queue = _sse_queues.get(session_id)
        if queue:
            await queue.put({"type": "response", "content": message})
            logger.info("[WEB_FORM SSE] Pushed response to session %s", session_id)
            return True
        logger.warning("[WEB_FORM SSE] No queue for session %s", session_id)
        return False

    def register_session(self, session_id: str) -> asyncio.Queue:
        """Register a new SSE session and return its queue."""
        queue: asyncio.Queue = asyncio.Queue(maxsize=20)
        _sse_queues[session_id] = queue
        return queue

    def close_session(self, session_id: str) -> None:
        """Clean up SSE queue for a session."""
        _sse_queues.pop(session_id, None)

    async def sse_stream(self, session_id: str) -> AsyncGenerator[str, None]:
        """Yield SSE events for a session until connection closes."""
        queue = _sse_queues.get(session_id)
        if queue is None:
            queue = self.register_session(session_id)

        yield "data: {\"type\": \"connected\"}\n\n"

        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    import json
                    yield f"data: {json.dumps(event)}\n\n"
                    if event.get("type") == "done":
                        break
                except asyncio.TimeoutError:
                    # Heartbeat to keep connection alive
                    yield "data: {\"type\": \"heartbeat\"}\n\n"
        finally:
            self.close_session(session_id)
