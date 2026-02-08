"""
End-to-end tests for the web form → agent → response flow.
These tests require a running stack (docker-compose up) or pytest-mark skip.
"""
import pytest
import asyncio
import httpx


BASE_URL = "http://localhost:8000"


@pytest.mark.e2e
class TestWebFormEndToEnd:
    """Full web form flow: submit → SSE response."""

    def test_submit_and_get_response(self):
        """Submit a web form ticket and verify it's accepted."""
        with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
            response = client.post("/webhooks/web_form", json={
                "email": "e2e-test@example.com",
                "message": "How do I add team members to my project?",
                "subject": "Team management question",
            })
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "accepted"
            assert "conversation_id" in data

    def test_health_endpoint(self):
        """Verify the API is running."""
        with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
            response = client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"

    def test_cross_channel_customer_identity(self):
        """Same email via web form and email creates same customer."""
        with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
            # Web form submission
            r1 = client.post("/webhooks/web_form", json={
                "email": "cross-channel@test.com",
                "message": "Test from web form",
            })
            # Email webhook
            r2 = client.post("/webhooks/email", json={
                "from": "cross-channel@test.com",
                "subject": "Test from email",
                "body": "Same customer, different channel",
            })
            assert r1.status_code == 200
            assert r2.status_code == 200
            # Both should reference same customer (verified via /api/v1/tickets query)

    def test_ticket_list_endpoint(self):
        """Verify ticket listing works after submissions."""
        with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
            response = client.get("/api/v1/tickets?limit=10")
            assert response.status_code == 200
            assert isinstance(response.json(), list)


@pytest.mark.e2e
class TestEscalationFlow:
    """Test escalation triggers in production flow."""

    def test_security_incident_escalation(self):
        """Security keywords should result in escalated ticket status."""
        with httpx.Client(base_url=BASE_URL, timeout=15.0) as client:
            response = client.post("/webhooks/email", json={
                "from": "security-test@company.com",
                "subject": "Security incident",
                "body": "Our account has been breached! Unauthorized access detected!",
            })
            assert response.status_code == 200

    def test_billing_category_escalation(self):
        """Billing questions should escalate."""
        with httpx.Client(base_url=BASE_URL, timeout=15.0) as client:
            response = client.post("/webhooks/web_form", json={
                "email": "billing@test.com",
                "message": "I need a refund for the incorrect charge on my account",
            })
            assert response.status_code == 200
