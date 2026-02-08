"""
Data models for Customer Success FTE prototype.
"""
from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class Channel(str, Enum):
    """Communication channel"""
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"


class Priority(str, Enum):
    """Ticket priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    P0 = "p0"


class Category(str, Enum):
    """Ticket categories"""
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


class Sentiment(str, Enum):
    """Customer sentiment"""
    VERY_POSITIVE = "very-positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    CONFUSED = "confused"
    FRUSTRATED = "frustrated"
    ANGRY = "angry"
    VERY_ANGRY = "very-angry"


class IncomingMessage(BaseModel):
    """Incoming customer message"""
    message_id: str
    customer_id: str  # email or phone
    channel: Channel
    message_text: str
    subject: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class SentimentAnalysis(BaseModel):
    """Sentiment analysis result"""
    score: float = Field(..., ge=0.0, le=1.0, description="0=very negative, 1=very positive")
    confidence: float = Field(..., ge=0.0, le=1.0)
    label: Sentiment
    detected_emotions: List[str] = Field(default_factory=list)


class KnowledgeBaseResult(BaseModel):
    """Knowledge base search result"""
    content: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    source_section: str
    url: Optional[str] = None


class EscalationReason(BaseModel):
    """Reason for escalation"""
    trigger: str  # sentiment | keywords | category | confidence | conversation_length
    details: str
    priority: Priority
    suggested_sla_hours: float


class AgentResponse(BaseModel):
    """Agent's response to customer"""
    ticket_id: str
    customer_id: str
    channel: Channel
    response_text: str
    formatted_response: str  # Channel-formatted version
    should_escalate: bool
    escalation_reason: Optional[EscalationReason] = None
    sentiment: SentimentAnalysis
    category: Category
    priority: Priority
    kb_results: List[KnowledgeBaseResult] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    processing_time_ms: float
    timestamp: datetime = Field(default_factory=datetime.now)


class Ticket(BaseModel):
    """Support ticket"""
    ticket_id: str
    customer_id: str
    channel: Channel
    category: Category
    priority: Priority
    message_text: str
    sentiment_score: float
    resolution_status: str  # open | resolved | escalated
    created_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


class CustomerHistory(BaseModel):
    """Customer interaction history"""
    customer_id: str
    tickets: List[Ticket] = Field(default_factory=list)
    total_tickets: int = 0
    repeat_issues: int = 0
    average_sentiment: float = 0.5
    channels_used: List[Channel] = Field(default_factory=list)
