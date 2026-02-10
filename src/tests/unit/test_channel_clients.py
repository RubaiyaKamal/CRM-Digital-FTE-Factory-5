"""Unit tests for channel client modules (Gmail, WhatsApp)."""
import pytest
import base64
import json
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from datetime import datetime, timedelta

# Import clients at module level for coverage tracking
import src.channels.gmail_client as gmail_mod
import src.channels.whatsapp_client as whatsapp_mod


class TestGmailClient:
    """Test Gmail API client functions."""

    @pytest.mark.asyncio
    async def test_load_credentials_from_db_success(self):
        """Test loading valid credentials from database."""
        mock_row = {
            "credentials": json.dumps({
                "token": "test-token",
                "refresh_token": "test-refresh",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "test-client-id",
                "client_secret": "test-secret",
                "scopes": ["https://www.googleapis.com/auth/gmail.modify"],
                "expiry": (datetime.now() + timedelta(hours=1)).isoformat(),
            })
        }

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=mock_row)
        mock_conn.execute = AsyncMock()
        mock_conn.close = AsyncMock()

        with patch("asyncpg.connect", AsyncMock(return_value=mock_conn)):
            creds = await gmail_mod._load_credentials_from_db("test@example.com")

            assert creds is not None
            assert creds.token == "test-token"
            assert creds.refresh_token == "test-refresh"

    @pytest.mark.asyncio
    async def test_load_credentials_from_db_not_found(self):
        """Test when no credentials exist in database."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)
        mock_conn.close = AsyncMock()

        with patch("asyncpg.connect", AsyncMock(return_value=mock_conn)):
            creds = await gmail_mod._load_credentials_from_db("noexist@example.com")

            assert creds is None

    @pytest.mark.asyncio
    async def test_load_credentials_with_expiry(self):
        """Test loading credentials with expiry set."""
        future_time = datetime.now() + timedelta(hours=1)
        mock_row = {
            "credentials": json.dumps({
                "token": "valid-token",
                "refresh_token": "refresh-token",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "client-id",
                "client_secret": "secret",
                "scopes": ["https://www.googleapis.com/auth/gmail.modify"],
                "expiry": future_time.isoformat(),
            })
        }

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=mock_row)
        mock_conn.execute = AsyncMock()
        mock_conn.close = AsyncMock()

        with patch("asyncpg.connect", AsyncMock(return_value=mock_conn)):
            creds = await gmail_mod._load_credentials_from_db("test@example.com")

            # Should successfully load credentials
            assert creds is not None
            assert creds.token == "valid-token"
            # Expiry should be set
            assert creds.expiry is not None

    @pytest.mark.asyncio
    async def test_get_gmail_service_success(self):
        """Test building Gmail service successfully."""
        mock_creds = Mock()
        mock_creds.token = "valid-token"

        mock_service = Mock()

        with patch.object(gmail_mod, "_load_credentials_from_db", AsyncMock(return_value=mock_creds)), \
             patch("asyncio.to_thread", AsyncMock(return_value=mock_service)):
            service = await gmail_mod.get_gmail_service()

            assert service is not None

    @pytest.mark.asyncio
    async def test_get_gmail_service_no_credentials(self):
        """Test building Gmail service when no credentials exist."""
        with patch.object(gmail_mod, "_load_credentials_from_db", AsyncMock(return_value=None)), \
             pytest.raises(RuntimeError, match="No Gmail credentials found"):
            await gmail_mod.get_gmail_service()

    @pytest.mark.asyncio
    async def test_fetch_unread_messages_success(self):
        """Test fetching unread messages successfully."""
        mock_service = Mock()
        mock_messages_api = Mock()
        mock_list_result = {"messages": [{"id": "msg1", "threadId": "thread1"}]}

        mock_messages_api.list.return_value.execute.return_value = mock_list_result
        mock_service.users.return_value.messages.return_value = mock_messages_api

        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(return_value=mock_service)), \
             patch("asyncio.to_thread", AsyncMock(return_value=mock_list_result)):
            messages = await gmail_mod.fetch_unread_messages(max_results=10)

            assert len(messages) == 1
            assert messages[0]["id"] == "msg1"

    @pytest.mark.asyncio
    async def test_fetch_unread_messages_empty(self):
        """Test fetching when no unread messages exist."""
        mock_service = Mock()
        mock_list_result = {"messages": []}

        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(return_value=mock_service)), \
             patch("asyncio.to_thread", AsyncMock(return_value=mock_list_result)):
            messages = await gmail_mod.fetch_unread_messages()

            assert messages == []

    @pytest.mark.asyncio
    async def test_fetch_unread_messages_auth_error(self):
        """Test handling authentication error when fetching messages."""
        from googleapiclient.errors import HttpError

        mock_error = HttpError(
            resp=Mock(status=401),
            content=b'{"error": "invalid_grant"}'
        )

        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(side_effect=mock_error)):
            messages = await gmail_mod.fetch_unread_messages()

            assert messages == []

    @pytest.mark.asyncio
    async def test_fetch_unread_messages_general_error(self):
        """Test handling general error when fetching messages."""
        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(side_effect=Exception("API Error"))):
            messages = await gmail_mod.fetch_unread_messages()

            assert messages == []

    def test_decode_mime_words_plain_text(self):
        """Test decoding plain ASCII text."""
        result = gmail_mod._decode_mime_words("Hello World")
        assert result == "Hello World"

    def test_decode_mime_words_empty(self):
        """Test decoding empty string."""
        result = gmail_mod._decode_mime_words("")
        assert result == ""

    def test_decode_mime_words_none(self):
        """Test decoding None."""
        result = gmail_mod._decode_mime_words(None)
        assert result == ""

    def test_decode_mime_words_utf8_encoded(self):
        """Test decoding UTF-8 MIME encoded words."""
        # This would be MIME encoded in reality, but testing the logic
        with patch("email.header.decode_header") as mock_decode:
            mock_decode.return_value = [(b"Test Subject", "utf-8")]
            result = gmail_mod._decode_mime_words("=?utf-8?B?VGVzdCBTdWJqZWN0?=")
            assert result == "Test Subject"

    def test_decode_mime_words_mixed_encoding(self):
        """Test decoding mixed plain and encoded parts."""
        with patch("email.header.decode_header") as mock_decode:
            mock_decode.return_value = [
                ("Plain ", None),
                (b"Encoded", "utf-8"),
            ]
            result = gmail_mod._decode_mime_words("Plain =?utf-8?B?RW5jb2RlZA==?=")
            assert "Plain" in result
            assert "Encoded" in result

    def test_decode_mime_words_error_handling(self):
        """Test error handling in MIME decoding."""
        with patch("email.header.decode_header", side_effect=Exception("Decode error")):
            result = gmail_mod._decode_mime_words("Bad encoding")
            # Should return original text on error
            assert result == "Bad encoding"

    def test_extract_body_plain_text(self):
        """Test extracting plain text body."""
        payload = {
            "mimeType": "text/plain",
            "body": {"data": base64.urlsafe_b64encode(b"Hello, this is the body").decode()}
        }

        body = gmail_mod._extract_body(payload)
        assert "Hello, this is the body" in body

    def test_extract_body_multipart_plain(self):
        """Test extracting body from multipart email with plain text."""
        payload = {
            "mimeType": "multipart/alternative",
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {"data": base64.urlsafe_b64encode(b"Plain text body").decode()}
                },
                {
                    "mimeType": "text/html",
                    "body": {"data": base64.urlsafe_b64encode(b"<p>HTML body</p>").decode()}
                }
            ]
        }

        body = gmail_mod._extract_body(payload)
        assert "Plain text body" in body

    def test_extract_body_nested_multipart(self):
        """Test extracting body from nested multipart structure."""
        payload = {
            "mimeType": "multipart/mixed",
            "parts": [
                {
                    "mimeType": "multipart/alternative",
                    "parts": [
                        {
                            "mimeType": "text/plain",
                            "body": {"data": base64.urlsafe_b64encode(b"Nested body").decode()}
                        }
                    ]
                }
            ]
        }

        body = gmail_mod._extract_body(payload)
        assert "Nested body" in body

    def test_extract_body_html_fallback(self):
        """Test falling back to HTML when no plain text available."""
        payload = {
            "mimeType": "multipart/alternative",
            "parts": [
                {
                    "mimeType": "text/html",
                    "body": {"data": base64.urlsafe_b64encode(b"<p>HTML only</p>").decode()}
                }
            ]
        }

        body = gmail_mod._extract_body(payload)
        # HTML tags should be stripped
        assert "HTML only" in body
        assert "<p>" not in body

    def test_extract_body_empty_payload(self):
        """Test extracting from empty payload."""
        payload = {}
        body = gmail_mod._extract_body(payload)
        assert body == ""

    @pytest.mark.asyncio
    async def test_get_message_details_success(self):
        """Test parsing full email message successfully."""
        mock_message = {
            "id": "msg123",
            "threadId": "thread456",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "John Doe <john@example.com>"},
                    {"name": "Date", "value": "Mon, 10 Feb 2026 10:00:00 +0000"},
                ],
                "mimeType": "text/plain",
                "body": {"data": base64.urlsafe_b64encode(b"Test body content").decode()}
            }
        }

        mock_service = Mock()

        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(return_value=mock_service)), \
             patch("asyncio.to_thread", AsyncMock(return_value=mock_message)):
            details = await gmail_mod.get_message_details("msg123")

            assert details["id"] == "msg123"
            assert details["threadId"] == "thread456"
            assert details["subject"] == "Test Subject"
            assert details["from"] == "john@example.com"
            assert "Test body content" in details["body"]

    @pytest.mark.asyncio
    async def test_get_message_details_complex_from(self):
        """Test parsing email with complex From header."""
        mock_message = {
            "id": "msg123",
            "threadId": "thread456",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test"},
                    {"name": "From", "value": "Display Name (Company) <email@domain.com>"},
                    {"name": "Date", "value": ""},
                ],
                "mimeType": "text/plain",
                "body": {"data": base64.urlsafe_b64encode(b"Body").decode()}
            }
        }

        mock_service = Mock()

        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(return_value=mock_service)), \
             patch("asyncio.to_thread", AsyncMock(return_value=mock_message)):
            details = await gmail_mod.get_message_details("msg123")

            assert details["from"] == "email@domain.com"

    @pytest.mark.asyncio
    async def test_get_message_details_http_error(self):
        """Test handling HTTP error when fetching message details."""
        from googleapiclient.errors import HttpError

        mock_error = HttpError(
            resp=Mock(status=404),
            content=b'{"error": "Message not found"}'
        )

        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(side_effect=mock_error)), \
             pytest.raises(HttpError):
            await gmail_mod.get_message_details("nonexistent")

    @pytest.mark.asyncio
    async def test_get_message_details_parse_error(self):
        """Test handling parsing error in message details."""
        mock_message = {
            "id": "msg123",
            # Missing required fields to trigger parsing error
        }

        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(return_value=Mock())), \
             patch("asyncio.to_thread", AsyncMock(return_value=mock_message)), \
             pytest.raises(Exception):
            await gmail_mod.get_message_details("msg123")

    @pytest.mark.asyncio
    async def test_send_email_success(self):
        """Test sending email successfully."""
        mock_result = {"id": "sent123", "threadId": "thread789"}
        mock_service = Mock()

        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(return_value=mock_service)), \
             patch("asyncio.to_thread", AsyncMock(return_value=mock_result)):
            success = await gmail_mod.send_email(
                to="recipient@example.com",
                subject="Test Subject",
                body="Test body content"
            )

            assert success is True

    @pytest.mark.asyncio
    async def test_send_email_with_threading(self):
        """Test sending email with thread ID for conversation threading."""
        mock_result = {"id": "sent456", "threadId": "existing-thread"}
        mock_service = Mock()

        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(return_value=mock_service)), \
             patch("asyncio.to_thread", AsyncMock(return_value=mock_result)):
            success = await gmail_mod.send_email(
                to="recipient@example.com",
                subject="Re: Original Subject",
                body="Reply body",
                thread_id="existing-thread"
            )

            assert success is True

    @pytest.mark.asyncio
    async def test_send_email_http_error(self):
        """Test handling HTTP error when sending email."""
        from googleapiclient.errors import HttpError

        mock_error = HttpError(
            resp=Mock(status=403),
            content=b'{"error": "Insufficient permissions"}'
        )

        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(return_value=Mock())), \
             patch("asyncio.to_thread", AsyncMock(side_effect=mock_error)):
            success = await gmail_mod.send_email(
                to="test@example.com",
                subject="Test",
                body="Body"
            )

            assert success is False

    @pytest.mark.asyncio
    async def test_send_email_general_error(self):
        """Test handling general error when sending email."""
        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(side_effect=Exception("Network error"))):
            success = await gmail_mod.send_email(
                to="test@example.com",
                subject="Test",
                body="Body"
            )

            assert success is False

    @pytest.mark.asyncio
    async def test_mark_as_read_success(self):
        """Test marking message as read successfully."""
        mock_service = Mock()

        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(return_value=mock_service)), \
             patch("asyncio.to_thread", AsyncMock(return_value={})):
            success = await gmail_mod.mark_as_read("msg789")

            assert success is True

    @pytest.mark.asyncio
    async def test_mark_as_read_http_error(self):
        """Test handling HTTP error when marking as read."""
        from googleapiclient.errors import HttpError

        mock_error = HttpError(
            resp=Mock(status=404),
            content=b'{"error": "Message not found"}'
        )

        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(return_value=Mock())), \
             patch("asyncio.to_thread", AsyncMock(side_effect=mock_error)):
            success = await gmail_mod.mark_as_read("nonexistent")

            assert success is False

    @pytest.mark.asyncio
    async def test_mark_as_read_general_error(self):
        """Test handling general error when marking as read."""
        with patch.object(gmail_mod, "get_gmail_service", AsyncMock(side_effect=Exception("API error"))):
            success = await gmail_mod.mark_as_read("msg789")

            assert success is False
