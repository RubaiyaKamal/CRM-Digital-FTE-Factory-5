"""Unit tests for database connection module."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestDatabaseConnection:
    @pytest.mark.asyncio
    async def test_get_db_pool_returns_existing_pool(self):
        """If pool already exists, get_db_pool returns it without creating."""
        import src.database.connection as db_mod
        mock_pool = MagicMock()
        original = db_mod._pool
        db_mod._pool = mock_pool
        try:
            from src.database.connection import get_db_pool
            result = await get_db_pool()
            assert result is mock_pool
        finally:
            db_mod._pool = original

    @pytest.mark.asyncio
    async def test_get_db_pool_creates_when_none(self):
        """If pool is None, get_db_pool calls create_pool."""
        import src.database.connection as db_mod
        original = db_mod._pool
        db_mod._pool = None
        mock_pool = MagicMock()
        try:
            with patch("src.database.connection.create_pool", AsyncMock(return_value=mock_pool)):
                from src.database.connection import get_db_pool
                result = await get_db_pool()
                assert result is mock_pool
        finally:
            db_mod._pool = original

    @pytest.mark.asyncio
    async def test_close_pool_closes_and_clears(self):
        """close_pool should close the pool and set _pool to None."""
        import src.database.connection as db_mod
        original = db_mod._pool
        mock_pool = AsyncMock()
        db_mod._pool = mock_pool
        try:
            from src.database.connection import close_pool
            await close_pool()
            mock_pool.close.assert_called_once()
            assert db_mod._pool is None
        finally:
            db_mod._pool = original

    @pytest.mark.asyncio
    async def test_close_pool_noop_when_none(self):
        """close_pool should not error when pool is already None."""
        import src.database.connection as db_mod
        original = db_mod._pool
        db_mod._pool = None
        try:
            from src.database.connection import close_pool
            await close_pool()  # Should not raise
        finally:
            db_mod._pool = original

    @pytest.mark.asyncio
    async def test_apply_schema_executes_sql(self):
        """apply_schema reads schema.sql and executes it."""
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=None)
        mock_pool = MagicMock()
        mock_pool.acquire = MagicMock(return_value=mock_conn)

        from src.database.connection import apply_schema
        await apply_schema(mock_pool)
        mock_conn.execute.assert_called_once()
        # Verify it passed actual SQL content
        args = mock_conn.execute.call_args[0]
        assert len(args) == 1
        assert "CREATE" in args[0] or "create" in args[0].lower()

    @pytest.mark.asyncio
    async def test_create_pool_calls_asyncpg(self):
        """create_pool calls asyncpg.create_pool with configured settings."""
        mock_pool = MagicMock()
        with patch("asyncpg.create_pool", AsyncMock(return_value=mock_pool)):
            from src.database.connection import create_pool
            result = await create_pool()
            assert result is mock_pool


class TestToolsWithMockedDB:
    """Test agent tool functions with mocked DB pool.

    Note: @function_tool wraps functions as FunctionTool objects (not directly callable).
    We call the underlying functions via the tools module's private helpers.
    """

    def test_get_pool_raises_when_uninitialized(self):
        """_get_pool should raise RuntimeError when _pool is None."""
        import src.database.connection as db_mod
        original = db_mod._pool
        db_mod._pool = None
        try:
            from src.agent.tools import _get_pool
            with pytest.raises(RuntimeError, match="not initialized"):
                _get_pool()
        finally:
            db_mod._pool = original

    def test_get_pool_returns_pool_when_set(self):
        """_get_pool returns pool when initialized."""
        import src.database.connection as db_mod
        original = db_mod._pool
        mock_pool = MagicMock()
        db_mod._pool = mock_pool
        try:
            from src.agent.tools import _get_pool
            result = _get_pool()
            assert result is mock_pool
        finally:
            db_mod._pool = original


    @pytest.mark.asyncio
    async def test_detect_escalation_all_paths(self):
        """Test all escalation detection paths for coverage."""
        from src.agent.tools import detect_escalation_need

        # Compliance keyword
        e, t, r, s = detect_escalation_need("need soc 2 report", "general", 0.6)
        assert e is True
        assert t == "keywords"

        # Category escalation (sales)
        e, t, r, s = detect_escalation_need("pricing question", "sales", 0.6)
        assert e is True
        assert t == "category"

        # Low sentiment (0.25 = high priority, not urgent)
        e, t, r, s = detect_escalation_need("this is frustrating", "general", 0.25)
        assert e is True
        assert t == "sentiment"

        # Very low sentiment (< 0.2 = urgent)
        e, t, r, s = detect_escalation_need("absolutely terrible", "general", 0.15)
        assert e is True
        assert t == "sentiment"

        # Speak to person
        e, t, r, s = detect_escalation_need("I want to talk to a person", "general", 0.5)
        assert e is True
        assert t == "explicit_request"
