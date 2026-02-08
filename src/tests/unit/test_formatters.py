"""Unit tests for channel response formatters."""
import pytest
from src.agent.formatters import format_response, _extract_first_name
from src.agent.models import Channel


SAMPLE_RESPONSE = """To reset your password:

1. Go to the login page
2. Click "Forgot Password"
3. Enter your email address
4. Check your inbox for the reset link

**IMPORTANT:** The link expires in 1 hour."""


class TestExtractFirstName:
    def test_email_simple(self):
        assert _extract_first_name("john@example.com") == "John"

    def test_email_dotted(self):
        assert _extract_first_name("john.doe@example.com") == "John"

    def test_full_name(self):
        assert _extract_first_name("Jane Smith") == "Jane"

    def test_single_name(self):
        assert _extract_first_name("Alice") == "Alice"

    def test_none(self):
        assert _extract_first_name(None) == "there"

    def test_empty(self):
        assert _extract_first_name("") == "there"


class TestEmailFormatter:
    def test_contains_greeting(self):
        result = format_response(SAMPLE_RESPONSE, Channel.EMAIL, "user@example.com")
        assert result.startswith("Hi User,")

    def test_contains_signature(self):
        result = format_response(SAMPLE_RESPONSE, Channel.EMAIL, "user@example.com")
        assert "CloudFlow Support Team" in result

    def test_length_limit(self):
        long_response = "A" * 3000
        result = format_response(long_response, Channel.EMAIL, "user@example.com")
        assert len(result) <= 2000

    def test_keeps_markdown(self):
        result = format_response(SAMPLE_RESPONSE, Channel.EMAIL, "user@example.com")
        assert "**IMPORTANT:**" in result


class TestWhatsAppFormatter:
    def test_concise_greeting(self):
        result = format_response("Short reply", Channel.WHATSAPP, "John")
        assert "Hey John!" in result

    def test_removes_markdown(self):
        result = format_response("**Bold** and _italic_", Channel.WHATSAPP, "user")
        assert "**" not in result
        assert "__" not in result

    def test_length_limit(self):
        long_response = "A " * 1000
        result = format_response(long_response, Channel.WHATSAPP, "user")
        assert len(result) <= 1600


class TestWebFormFormatter:
    def test_contains_greeting(self):
        result = format_response(SAMPLE_RESPONSE, Channel.WEB_FORM, "Sarah")
        assert result.startswith("Hi Sarah,")

    def test_contains_signature(self):
        result = format_response(SAMPLE_RESPONSE, Channel.WEB_FORM, "Sarah")
        assert "CloudFlow Support" in result

    def test_length_limit(self):
        long_response = "B" * 2000
        result = format_response(long_response, Channel.WEB_FORM, "user")
        assert len(result) <= 1200
