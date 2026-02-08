"""Unit tests for channel adapters."""
import pytest
from unittest.mock import AsyncMock
from src.channels.gmail import GmailAdapter
from src.channels.whatsapp import WhatsAppAdapter
from src.channels.web_form import WebFormAdapter
from src.agent.models import Channel


class TestGmailAdapter:
    def test_normalize_direct_format(self):
        adapter = GmailAdapter()
        hook = adapter.normalize({
            "from": "user@test.com",
            "subject": "Help",
            "body": "I need help",
        })
        assert hook.channel == Channel.EMAIL
        assert hook.identifier_type == "email"
        assert hook.customer_identifier == "user@test.com"
        assert hook.message_text == "I need help"

    @pytest.mark.asyncio
    async def test_send_mock(self, capsys):
        adapter = GmailAdapter()
        result = await adapter.send("test@test.com", "Hello")
        assert result is True

    def test_validate_signature_always_true_without_token(self):
        adapter = GmailAdapter()
        assert adapter.validate_signature(b"body", "sig") is True


class TestWhatsAppAdapter:
    def test_normalize_strips_whatsapp_prefix(self):
        adapter = WhatsAppAdapter()
        hook = adapter.normalize({
            "From": "whatsapp:+1234567890",
            "Body": "Hey",
            "MessageSid": "SM001",
        })
        assert hook.customer_identifier == "+1234567890"
        assert hook.channel == Channel.WHATSAPP
        assert hook.identifier_type == "phone"

    def test_validate_signature_no_token(self):
        adapter = WhatsAppAdapter()
        # Without auth token configured, should pass
        assert adapter.validate_signature(b"body", "any") is True

    @pytest.mark.asyncio
    async def test_send_mock(self):
        adapter = WhatsAppAdapter()
        result = await adapter.send("+1234567890", "Test message")
        assert result is True


class TestWebFormAdapter:
    def test_normalize_full_payload(self):
        adapter = WebFormAdapter()
        hook = adapter.normalize({
            "email": "user@form.com",
            "message": "Question about billing",
            "subject": "Billing",
            "session_id": "sess-001",
        })
        assert hook.customer_identifier == "user@form.com"
        assert hook.channel == Channel.WEB_FORM
        assert hook.message_id == "sess-001"

    def test_normalize_minimal_payload(self):
        adapter = WebFormAdapter()
        hook = adapter.normalize({
            "email": "anon@form.com",
            "message": "help",
        })
        assert hook.customer_identifier == "anon@form.com"
        assert hook.message_id is not None  # Should generate session_id

    def test_register_and_close_session(self):
        adapter = WebFormAdapter()
        queue = adapter.register_session("test-session")
        assert queue is not None
        adapter.close_session("test-session")
        # Queue should be removed

    @pytest.mark.asyncio
    async def test_send_to_registered_session(self):
        adapter = WebFormAdapter()
        queue = adapter.register_session("test-send-session")
        result = await adapter.send("test-send-session", "Response text", session_id="test-send-session")
        assert result is True
        event = queue.get_nowait()
        assert event["type"] == "response"
        assert event["content"] == "Response text"

    @pytest.mark.asyncio
    async def test_send_to_missing_session(self):
        adapter = WebFormAdapter()
        result = await adapter.send("nonexistent-session", "msg", session_id="nonexistent-session")
        assert result is False
