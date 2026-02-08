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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(webhooks.router)
app.include_router(tickets.router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "env": settings.app_env}


@app.get("/webhooks/web_form/stream/{session_id}")
async def web_form_stream(session_id: str):
    """SSE endpoint for real-time web form responses."""
    adapter = WebFormAdapter()
    return StreamingResponse(
        adapter.sse_stream(session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
