"""Integration tests for webhook endpoints."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

# Pre-import all modules so patch targets are resolvable
import src.api.routers.webhooks as _webhooks_mod
import src.api.main as _main_mod
import src.database.connection as _db_mod


def _make_mock_pool():
    """Build a mock asyncpg pool."""
    mock_conn = AsyncMock()
    mock_conn.fetchval = AsyncMock(return_value="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
    mock_conn.fetchrow = AsyncMock(return_value=None)
    mock_conn.execute = AsyncMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)
    mock_pool = MagicMock()
    mock_pool.acquire = MagicMock(return_value=mock_conn)
    return mock_pool


@pytest.fixture
def client():
    """Create test client with all external dependencies mocked."""
    pool = _make_mock_pool()

    # Directly inject mock pool into connection module so get_db_pool returns it
    original_pool = _db_mod._pool
    _db_mod._pool = pool

    # Patch kafka publish and lifecycle functions
    with patch.object(_webhooks_mod, "publish", AsyncMock()), \
         patch.object(_main_mod, "create_pool", AsyncMock(return_value=pool)), \
         patch.object(_main_mod, "apply_schema", AsyncMock()), \
         patch.object(_main_mod, "get_producer", AsyncMock()), \
         patch.object(_main_mod, "stop_producer", AsyncMock()), \
         patch.object(_main_mod, "close_pool", AsyncMock()):
        yield TestClient(_main_mod.app)

    # Restore
    _db_mod._pool = original_pool


class TestWebFormWebhook:
    def test_valid_web_form_submission(self, client):
        response = client.post("/webhooks/web_form", json={
            "email": "user@test.com",
            "message": "How do I reset my password?",
            "subject": "Password help",
        })
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert data["status"] == "accepted"

    def test_invalid_channel(self, client):
        response = client.post("/webhooks/invalid_channel", json={})
        assert response.status_code == 404

    def test_invalid_json(self, client):
        response = client.post(
            "/webhooks/web_form",
            data="not json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 400


class TestEmailWebhook:
    def test_valid_gmail_webhook(self, client):
        response = client.post("/webhooks/email", json={
            "from": "customer@company.com",
            "subject": "Need help with billing",
            "body": "I have a question about my invoice",
        })
        assert response.status_code == 200

    def test_empty_body_field(self, client):
        response = client.post("/webhooks/email", json={
            "from": "test@test.com",
            "subject": "Test",
            "body": "",
        })
        # Should still accept (empty message is valid, agent handles it)
        assert response.status_code == 200


class TestWhatsAppWebhook:
    def test_valid_whatsapp_webhook(self, client):
        response = client.post("/webhooks/whatsapp", json={
            "From": "whatsapp:+1234567890",
            "Body": "Hello I need help",
            "MessageSid": "SM123456",
        })
        assert response.status_code == 200


class TestHealthEndpoint:
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
