"""
OpenAI Agents SDK @function_tool definitions for the Customer Success FTE agent.
"""
from __future__ import annotations

import logging
import re
from typing import Optional

import asyncpg
from agents import function_tool

logger = logging.getLogger(__name__)

# Escalation keyword sets (ported from prototype escalation_engine.py)
_FINANCIAL_KW = {"refund", "charge", "billing dispute", "money back", "chargeback", "double charge"}
_LEGAL_KW = {"lawyer", "attorney", "lawsuit", "legal action", "sue", "legal counsel"}
_SECURITY_KW = {"breach", "hacked", "unauthorized", "suspicious activity", "security incident", "compromised", "data leak"}
_COMPLIANCE_KW = {"gdpr", "data deletion", "delete my data", "right to be forgotten", "soc 2", "dpa"}
_ESCALATION_CATEGORIES = {"billing", "legal", "compliance", "sales"}


def _get_pool() -> asyncpg.Pool:
    """Import pool at call time to avoid circular imports."""
    from src.database.connection import _pool
    if _pool is None:
        raise RuntimeError("Database pool not initialized")
    return _pool


@function_tool
async def create_ticket(
    customer_id: str,
    channel: str,
    category: str,
    priority: str,
    message_text: str,
    sentiment_score: float,
    conversation_id: str,
) -> str:
    """
    Create a new support ticket in the database.

    Args:
        customer_id: UUID of the customer
        channel: Channel name (email, whatsapp, web_form)
        category: Ticket category (technical, how-to, billing, etc.)
        priority: Priority level (low, medium, high, urgent, p0)
        message_text: The raw customer message
        sentiment_score: Sentiment score 0.0-1.0 (0=negative, 1=positive)
        conversation_id: UUID of the conversation

    Returns:
        The new ticket UUID as a string.
    """
    pool = _get_pool()
    async with pool.acquire() as conn:
        ticket_id = await conn.fetchval(
            """
            INSERT INTO tickets (conversation_id, customer_id, channel, category, priority,
                                 status, sentiment_score, raw_message)
            VALUES ($1, $2, $3, $4, $5, 'open', $6, $7)
            RETURNING id
            """,
            conversation_id, customer_id, channel, category, priority,
            sentiment_score, message_text,
        )
    logger.info("Created ticket %s for customer %s", ticket_id, customer_id)
    return str(ticket_id)


@function_tool
async def get_customer_history(customer_id: str, limit: int = 5) -> str:
    """
    Retrieve recent ticket history for a customer.

    Args:
        customer_id: UUID of the customer
        limit: Maximum number of recent tickets to return (default 5)

    Returns:
        JSON string with customer's recent tickets and conversation summary.
    """
    import json
    pool = _get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT t.id, t.channel, t.category, t.priority, t.status,
                   t.sentiment_score, t.created_at, t.raw_message
            FROM tickets t
            WHERE t.customer_id = $1
            ORDER BY t.created_at DESC
            LIMIT $2
            """,
            customer_id, limit,
        )
    tickets = [dict(r) for r in rows]
    for t in tickets:
        t["id"] = str(t["id"])
        t["created_at"] = t["created_at"].isoformat() if t["created_at"] else None
    return json.dumps({"customer_id": customer_id, "recent_tickets": tickets})


@function_tool
async def search_knowledge_base(query: str, limit: int = 3) -> str:
    """
    Search the knowledge base using semantic similarity (pgvector).

    Args:
        query: The search query text
        limit: Maximum number of results to return (default 3)

    Returns:
        JSON string with relevant knowledge base articles.
    """
    import json
    from src.config import settings

    pool = _get_pool()

    # Generate embedding for the query
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=query,
        )
        embedding = response.data[0].embedding
    except Exception as e:
        logger.warning("Embedding generation failed: %s — falling back to keyword search", e)
        embedding = None

    async with pool.acquire() as conn:
        if embedding is not None:
            rows = await conn.fetch(
                """
                SELECT id, title, content, section, url,
                       1 - (embedding <=> CAST($1 AS vector)) AS similarity
                FROM knowledge_base
                ORDER BY embedding <=> CAST($1 AS vector)
                LIMIT $2
                """,
                str(embedding), limit,
            )
        else:
            # Fallback: simple ILIKE keyword search
            rows = await conn.fetch(
                """
                SELECT id, title, content, section, url, 0.5 AS similarity
                FROM knowledge_base
                WHERE content ILIKE $1 OR title ILIKE $1
                LIMIT $2
                """,
                f"%{query}%", limit,
            )

    results = [dict(r) for r in rows]
    for r in results:
        r["id"] = str(r["id"])
    return json.dumps({"query": query, "results": results})


@function_tool
async def escalate_to_human(
    ticket_id: str,
    reason: str,
    priority: str,
    suggested_sla_hours: float,
    trigger: str,
) -> str:
    """
    Escalate a ticket to a human agent.

    Args:
        ticket_id: UUID of the ticket to escalate
        reason: Human-readable explanation of why escalation is needed
        priority: Escalation priority (low, medium, high, urgent, p0)
        suggested_sla_hours: Suggested response time in hours
        trigger: What triggered escalation (sentiment, keywords, category, etc.)

    Returns:
        Confirmation string with escalation details.
    """
    import json
    pool = _get_pool()
    escalation_data = {
        "trigger": trigger,
        "reason": reason,
        "priority": priority,
        "suggested_sla_hours": suggested_sla_hours,
    }
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE tickets
            SET status = 'escalated',
                escalation_reason = $1::jsonb,
                priority = $2
            WHERE id = $3
            """,
            json.dumps(escalation_data), priority, ticket_id,
        )
    logger.info("Ticket %s escalated: %s (priority=%s)", ticket_id, trigger, priority)
    return f"Escalated ticket {ticket_id} with priority {priority}. SLA: {suggested_sla_hours}h"


