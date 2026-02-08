"""Unit tests for configuration."""
import pytest
from src.config import Settings


class TestSettings:
    def test_default_database_url(self):
        s = Settings()
        assert "localhost" in s.database_url or "crm_fte" in s.database_url

    def test_database_url_safe_masks_password(self):
        s = Settings()
        s.database_url = "postgresql://user:secret123@localhost:5432/db"
        assert "secret123" not in s.database_url_safe
        assert "***" in s.database_url_safe

    def test_database_url_safe_no_password(self):
        s = Settings()
        s.database_url = "postgresql://localhost:5432/db"
        safe = s.database_url_safe
        assert safe == s.database_url

    def test_default_model(self):
        s = Settings()
        assert s.openai_model == "gpt-4o-mini"

    def test_default_pool_sizes(self):
        s = Settings()
        assert s.db_pool_min == 2
        assert s.db_pool_max == 10
