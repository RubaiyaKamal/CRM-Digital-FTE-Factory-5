"""Integration tests for tickets API endpoints."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import uuid4

import src.api.routers.tickets as _tickets_mod
import src.api.main as _main_mod
import src.database.connection as _db_mod

from fastapi.testclient import TestClient


def _make_mock_pool_with_data():
    """Create mock pool that returns sample ticket data."""
    ticket_row = {
        "id": uuid4(),
        "customer_id": uuid4(),
        "channel": "web_form",
        "category": "how-to",
        "priority": "low",
        "status": "resolved",
        "sentiment_score": 0.7,
        "created_at": datetime.utcnow(),
        "raw_message": "How do I reset my password?",
    }

    conv_row = {
        "id": uuid4(),
        "customer_id": uuid4(),
        "channel": "web_form",
        "status": "resolved",
        "subject": "Password help",
        "created_at": datetime.utcnow(),
        "message_count": 2,
    }

    mock_conn = AsyncMock()

    # fetch returns appropriate data per query (detect by SQL keyword)
    async def smart_fetch(sql, *args):
        if "conversations" in sql.lower():
            return [conv_row]
        return [ticket_row]

    mock_conn.fetch = smart_fetch
    mock_conn.fetchrow = AsyncMock(return_value=ticket_row)
    mock_conn.fetchval = AsyncMock(return_value=str(uuid4()))
    mock_conn.execute = AsyncMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)

    mock_pool = MagicMock()
    mock_pool.acquire = MagicMock(return_value=mock_conn)
    return mock_pool, ticket_row, conv_row


@pytest.fixture
def client_with_data():
    pool, ticket_row, conv_row = _make_mock_pool_with_data()
    original_pool = _db_mod._pool
    _db_mod._pool = pool

    with patch.object(_main_mod, "create_pool", AsyncMock(return_value=pool)), \
         patch.object(_main_mod, "apply_schema", AsyncMock()), \
         patch.object(_main_mod, "get_producer", AsyncMock()), \
         patch.object(_main_mod, "stop_producer", AsyncMock()), \
         patch.object(_main_mod, "close_pool", AsyncMock()):
        yield TestClient(_main_mod.app), ticket_row, conv_row

    _db_mod._pool = original_pool


class TestTicketsAPI:
    def test_list_tickets(self, client_with_data):
        client, ticket_row, _ = client_with_data
        response = client.get("/api/v1/tickets")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_tickets_with_filter(self, client_with_data):
        client, _, _ = client_with_data
        response = client.get("/api/v1/tickets?status=resolved&channel=web_form")
        assert response.status_code == 200

    def test_get_ticket_by_id(self, client_with_data):
        client, ticket_row, _ = client_with_data
        ticket_id = str(ticket_row["id"])
        response = client.get(f"/api/v1/tickets/{ticket_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["channel"] == "web_form"

    def test_list_conversations(self, client_with_data):
        client, _, _ = client_with_data
        response = client.get("/api/v1/conversations")
        assert response.status_code == 200
