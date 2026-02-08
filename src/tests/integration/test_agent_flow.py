"""Integration tests for the agent processing flow."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.agent.models import AgentTask, Channel


@pytest.fixture
def mock_agent_dependencies():
    """Mock all external dependencies for agent tests."""
    mock_conn = AsyncMock()
    mock_conn.fetch = AsyncMock(return_value=[])
    mock_conn.fetchval = AsyncMock(return_value="ticket-uuid")
    mock_conn.execute = AsyncMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)

    mock_pool = MagicMock()
    mock_pool.acquire = MagicMock(return_value=mock_conn)

    return mock_pool


class TestMessageProcessor:
    @pytest.mark.asyncio
    async def test_process_normal_message(self, mock_agent_dependencies):
        """Test processing a normal how-to message."""
        with patch("src.database.connection._pool", mock_agent_dependencies), \
             patch("openai.AsyncOpenAI") as mock_openai:
            # Mock OpenAI agent response
            mock_result = MagicMock()
            mock_result.final_output = "Here's how to reset your password: go to Settings → Security"
            mock_result.new_items = []

            with patch("agents.Runner.run", AsyncMock(return_value=mock_result)):
                from src.agent.customer_success_agent import CustomerSuccessAgent
                agent = CustomerSuccessAgent()

                task = AgentTask(
                    ticket_id="test-ticket-1",
                    conversation_id="test-conv-1",
                    customer_id="test-customer-1",
                    customer_identifier="user@test.com",
                    channel=Channel.WEB_FORM,
                    message_text="How do I reset my password?",
                )

                result = await agent.process(task)

                assert result.ticket_id == "test-ticket-1"
                assert result.should_escalate is False
                assert len(result.response_text) > 0

    @pytest.mark.asyncio
    async def test_process_escalation_message(self, mock_agent_dependencies):
        """Test that security keywords trigger escalation."""
        with patch("src.database.connection._pool", mock_agent_dependencies), \
             patch("agents.Runner.run", AsyncMock(return_value=MagicMock(
                 final_output="I'll connect you with our team",
                 new_items=[],
             ))):
            from src.agent.customer_success_agent import CustomerSuccessAgent
            agent = CustomerSuccessAgent()

            task = AgentTask(
                ticket_id="test-ticket-2",
                conversation_id="test-conv-2",
                customer_id="test-customer-2",
                customer_identifier="ciso@company.com",
                channel=Channel.EMAIL,
                message_text="We've been hacked! Unauthorized access to our account!",
            )

            result = await agent.process(task)

            assert result.should_escalate is True
            assert result.escalation_priority is not None


class TestKafkaFlow:
    @pytest.mark.asyncio
    async def test_message_payload_structure(self):
        """Test that Kafka message payload has correct structure."""
        from src.agent.models import KafkaMessage
        msg = KafkaMessage(
            topic="fte.tickets.incoming",
            payload={
                "ticket_id": "t-1",
                "customer_id": "c-1",
                "channel": "email",
                "message_text": "test",
            },
        )
        assert msg.version == "1.0"
        assert msg.payload["channel"] == "email"
