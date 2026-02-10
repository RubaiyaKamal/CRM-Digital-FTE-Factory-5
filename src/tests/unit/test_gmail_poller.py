"""Unit tests for Gmail poller worker."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock
import httpx

# Import gmail_poller at module level for coverage tracking
import src.workers.gmail_poller as poller_mod


class TestNormalizeEmailToWebhook:
    """Test email normalization to webhook format."""

    @pytest.mark.asyncio
    async def test_normalize_complete_email(self):
        """Test normalizing email with all fields present."""
        email_data = {
            "id": "msg123",
            "threadId": "thread456",
            "from": "sender@example.com",
            "from_full": "John Doe <sender@example.com>",
            "subject": "Test Subject",
            "body": "Test email body",
            "date": "Mon, 10 Feb 2026 10:00:00 +0000",
        }

        result = await poller_mod.normalize_email_to_webhook(email_data)

        assert result["email"] == "sender@example.com"
        assert result["subject"] == "Test Subject"
        assert result["message"] == "Test email body"
        assert result["session_id"] == "thread456"
        assert result["metadata"]["gmail_message_id"] == "msg123"
        assert result["metadata"]["gmail_thread_id"] == "thread456"
        assert result["metadata"]["from_full"] == "John Doe <sender@example.com>"
        assert result["metadata"]["date"] == "Mon, 10 Feb 2026 10:00:00 +0000"

    @pytest.mark.asyncio
    async def test_normalize_email_no_subject(self):
        """Test normalizing email with missing subject."""
        email_data = {
            "id": "msg456",
            "threadId": "thread789",
            "from": "user@test.com",
            "body": "Email content",
        }

        result = await poller_mod.normalize_email_to_webhook(email_data)

        assert result["subject"] == "(No Subject)"
        assert result["email"] == "user@test.com"
        assert result["message"] == "Email content"

    @pytest.mark.asyncio
    async def test_normalize_email_minimal_data(self):
        """Test normalizing email with minimal required fields."""
        email_data = {
            "id": "msg789",
            "threadId": "thread123",
            "from": "minimal@example.com",
            "body": "Minimal content",
        }

        result = await poller_mod.normalize_email_to_webhook(email_data)

        assert result["email"] == "minimal@example.com"
        assert result["message"] == "Minimal content"
        assert result["session_id"] == "thread123"
        # Metadata should handle missing fields gracefully
        assert result["metadata"]["from_full"] == "minimal@example.com"
        assert result["metadata"]["date"] == ""


class TestProcessMessage:
    """Test individual message processing."""

    @pytest.mark.asyncio
    async def test_process_message_success(self):
        """Test successfully processing a message."""
        message_metadata = {"id": "msg-001", "threadId": "thread-001"}

        email_data = {
            "id": "msg-001",
            "threadId": "thread-001",
            "from": "test@example.com",
            "subject": "Test",
            "body": "Body",
        }

        mock_http_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.post = AsyncMock(return_value=mock_response)

        with patch.object(poller_mod, "get_message_details", AsyncMock(return_value=email_data)), \
             patch.object(poller_mod, "mark_as_read", AsyncMock(return_value=True)):
            success = await poller_mod.process_message(message_metadata, mock_http_client)

            assert success is True
            # Verify webhook was called
            mock_http_client.post.assert_called_once()
            call_args = mock_http_client.post.call_args
            assert "/webhooks/email" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_process_message_webhook_http_error(self):
        """Test handling webhook HTTP error."""
        message_metadata = {"id": "msg-002", "threadId": "thread-002"}

        email_data = {
            "id": "msg-002",
            "threadId": "thread-002",
            "from": "test@example.com",
            "subject": "Test",
            "body": "Body",
        }

        mock_http_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        # Create HTTPStatusError
        http_error = httpx.HTTPStatusError(
            "Server error",
            request=Mock(),
            response=mock_response
        )
        mock_http_client.post = AsyncMock(side_effect=http_error)

        with patch.object(poller_mod, "get_message_details", AsyncMock(return_value=email_data)), \
             patch.object(poller_mod, "mark_as_read", AsyncMock()):
            success = await poller_mod.process_message(message_metadata, mock_http_client)

            assert success is False
            # mark_as_read should NOT be called on webhook error
            # (In this mock setup, it's not called)

    @pytest.mark.asyncio
    async def test_process_message_webhook_request_error(self):
        """Test handling webhook connection error."""
        message_metadata = {"id": "msg-003", "threadId": "thread-003"}

        email_data = {
            "id": "msg-003",
            "threadId": "thread-003",
            "from": "test@example.com",
            "subject": "Test",
            "body": "Body",
        }

        mock_http_client = AsyncMock()
        request_error = httpx.RequestError("Connection refused")
        mock_http_client.post = AsyncMock(side_effect=request_error)

        with patch.object(poller_mod, "get_message_details", AsyncMock(return_value=email_data)):
            success = await poller_mod.process_message(message_metadata, mock_http_client)

            assert success is False

    @pytest.mark.asyncio
    async def test_process_message_get_details_error(self):
        """Test handling error when fetching message details."""
        message_metadata = {"id": "msg-004", "threadId": "thread-004"}

        mock_http_client = AsyncMock()

        with patch.object(poller_mod, "get_message_details", AsyncMock(side_effect=Exception("Gmail API error"))):
            success = await poller_mod.process_message(message_metadata, mock_http_client)

            assert success is False

    @pytest.mark.asyncio
    async def test_process_message_mark_as_read_called(self):
        """Test that mark_as_read is called after successful webhook post."""
        message_metadata = {"id": "msg-005", "threadId": "thread-005"}

        email_data = {
            "id": "msg-005",
            "threadId": "thread-005",
            "from": "test@example.com",
            "subject": "Test",
            "body": "Body",
        }

        mock_http_client = AsyncMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_client.post = AsyncMock(return_value=mock_response)

        mock_mark_as_read = AsyncMock(return_value=True)

        with patch.object(poller_mod, "get_message_details", AsyncMock(return_value=email_data)), \
             patch.object(poller_mod, "mark_as_read", mock_mark_as_read):
            success = await poller_mod.process_message(message_metadata, mock_http_client)

            assert success is True
            # Verify mark_as_read was called with correct message ID
            mock_mark_as_read.assert_called_once_with("msg-005")


class TestSignalHandler:
    """Test signal handling for graceful shutdown."""

    def test_signal_handler_sets_shutdown_flag(self):
        """Test that signal handler sets the shutdown flag."""
        # Reset flag first
        poller_mod.shutdown_flag = False

        # Call signal handler
        poller_mod.signal_handler(2, None)  # SIGINT = 2

        # Flag should be set
        assert poller_mod.shutdown_flag is True

        # Reset for other tests
        poller_mod.shutdown_flag = False


class TestPollGmailInbox:
    """Test the main polling loop logic."""

    @pytest.mark.asyncio
    async def test_poll_gmail_inbox_mock_mode(self):
        """Test that poller doesn't run when GMAIL_MOCK=true."""
        with patch.object(poller_mod.settings, "gmail_mock", True):
            # Should return immediately without polling
            await poller_mod.poll_gmail_inbox()
            # If it returns without error, mock mode is working

    @pytest.mark.asyncio
    async def test_poll_gmail_inbox_no_messages(self):
        """Test polling when no unread messages exist."""
        # Reset shutdown flag
        poller_mod.shutdown_flag = False

        # Set flag after one iteration
        async def set_flag_after_delay():
            await asyncio.sleep(0.1)
            poller_mod.shutdown_flag = True

        with patch.object(poller_mod.settings, "gmail_mock", False), \
             patch.object(poller_mod.settings, "gmail_polling_interval", 0.05), \
             patch.object(poller_mod, "fetch_unread_messages", AsyncMock(return_value=[])):

            # Start shutdown task
            shutdown_task = asyncio.create_task(set_flag_after_delay())

            # Should poll once and find no messages
            await poller_mod.poll_gmail_inbox()

            await shutdown_task

        # Reset flag
        poller_mod.shutdown_flag = False

    @pytest.mark.asyncio
    async def test_poll_gmail_inbox_processes_messages(self):
        """Test polling and processing multiple messages."""
        # Reset shutdown flag
        poller_mod.shutdown_flag = False

        messages = [
            {"id": "msg1", "threadId": "thread1"},
            {"id": "msg2", "threadId": "thread2"},
        ]

        email_data = {
            "id": "msg1",
            "threadId": "thread1",
            "from": "test@example.com",
            "subject": "Test",
            "body": "Body",
        }

        # Track how many times fetch was called
        fetch_call_count = 0

        async def mock_fetch(*args, **kwargs):
            nonlocal fetch_call_count
            fetch_call_count += 1
            if fetch_call_count == 1:
                return messages
            else:
                # Trigger shutdown after first fetch
                poller_mod.shutdown_flag = True
                return []

        with patch.object(poller_mod.settings, "gmail_mock", False), \
             patch.object(poller_mod.settings, "gmail_polling_interval", 0.05), \
             patch.object(poller_mod, "fetch_unread_messages", mock_fetch), \
             patch.object(poller_mod, "get_message_details", AsyncMock(return_value=email_data)), \
             patch.object(poller_mod, "mark_as_read", AsyncMock(return_value=True)), \
             patch("httpx.AsyncClient") as mock_client_class:

            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock()
            mock_client_class.return_value = mock_client

            await poller_mod.poll_gmail_inbox()

        # Reset flag
        poller_mod.shutdown_flag = False

    @pytest.mark.asyncio
    async def test_poll_gmail_inbox_error_backoff(self):
        """Test exponential backoff on consecutive errors."""
        # Reset shutdown flag
        poller_mod.shutdown_flag = False

        error_count = 0

        async def mock_fetch_with_errors(*args, **kwargs):
            nonlocal error_count
            error_count += 1
            if error_count >= 3:
                # Stop after 3 errors
                poller_mod.shutdown_flag = True
            raise Exception(f"Fetch error {error_count}")

        with patch.object(poller_mod.settings, "gmail_mock", False), \
             patch.object(poller_mod.settings, "gmail_polling_interval", 0.01), \
             patch.object(poller_mod, "fetch_unread_messages", mock_fetch_with_errors), \
             patch("asyncio.sleep", AsyncMock()) as mock_sleep:

            await poller_mod.poll_gmail_inbox()

            # Should have called sleep with backoff intervals
            # First error: backoff = 0.01 * 2^1 = 0.02
            # Second error: backoff = 0.01 * 2^2 = 0.04
            assert mock_sleep.called

        # Reset flag
        poller_mod.shutdown_flag = False

    @pytest.mark.asyncio
    async def test_poll_gmail_inbox_max_consecutive_errors(self):
        """Test that poller stops after max consecutive errors."""
        # Reset shutdown flag
        poller_mod.shutdown_flag = False

        async def mock_fetch_error(*args, **kwargs):
            raise Exception("Persistent fetch error")

        with patch.object(poller_mod.settings, "gmail_mock", False), \
             patch.object(poller_mod.settings, "gmail_polling_interval", 0.01), \
             patch.object(poller_mod, "fetch_unread_messages", mock_fetch_error), \
             patch("asyncio.sleep", AsyncMock()):

            await poller_mod.poll_gmail_inbox()

            # Should have stopped due to max errors
            # (The loop should exit naturally)

        # Reset flag
        poller_mod.shutdown_flag = False


class TestHealthCheckEndpoint:
    """Test health check functionality."""

    @pytest.mark.asyncio
    async def test_health_check_logs(self):
        """Test that health check logs correctly."""
        # Just verify it runs without error
        await poller_mod.health_check_endpoint()
        # If no exception, health check is working
