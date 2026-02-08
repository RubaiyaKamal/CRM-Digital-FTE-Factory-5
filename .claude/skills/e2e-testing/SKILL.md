# E2E Testing Skill

## Skill Definition

**Name:** e2e-testing
**Version:** 1.0.0
**Type:** Testing
**Complexity:** Intermediate

## Description

End-to-end testing of multi-channel customer support workflows from message receipt through agent processing to response delivery.

## Test Structure

```python
# tests/test_e2e.py
import pytest
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"

class TestWebFormChannel:
    """Test web form end-to-end flow."""

    @pytest.mark.asyncio
    async def test_form_submission_to_response(self):
        """Complete flow: form submit → ticket created → agent responds."""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Submit form
            response = await client.post("/support/submit", json={
                "name": "Test User",
                "email": "test@example.com",
                "subject": "Need help with API",
                "category": "technical",
                "message": "How do I authenticate?"
            })

            assert response.status_code == 200
            ticket_id = response.json()["ticket_id"]

            # Wait for agent processing (poll ticket status)
            import asyncio
            for _ in range(10):  # 10 second timeout
                status_response = await client.get(f"/support/ticket/{ticket_id}")
                if status_response.json()["status"] == "responded":
                    break
                await asyncio.sleep(1)

            # Verify response exists
            ticket = status_response.json()
            assert len(ticket["messages"]) >= 2  # Customer message + agent response
            assert ticket["status"] == "responded"


class TestCrossChannelContinuity:
    """Test that conversations persist across channels."""

    @pytest.mark.asyncio
    async def test_customer_switches_channels(self):
        """Customer starts on web, continues on email."""
        async with AsyncClient(base_url=BASE_URL) as client:
            # Web form submission
            web_response = await client.post("/support/submit", json={
                "name": "John Doe",
                "email": "john@example.com",
                "subject": "Question about billing",
                "category": "billing",
                "message": "What is my current plan?"
            })

            ticket_id_1 = web_response.json()["ticket_id"]

            # Simulate email follow-up (same customer)
            # In real scenario, Gmail webhook would receive this
            email_message = {
                "channel": "email",
                "customer_email": "john@example.com",
                "subject": "Re: Question about billing",
                "content": "Also, can I upgrade mid-month?"
            }

            # Process email
            await client.post("/webhooks/gmail", json={
                "message": {"data": "mock_gmail_notification"}
            })

            # Verify customer history includes both interactions
            customer_response = await client.get(
                "/customers/lookup",
                params={"email": "john@example.com"}
            )

            customer = customer_response.json()
            conversations = customer["conversations"]

            # Should have messages from both web and email
            channels_used = set()
            for conv in conversations:
                for msg in conv["messages"]:
                    channels_used.add(msg["channel"])

            assert "web_form" in channels_used
            assert "email" in channels_used
```

## Mock Channel APIs

```python
# tests/mocks/twilio_mock.py
class MockTwilioClient:
    """Mock Twilio for testing WhatsApp integration."""

    def __init__(self):
        self.messages_sent = []

    def messages_create(self, body, from_, to):
        message = {
            "sid": f"SM{len(self.messages_sent)}",
            "body": body,
            "from_": from_,
            "to": to,
            "status": "sent"
        }
        self.messages_sent.append(message)
        return type('obj', (object,), message)

    def verify_message_sent(self, to: str, contains: str):
        """Helper to verify message was sent."""
        for msg in self.messages_sent:
            if msg["to"] == to and contains in msg["body"]:
                return True
        return False
```

## Related Skills

- **agent-specialization** - Agent being tested
- **web-form-builder** - Form tests
- **gmail-integration** - Email tests
- **whatsapp-integration** - WhatsApp tests
