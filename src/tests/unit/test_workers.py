"""Unit tests for worker modules."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from uuid import uuid4

# Import workers at module level for coverage tracking
import src.workers.message_processor
import src.workers.response_handler
from src.agent.customer_success_agent import CustomerSuccessAgent


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

    @pytest.mark.asyncio
    async def test_process_message_kafka_publish_failure(self):
        """Test error handling when Kafka publish fails."""
        payload = {
            "ticket_id": "ticket-002",
            "conversation_id": "conv-002",
            "customer_id": "cust-002",
            "customer_identifier": "user2@test.com",
            "channel": "email",
            "message_text": "Need help with billing",
            "subject": "Billing question",
        }

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[])
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=mock_conn)

        mock_result = MagicMock()
        mock_result.final_output = "Billing response"
        mock_result.to_input_list = MagicMock(return_value=[])

        # Mock publish to raise an exception
        async def failing_publish(topic, payload, key=None):
            raise Exception("Kafka publish failed")

        import src.workers.message_processor as mp_mod
        with patch("src.database.connection._pool", mock_pool), \
             patch("agents.Runner.run", AsyncMock(return_value=mock_result)), \
             patch.object(mp_mod, "publish", failing_publish), \
             pytest.raises(Exception, match="Kafka publish failed"):
            from src.agent.customer_success_agent import CustomerSuccessAgent
            agent = CustomerSuccessAgent()
            await mp_mod._process_message(agent, payload)

    @pytest.mark.asyncio
    async def test_process_message_database_error(self):
        """Test error handling when database query fails."""
        payload = {
            "ticket_id": "ticket-003",
            "conversation_id": "conv-003",
            "customer_id": "cust-003",
            "customer_identifier": "user3@test.com",
            "channel": "whatsapp",
            "message_text": "Account issue",
            "subject": "Account help",
        }

        # Mock DB connection that fails
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(side_effect=Exception("Database connection failed"))
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=mock_conn)

        import src.workers.message_processor as mp_mod
        with patch("src.database.connection._pool", mock_pool), \
             pytest.raises(Exception, match="Database connection failed"):
            from src.agent.customer_success_agent import CustomerSuccessAgent
            agent = CustomerSuccessAgent()
            await mp_mod._process_message(agent, payload)

    @pytest.mark.asyncio
    async def test_process_message_agent_execution_error(self):
        """Test error handling when agent execution fails - should use fallback response."""
        payload = {
            "ticket_id": "ticket-004",
            "conversation_id": "conv-004",
            "customer_id": "cust-004",
            "customer_identifier": "user4@test.com",
            "channel": "email",
            "message_text": "Complex question",
            "subject": "Help needed",
        }

        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[])
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=mock_conn)

        # Mock agent execution to fail
        async def failing_agent_run(*args, **kwargs):
            raise Exception("Agent execution failed")

        published = []

        async def mock_publish(topic, payload_data, key=None):
            published.append(payload_data)

        import src.workers.message_processor as mp_mod
        with patch("src.database.connection._pool", mock_pool), \
             patch("agents.Runner.run", failing_agent_run), \
             patch.object(mp_mod, "publish", mock_publish):
            from src.agent.customer_success_agent import CustomerSuccessAgent
            agent = CustomerSuccessAgent()
            # Should not raise - agent catches exception and uses fallback
            await mp_mod._process_message(agent, payload)

            # Verify fallback response was used (agent catches exception)
            assert len(published) == 1
            # Fallback response is the escalation message
            assert "specialist" in published[0]["response_text"].lower() or \
                   "team member" in published[0]["response_text"].lower()

    @pytest.mark.asyncio
    async def test_process_message_empty_conversation_history(self):
        """Test processing with empty conversation history."""
        payload = {
            "ticket_id": "ticket-005",
            "conversation_id": "conv-005",
            "customer_id": "cust-005",
            "customer_identifier": "newuser@test.com",
            "channel": "web_form",
            "message_text": "First message from new customer",
            "subject": "New inquiry",
        }

        # Mock DB with empty history
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[])
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=mock_conn)

        mock_result = MagicMock()
        mock_result.final_output = "Welcome! How can I help?"
        mock_result.to_input_list = MagicMock(return_value=[])

        import src.workers.message_processor as mp_mod
        with patch("src.database.connection._pool", mock_pool), \
             patch("agents.Runner.run", AsyncMock(return_value=mock_result)), \
             patch.object(mp_mod, "publish", AsyncMock()):
            from src.agent.customer_success_agent import CustomerSuccessAgent
            agent = CustomerSuccessAgent()
            await mp_mod._process_message(agent, payload)
            # Should succeed with empty history


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

    @pytest.mark.asyncio
    async def test_handle_response_missing_adapter(self):
        """Test handling response when channel adapter is not available."""
        payload = {
            "channel": "email",
            "customer_identifier": "user@test.com",
            "response_text": "Response text",
            "ticket_id": "ticket-006",
            "conversation_id": "conv-006",
            "should_escalate": False,
            "latency_ms": 100.0,
        }

        mock_conn = AsyncMock()
        mock_conn.execute = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=mock_conn)

        # Mock channel_adapters to be empty
        import src.workers.response_handler as rh_mod
        original_adapters = rh_mod._channel_adapters.copy()
        rh_mod._channel_adapters.clear()

        try:
            with patch("src.database.connection._pool", mock_pool):
                from src.workers.response_handler import _handle_response
                # Should not raise exception, just skip sending when adapter missing
                await _handle_response(payload)
                # Metrics should still be recorded
                mock_conn.execute.assert_called_once()
        finally:
            # Restore original adapters
            rh_mod._channel_adapters.update(original_adapters)

    @pytest.mark.asyncio
    async def test_handle_response_database_update_failure(self):
        """Test error handling when database metrics update fails."""
        payload = {
            "channel": "email",
            "customer_identifier": "user@test.com",
            "response_text": "Response",
            "ticket_id": "ticket-007",
            "conversation_id": "conv-007",
            "should_escalate": False,
            "latency_ms": 250.0,
        }

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock(side_effect=Exception("Database write failed"))
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=mock_conn)

        with patch("src.database.connection._pool", mock_pool), \
             pytest.raises(Exception, match="Database write failed"):
            from src.workers.response_handler import _handle_response
            await _handle_response(payload)

    @pytest.mark.asyncio
    async def test_handle_response_email_with_thread_id(self):
        """Test email response with Gmail thread ID for threading."""
        payload = {
            "channel": "email",
            "customer_identifier": "user@test.com",
            "response_text": "Follow-up response",
            "ticket_id": "ticket-008",
            "conversation_id": "conv-008",
            "should_escalate": False,
            "latency_ms": 400.0,
        }

        # Mock DB with message containing thread_id
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value={
            "metadata": {
                "gmail_thread_id": "thread-12345",
                "subject": "Original Subject"
            }
        })
        mock_conn.execute = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=mock_conn)

        # Mock Gmail adapter send to verify thread_id is passed
        from src.channels.gmail import GmailAdapter
        mock_send = AsyncMock(return_value=True)

        with patch("src.database.connection._pool", mock_pool), \
             patch.object(GmailAdapter, "send", mock_send):
            from src.workers.response_handler import _handle_response
            await _handle_response(payload)

            # Verify send was called with thread_id
            assert mock_send.called
            call_kwargs = mock_send.call_args[1]
            assert "gmail_thread_id" in call_kwargs
            assert call_kwargs["gmail_thread_id"] == "thread-12345"

    @pytest.mark.asyncio
    async def test_handle_response_email_no_thread_id(self):
        """Test email response when no thread ID exists (new conversation)."""
        payload = {
            "channel": "email",
            "customer_identifier": "newuser@test.com",
            "response_text": "First response",
            "ticket_id": "ticket-009",
            "conversation_id": "conv-009",
            "should_escalate": False,
            "latency_ms": 150.0,
        }

        # Mock DB with no message metadata
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=mock_conn)

        with patch("src.database.connection._pool", mock_pool):
            from src.workers.response_handler import _handle_response
            await _handle_response(payload)
            # Should succeed without thread_id
            mock_conn.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_response_escalated_ticket(self):
        """Test response handling for escalated tickets."""
        payload = {
            "channel": "whatsapp",
            "customer_identifier": "+1234567890",
            "response_text": "Escalating to human agent",
            "ticket_id": "ticket-010",
            "conversation_id": "conv-010",
            "should_escalate": True,
            "latency_ms": 600.0,
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

            # Verify escalated=True was recorded in metrics
            call_args = mock_conn.execute.call_args[0]
            assert call_args[4] is True  # should_escalate parameter