@function_tool
async def send_response(
    ticket_id: str,
    conversation_id: str,
    response_text: str,
    channel: str,
    customer_identifier: str,
) -> str:
    """
    Store the agent's response and mark the ticket as resolved.

    Args:
        ticket_id: UUID of the ticket
        conversation_id: UUID of the conversation
        response_text: The response text to send to the customer
        channel: Channel to send via (email, whatsapp, web_form)
        customer_identifier: Customer email or phone for delivery

    Returns:
        Confirmation string.
    """
    pool = _get_pool()
    async with pool.acquire() as conn:
        # Store agent message
        await conn.execute(
            """
            INSERT INTO messages (conversation_id, role, content, channel, metadata)
            VALUES ($1, 'agent', $2, $3, '{"sent_by": "ai_agent"}')
            """,
            conversation_id, response_text, channel,
        )
        # Mark ticket resolved
        await conn.execute(
            "UPDATE tickets SET status = 'resolved' WHERE id = $1",
            ticket_id,
        )
    logger.info("Response stored for ticket %s, channel=%s", ticket_id, channel)
    return f"Response delivered to {customer_identifier} via {channel}"


def detect_escalation_need(message: str, category: str, sentiment_score: float) -> tuple[bool, str, str, float]:
    """
    Pure-function escalation detection (no DB required).
    Returns (should_escalate, trigger, reason, sla_hours).
    """
    msg = message.lower()

    if any(kw in msg for kw in _SECURITY_KW):
        return True, "keywords", "Security incident detected", 0.25

    if any(kw in msg for kw in _LEGAL_KW):
        return True, "keywords", "Legal language detected", 4.0

    if any(kw in msg for kw in _FINANCIAL_KW):
        return True, "keywords", "Financial dispute detected", 4.0

    if any(kw in msg for kw in _COMPLIANCE_KW):
        return True, "keywords", "Compliance request detected", 4.0

    if category.lower() in _ESCALATION_CATEGORIES:
        return True, "category", f"Category '{category}' requires human handling", 4.0

    if sentiment_score < 0.3:
        priority_level = "urgent" if sentiment_score < 0.2 else "high"
        return True, "sentiment", f"Very negative sentiment (score={sentiment_score:.2f})", 1.0

    human_requests = ["speak to a human", "talk to a person", "real person", "human agent"]
    if any(req in msg for req in human_requests):
        return True, "explicit_request", "Customer requested human agent", 4.0

    return False, "", "", 0.0
