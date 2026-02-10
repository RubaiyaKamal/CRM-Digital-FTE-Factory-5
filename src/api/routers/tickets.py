"""
Ticket and conversation management endpoints.
"""
from __future__ import annotations

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from src.database.connection import get_db_pool

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["tickets"])


class TicketOut(BaseModel):
    id: str
    customer_id: str
    channel: str
    category: str
    priority: str
    status: str
    sentiment_score: Optional[float]
    created_at: str
    raw_message: Optional[str]


class ConversationOut(BaseModel):
    id: str
    customer_id: str
    channel: str
    status: str
    subject: Optional[str]
    created_at: str
    message_count: int


class CustomerOut(BaseModel):
    id: str
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    created_at: str
    ticket_count: int


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    channel: str
    created_at: str


@router.get("/tickets", response_model=List[TicketOut])
async def list_tickets(
    status: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    """List tickets with optional filtering."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        where_clauses = []
        params = []
        idx = 1
        if status:
            where_clauses.append(f"status = ${idx}")
            params.append(status)
            idx += 1
        if channel:
            where_clauses.append(f"channel = ${idx}")
            params.append(channel)
            idx += 1
        where = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        params.extend([limit, offset])
        rows = await conn.fetch(
            f"""
            SELECT id, customer_id, channel, category, priority, status,
                   sentiment_score, created_at, raw_message
            FROM tickets
            {where}
            ORDER BY created_at DESC
            LIMIT ${idx} OFFSET ${idx + 1}
            """,
            *params,
        )
    return [
        TicketOut(
            id=str(r["id"]),
            customer_id=str(r["customer_id"]),
            channel=r["channel"],
            category=r["category"],
            priority=r["priority"],
            status=r["status"],
            sentiment_score=r["sentiment_score"],
            created_at=r["created_at"].isoformat(),
            raw_message=r["raw_message"],
        )
        for r in rows
    ]


@router.get("/tickets/{ticket_id}", response_model=TicketOut)
async def get_ticket(ticket_id: str):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM tickets WHERE id = $1", ticket_id
        )
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketOut(
        id=str(row["id"]),
        customer_id=str(row["customer_id"]),
        channel=row["channel"],
        category=row["category"],
        priority=row["priority"],
        status=row["status"],
        sentiment_score=row["sentiment_score"],
        created_at=row["created_at"].isoformat(),
        raw_message=row["raw_message"],
    )


@router.get("/conversations", response_model=List[ConversationOut])
async def list_conversations(
    channel: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        where = ""
        params = []
        conditions = []
        if channel:
            conditions.append(f"c.channel = ${len(params) + 1}")
            params.append(channel)
        if status:
            conditions.append(f"c.status = ${len(params) + 1}")
            params.append(status)
        if conditions:
            where = "WHERE " + " AND ".join(conditions)
        params.append(limit)
        rows = await conn.fetch(
            f"""
            SELECT c.id, c.customer_id, c.channel, c.status, c.subject, c.created_at,
                   COUNT(m.id)::int AS message_count
            FROM conversations c
            LEFT JOIN messages m ON m.conversation_id = c.id
            {where}
            GROUP BY c.id
            ORDER BY c.created_at DESC
            LIMIT ${len(params)}
            """,
            *params,
        )
    return [
        ConversationOut(
            id=str(r["id"]),
            customer_id=str(r["customer_id"]),
            channel=r["channel"],
            status=r["status"],
            subject=r["subject"],
            created_at=r["created_at"].isoformat(),
            message_count=r["message_count"],
        )
        for r in rows
    ]


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageOut])
async def get_conversation_messages(conversation_id: str):
    """Get all messages in a conversation."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, conversation_id, role, content, channel, created_at
            FROM messages
            WHERE conversation_id = $1
            ORDER BY created_at ASC
            """,
            conversation_id,
        )
    return [
        MessageOut(
            id=str(r["id"]),
            conversation_id=str(r["conversation_id"]),
            role=r["role"],
            content=r["content"],
            channel=r["channel"],
            created_at=r["created_at"].isoformat(),
        )
        for r in rows
    ]


@router.post("/conversations/{conversation_id}/resolve")
async def resolve_conversation(conversation_id: str):
    """Mark a conversation and all its tickets as resolved."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Update conversation status
        await conn.execute(
            """
            UPDATE conversations
            SET status = 'resolved'
            WHERE id = $1
            """,
            conversation_id,
        )

        # Update all related tickets to resolved
        await conn.execute(
            """
            UPDATE tickets
            SET status = 'resolved'
            WHERE conversation_id = $1 AND status != 'resolved'
            """,
            conversation_id,
        )

    logger.info("Conversation %s marked as resolved", conversation_id)
    return {"success": True, "conversation_id": conversation_id, "status": "resolved"}


@router.get("/customers", response_model=List[CustomerOut])
async def list_customers(
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    """List customers with ticket counts."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT c.id, c.name, c.email, c.phone, c.created_at,
                   COUNT(DISTINCT t.id)::int AS ticket_count
            FROM customers c
            LEFT JOIN tickets t ON t.customer_id = c.id
            GROUP BY c.id
            ORDER BY c.created_at DESC
            LIMIT $1 OFFSET $2
            """,
            limit,
            offset,
        )
    return [
        CustomerOut(
            id=str(r["id"]),
            name=r["name"],
            email=r["email"],
            phone=r["phone"],
            created_at=r["created_at"].isoformat(),
            ticket_count=r["ticket_count"],
        )
        for r in rows
    ]
