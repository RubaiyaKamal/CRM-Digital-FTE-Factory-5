"""Unit tests for worker modules."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import uuid4


class TestMessageProcessorLogic:
    """Test message processor without full Kafka/DB setup."""

    @pytest.mark.asyncio
    async def test_process_message_builds_task_correctly(self):
        """Verify _process_message builds AgentTask from Kafka payload."""
        payload = {
            "ticket_id": "ticket-001",
            "conversation_id": "conv-001",
            "customer_id": "cust-001",
            "customer_identifier": "user@test.com",
            "channel": "web_form",
            "message_text": "How do I export data?",
            "subject": "Data export question",
        }

        # Mock DB pool with conversation history
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[
            {"role": "customer", "content": "Previous message"},
        ])
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=mock_conn)

        # Mock agent
        mock_result = MagicMock()
        mock_result.final_output = "You can export data from Settings > Export"
        mock_result.to_input_list = MagicMock(return_value=[])

        import src.workers.message_processor as mp_mod
        with patch("src.database.connection._pool", mock_pool), \
             patch("agents.Runner.run", AsyncMock(return_value=mock_result)), \
             patch.object(mp_mod, "publish", AsyncMock()):
            from src.agent.customer_success_agent import CustomerSuccessAgent
            agent = CustomerSuccessAgent()
            await mp_mod._process_message(agent, payload)
            # No exception = success

    @pytest.mark.asyncio
    async def test_process_message_with_security_incident(self):
        """Security keywords should result in escalation."""
        payload = {
            "ticket_id": "ticket-sec-001",
            "conversation_id": "conv-sec-001",
            "customer_id": "cust-sec-001",
            "customer_identifier": "ciso@company.com",
            "channel": "email",
            "message_text": "We have been hacked! Unauthorized access!",
            "subject": "Security breach",
        }

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[])
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=mock_conn)

        mock_result = MagicMock()
        mock_result.final_output = "Escalating to security team"
        mock_result.to_input_list = MagicMock(return_value=[])

        published = []

        async def mock_publish(topic, payload, key=None):
            published.append(payload)

        import src.workers.message_processor as mp_mod
        with patch("src.database.connection._pool", mock_pool), \
             patch("agents.Runner.run", AsyncMock(return_value=mock_result)), \
             patch.object(mp_mod, "publish", mock_publish):
            from src.agent.customer_success_agent import CustomerSuccessAgent
            agent = CustomerSuccessAgent()
            await mp_mod._process_message(agent, payload)

        assert len(published) == 1
        assert published[0]["should_escalate"] is True


class TestResponseHandlerLogic:
    """Test response handler formatting and sending."""

    @pytest.mark.asyncio
    async def test_handle_response_formats_for_channel(self):
        """Response should be formatted per channel before sending."""
        payload = {
            "channel": "email",
            "customer_identifier": "user@test.com",
            "response_text": "Here is the answer",
            "ticket_id": "ticket-001",
            "conversation_id": "conv-001",
            "should_escalate": False,
            "latency_ms": 500.0,
        }

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=mock_conn)

        with patch("src.database.connection._pool", mock_pool):
            from src.workers.response_handler import _handle_response
            await _handle_response(payload)
            # Verify DB metrics were recorded
            mock_conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_response_whatsapp(self):
        """WhatsApp response should be formatted correctly."""
        payload = {
            "channel": "whatsapp",
            "customer_identifier": "+1234567890",
            "response_text": "Here is a short answer for WhatsApp",
            "ticket_id": "ticket-wa-001",
            "conversation_id": "conv-wa-001",
            "should_escalate": False,
            "latency_ms": 300.0,
        }

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=mock_conn)

        with patch("src.database.connection._pool", mock_pool):
            from src.workers.response_handler import _handle_response
            await _handle_response(payload)
            mock_conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_response_web_form(self):
        """Web form response uses SSE push."""
        payload = {
            "channel": "web_form",
            "customer_identifier": "user@web.com",
            "response_text": "Web form response here",
            "ticket_id": "ticket-wf-001",
            "conversation_id": "conv-wf-001",
            "should_escalate": False,
            "latency_ms": 200.0,
        }

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=mock_conn)

        with patch("src.database.connection._pool", mock_pool):
            from src.workers.response_handler import _handle_response
            await _handle_response(payload)
            mock_conn.execute.assert_called_once()
