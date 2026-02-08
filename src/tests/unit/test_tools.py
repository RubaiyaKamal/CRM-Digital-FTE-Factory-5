"""Unit tests for agent tools (escalation detection)."""
import pytest
from src.agent.tools import detect_escalation_need


class TestDetectEscalationNeed:
    def test_security_keyword_triggers_immediate(self):
        escalate, trigger, reason, sla = detect_escalation_need(
            "We've been hacked and there's unauthorized access", "technical", 0.5
        )
        assert escalate is True
        assert trigger == "keywords"
        assert sla == 0.25

    def test_legal_keyword_triggers(self):
        escalate, trigger, reason, sla = detect_escalation_need(
            "I'm going to sue your company", "general", 0.5
        )
        assert escalate is True
        assert trigger == "keywords"

    def test_financial_keyword_triggers(self):
        escalate, trigger, reason, sla = detect_escalation_need(
            "I need a refund for the double charge", "billing", 0.4
        )
        assert escalate is True

    def test_billing_category_triggers(self):
        escalate, trigger, reason, sla = detect_escalation_need(
            "What's on my invoice?", "billing", 0.6
        )
        assert escalate is True
        assert trigger == "category"

    def test_negative_sentiment_triggers(self):
        escalate, trigger, reason, sla = detect_escalation_need(
            "This is really bad", "technical", 0.2
        )
        assert escalate is True
        assert trigger == "sentiment"

    def test_explicit_human_request(self):
        escalate, trigger, reason, sla = detect_escalation_need(
            "I want to speak to a human agent please", "general", 0.5
        )
        assert escalate is True
        assert trigger == "explicit_request"

    def test_normal_message_no_escalation(self):
        escalate, trigger, reason, sla = detect_escalation_need(
            "How do I create a new project?", "how-to", 0.7
        )
        assert escalate is False
        assert trigger == ""

    def test_compliance_keywords(self):
        escalate, trigger, reason, sla = detect_escalation_need(
            "I need my data deleted under GDPR right to be forgotten", "compliance", 0.5
        )
        assert escalate is True


class TestChannelAdapterNormalize:
    def test_gmail_normalize_direct(self):
        from src.channels.gmail import GmailAdapter
        adapter = GmailAdapter()
        webhook = adapter.normalize({
            "from": "user@example.com",
            "subject": "Test",
            "body": "Hello",
            "message_id": "msg-123",
        })
        assert webhook.customer_identifier == "user@example.com"
        assert webhook.identifier_type == "email"
        assert webhook.message_text == "Hello"

    def test_whatsapp_normalize(self):
        from src.channels.whatsapp import WhatsAppAdapter
        adapter = WhatsAppAdapter()
        webhook = adapter.normalize({
            "From": "whatsapp:+1234567890",
            "Body": "Hey there",
            "MessageSid": "SM123",
        })
        assert webhook.customer_identifier == "+1234567890"
        assert webhook.identifier_type == "phone"
        assert webhook.message_text == "Hey there"

    def test_web_form_normalize(self):
        from src.channels.web_form import WebFormAdapter
        adapter = WebFormAdapter()
        webhook = adapter.normalize({
            "email": "user@test.com",
            "message": "I need help",
            "subject": "Question",
            "session_id": "sess-abc",
        })
        assert webhook.customer_identifier == "user@test.com"
        assert webhook.message_text == "I need help"
        assert webhook.message_id == "sess-abc"
