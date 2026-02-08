"""
Abstract base class for channel adapters.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from src.agent.models import IncomingWebhook


class ChannelAdapter(ABC):
    """Contract for all channel adapters."""

    channel_name: str

    @abstractmethod
    def normalize(self, raw_payload: Dict[str, Any]) -> IncomingWebhook:
        """Parse raw webhook payload into a normalised IncomingWebhook."""
        ...

    @abstractmethod
    async def send(self, customer_identifier: str, message: str, **kwargs: Any) -> bool:
        """Send a response to the customer. Returns True on success."""
        ...

    def validate_signature(self, request_body: bytes, signature: str) -> bool:
        """Validate webhook signature. Override for channels that support it."""
        return True
