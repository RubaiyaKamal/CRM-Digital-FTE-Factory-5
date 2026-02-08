"""Unit tests for Pydantic models."""
import pytest
from datetime import datetime
from src.agent.models import (
    Channel, Priority, Category, IncomingWebhook, AgentTask, AgentResult
)


class TestChannel:
    def test_valid_channels(self):
        assert Channel.EMAIL == "email"
        assert Channel.WHATSAPP == "whatsapp"
        assert Channel.WEB_FORM == "web_form"


class TestIncomingWebhook:
    def test_create_webhook(self):
        w = IncomingWebhook(
            message_id="msg-1",
            customer_identifier="user@test.com",
            identifier_type="email",
            channel=Channel.EMAIL,
            message_text="Hello",
        )
        assert w.message_id == "msg-1"
        assert w.channel == Channel.EMAIL
        assert isinstance(w.received_at, datetime)

    def test_default_raw_payload(self):
        w = IncomingWebhook(
            message_id="x",
            customer_identifier="y",
            identifier_type="email",
            channel=Channel.WEB_FORM,
            message_text="test",
        )
        assert w.raw_payload == {}


class TestAgentTask:
    def test_create_task(self):
        task = AgentTask(
            ticket_id="t-1",
            conversation_id="c-1",
            customer_id="cu-1",
            customer_identifier="user@test.com",
            channel=Channel.EMAIL,
            message_text="Need help",
        )
        assert task.conversation_history == []


class TestAgentResult:
    def test_defaults(self):
        result = AgentResult(
            ticket_id="t-1",
            customer_id="cu-1",
            channel=Channel.EMAIL,
            response_text="Here's how to help",
            should_escalate=False,
        )
        assert result.category == Category.GENERAL
        assert result.priority == Priority.LOW
        assert result.sentiment_score == 0.5
        assert result.tool_calls == []
