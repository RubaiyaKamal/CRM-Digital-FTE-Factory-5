"""
FastAPI application entry point with lifespan management.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

from src.api.routers import webhooks, tickets
from src.channels.web_form import WebFormAdapter
from src.config import settings
from src.database.connection import create_pool, close_pool, apply_schema
from src.kafka_client import get_producer, stop_producer

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
logger = logging.getLogger(__name__)
logging.basicConfig(level=settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("Starting CRM FTE API (env=%s)", settings.app_env)

    # Init DB pool
    from src.database import connection as db_module
    db_module._pool = await create_pool()
    await apply_schema(db_module._pool)

    # Init Kafka producer
    await get_producer()

    logger.info("All services ready")
    yield

    # Shutdown
    await stop_producer()
    await close_pool()
    logger.info("Shutdown complete")


app = FastAPI(
    title="CRM Digital FTE Factory",
    version="1.0.0",
    description="Multi-channel AI Customer Success agent",
    lifespan=lifespan,
)

# CORS for React web form
# Note: allow_credentials=True is incompatible with allow_origins=["*"] per CORS spec.
# Use explicit origins. Update CORS_ORIGINS env var for production.
_cors_origins = [o.strip() for o in (settings.cors_origins or "http://localhost:3000,http://localhost:8000").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type"],
)

# Routers
app.include_router(webhooks.router)
app.include_router(tickets.router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "env": settings.app_env}


@app.get("/webhooks/web_form/stream/{conversation_id}")
async def web_form_stream(conversation_id: str):
    """SSE endpoint: polls DB for agent reply to a conversation."""
    import asyncio
    import json
    import time

    from src.database.connection import get_db_pool

    async def generate():
        yield 'data: {"type": "connected"}\n\n'

        pool = await get_db_pool()
        deadline = time.monotonic() + 90  # wait up to 90s

        while time.monotonic() < deadline:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT content FROM messages
                    WHERE conversation_id = $1 AND role = 'agent'
                    ORDER BY created_at DESC LIMIT 1
                    """,
                    conversation_id,
                )
            if row:
                yield f'data: {json.dumps({"type": "response", "content": row["content"]})}\n\n'
                return
            yield 'data: {"type": "heartbeat"}\n\n'
            await asyncio.sleep(2)

        yield 'data: {"type": "timeout"}\n\n'

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
