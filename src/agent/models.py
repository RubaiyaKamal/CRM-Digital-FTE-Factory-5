"""
Pydantic models for the Customer Success FTE agent (ported from prototype).
"""
from __future__ import annotations

from enum import Enum
from typing import Optional, List, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    P0 = "p0"


class Category(str, Enum):
    TECHNICAL = "technical"
    HOW_TO = "how-to"
    BILLING = "billing"
    SALES = "sales"
    LEGAL = "legal"
    COMPLIANCE = "compliance"
    FEATURE_REQUEST = "feature-request"
    POSITIVE_FEEDBACK = "positive-feedback"
    COMPLAINT = "complaint"
    ONBOARDING = "onboarding"
    GENERAL = "general"


class TicketStatus(str, Enum):
    OPEN = "open"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class IncomingWebhook(BaseModel):
    """Normalised webhook payload after channel parsing."""
    message_id: str
    customer_identifier: str          # email or phone
    identifier_type: str              # 'email' | 'phone' | 'web_session'
    channel: Channel
    subject: Optional[str] = None
    message_text: str
    raw_payload: Dict[str, Any] = Field(default_factory=dict)
    received_at: datetime = Field(default_factory=datetime.utcnow)


class AgentTask(BaseModel):
    """Task passed from Kafka consumer to the agent."""
    ticket_id: str
    conversation_id: str
    customer_id: str
    customer_identifier: str
    channel: Channel
    message_text: str
    subject: Optional[str] = None
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)


class AgentResult(BaseModel):
    """Output from the agent after processing a task."""
    ticket_id: str
    customer_id: str
    channel: Channel
    response_text: str
    should_escalate: bool
    escalation_reason: Optional[str] = None
    escalation_priority: Optional[Priority] = None
    category: Category = Category.GENERAL
    priority: Priority = Priority.LOW
    sentiment_score: float = 0.5
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    latency_ms: float = 0.0
    tokens_used: int = 0


class KafkaMessage(BaseModel):
    """Envelope for Kafka messages."""
    version: str = "1.0"
    topic: str
    payload: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
