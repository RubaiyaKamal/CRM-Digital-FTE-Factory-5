"""
PostgreSQL connection pool management using asyncpg.
"""
from __future__ import annotations

import logging
from typing import Optional

import asyncpg

from src.config import settings

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None


async def get_db_pool() -> asyncpg.Pool:
    """Return the global connection pool, creating it if necessary."""
    global _pool
    if _pool is None:
        _pool = await create_pool()
    return _pool


async def create_pool() -> asyncpg.Pool:
    """Create a new asyncpg connection pool."""
    logger.info("Creating PostgreSQL connection pool: %s", settings.database_url_safe)
    pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=settings.db_pool_min,
        max_size=settings.db_pool_max,
        command_timeout=30,
    )
    logger.info("PostgreSQL pool ready (min=%d, max=%d)", settings.db_pool_min, settings.db_pool_max)
    return pool


async def close_pool() -> None:
    """Close the global connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("PostgreSQL pool closed")


async def apply_schema(pool: asyncpg.Pool) -> None:
    """Apply schema.sql to the database (idempotent, uses IF NOT EXISTS)."""
    import pathlib
    schema_path = pathlib.Path(__file__).parent / "schema.sql"
    sql = schema_path.read_text()
    async with pool.acquire() as conn:
        await conn.execute(sql)
    logger.info("Schema applied successfully")
