"""
Escalation decision engine.
Determines when AI should escalate to human agents.
"""
import re
from typing import Optional, List
from models import (
    IncomingMessage, SentimentAnalysis, KnowledgeBaseResult,
    EscalationReason, Priority, Category, Channel
)


class EscalationEngine:
    """Decides when to escalate to human agents"""

    def __init__(self):
        # Immediate escalation keywords
        self.financial_keywords = [
            "refund", "charge", "billing dispute", "money back",
            "chargeback", "double charge", "incorrect charge"
        ]

        self.legal_keywords = [
            "lawyer", "attorney", "lawsuit", "legal action", "sue",
            "legal counsel", "legal team"
        ]

        self.security_keywords = [
            "breach", "hacked", "unauthorized", "suspicious activity",
            "security incident", "compromised", "data leak"
        ]

        self.compliance_keywords = [
            "gdpr", "data deletion", "delete my data", "right to be forgotten",
            "soc 2", "audit", "dpa", "data processing", "compliance"
        ]

        # Categories that always escalate
        self.escalation_categories = [
            Category.BILLING,
            Category.LEGAL,
            Category.COMPLIANCE,
            Category.SALES  # Pricing negotiations
        ]

    def should_escalate(
        self,
        message: IncomingMessage,
        sentiment: SentimentAnalysis,
        category: Category,
        kb_results: List[KnowledgeBaseResult],
        kb_confidence: float,
        conversation_length: int = 1
    ) -> tuple[bool, Optional[EscalationReason]]:
        """
        Determine if ticket should be escalated.

        Returns:
            (should_escalate, escalation_reason)
        """
        # Check 1: Severe negative sentiment
        if sentiment.score < 0.3:
            return True, EscalationReason(
                trigger="sentiment",
                details=f"Negative sentiment detected (score: {sentiment.score:.2f}). Customer appears {sentiment.label.value}.",
                priority=Priority.URGENT if sentiment.score < 0.2 else Priority.HIGH,
                suggested_sla_hours=1.0
            )

        # Check 2: Keyword triggers (financial/legal/security/compliance)
        keyword_match = self._check_escalation_keywords(message.message_text)
        if keyword_match:
            trigger_type, keywords_found = keyword_match
            priority = Priority.P0 if trigger_type == "security" else Priority.HIGH

            return True, EscalationReason(
                trigger="keywords",
                details=f"{trigger_type.title()} keywords detected: {', '.join(keywords_found)}",
                priority=priority,
                suggested_sla_hours=0.25 if priority == Priority.P0 else 4.0
            )

        # Check 3: Category-based escalation
        if category in self.escalation_categories:
            return True, EscalationReason(
                trigger="category",
                details=f"Category '{category.value}' requires human handling",
                priority=Priority.HIGH,
                suggested_sla_hours=4.0
            )

        # Check 4: Low knowledge base confidence
        if kb_confidence < 0.5 and conversation_length > 1:
            return True, EscalationReason(
                trigger="confidence",
                details=f"Unable to find relevant answer (confidence: {kb_confidence:.2f})",
                priority=Priority.MEDIUM,
                suggested_sla_hours=12.0
            )

        # Check 5: Conversation too long without resolution
        if conversation_length > 6:
            return True, EscalationReason(
                trigger="conversation_length",
                details=f"Conversation has reached {conversation_length} messages without resolution",
                priority=Priority.HIGH,
                suggested_sla_hours=2.0
            )

        # Check 6: Customer explicitly requests human
        if self._requests_human(message.message_text):
            return True, EscalationReason(
                trigger="explicit_request",
                details="Customer explicitly requested to speak with a human",
                priority=Priority.MEDIUM,
                suggested_sla_hours=4.0
            )

        # Check 7: Empty or very vague message
        if self._is_too_vague(message.message_text) and kb_confidence < 0.3:
            # Don't escalate immediately - ask clarifying question first
            # But if this is the 2nd vague message, escalate
            if conversation_length > 1:
                return True, EscalationReason(
                    trigger="unclear_request",
                    details="Unable to understand customer request after clarification attempt",
                    priority=Priority.LOW,
                    suggested_sla_hours=24.0
                )

        # No escalation needed
        return False, None

    def _check_escalation_keywords(self, message: str) -> Optional[tuple[str, List[str]]]:
        """
        Check for escalation keyword triggers.

        Returns:
            (trigger_type, keywords_found) or None
        """
        message_lower = message.lower()

        # Check each keyword category
        categories = {
            "security": self.security_keywords,
            "legal": self.legal_keywords,
            "financial": self.financial_keywords,
            "compliance": self.compliance_keywords
        }

        for trigger_type, keywords in categories.items():
            found = [kw for kw in keywords if kw in message_lower]
            if found:
                return trigger_type, found

        return None

    def _requests_human(self, message: str) -> bool:
        """Check if customer explicitly requests to speak with a human"""
        message_lower = message.lower()

        human_requests = [
            "speak to a human",
            "talk to a person",
            "speak with someone",
            "connect me with",
            "real person",
            "actual person",
            "human agent",
            "human support",
            "speak to your team",
            "talk to your team"
        ]

        return any(req in message_lower for req in human_requests)

    def _is_too_vague(self, message: str) -> bool:
        """Check if message is too vague to handle"""
        message_stripped = message.strip().lower()

        # Very short messages that are vague
        vague_messages = ["help", "hi", "hello", "hey", "question", "problem", "issue"]

        # Empty or only punctuation/emojis
        if not message_stripped or len(message_stripped) < 3:
            return True

        # Single word vague requests
        if message_stripped in vague_messages:
            return True

        return False

    def determine_priority(
        self,
        sentiment: SentimentAnalysis,
        category: Category,
        message: IncomingMessage
    ) -> Priority:
        """Determine ticket priority based on multiple factors"""

        # P0: Security incidents
        if any(kw in message.message_text.lower() for kw in self.security_keywords):
            return Priority.P0

        # Urgent: Very negative sentiment or legal threats
        if sentiment.score < 0.2 or any(kw in message.message_text.lower() for kw in self.legal_keywords):
            return Priority.URGENT

        # High: Billing disputes, negative sentiment, or important categories
        if (category in [Category.BILLING, Category.COMPLIANCE, Category.SALES] or
            sentiment.score < 0.3):
            return Priority.HIGH

        # Medium: Technical issues, moderate negative sentiment
        if category == Category.TECHNICAL or sentiment.label in ["frustrated", "confused"]:
            return Priority.MEDIUM

        # Low: How-to, feature requests, positive feedback
        return Priority.LOW


# Test escalation engine
if __name__ == "__main__":
    from models import Sentiment

    engine = EscalationEngine()

    test_cases = [
        {
            "message": "How do I reset my password?",
            "sentiment_score": 0.5,
            "sentiment_label": Sentiment.NEUTRAL,
            "category": Category.HOW_TO,
            "kb_confidence": 0.9,
            "expected": False
        },
        {
            "message": "I need a REFUND. This is terrible!",
            "sentiment_score": 0.15,
            "sentiment_label": Sentiment.VERY_ANGRY,
            "category": Category.BILLING,
            "kb_confidence": 0.8,
            "expected": True
        },
        {
            "message": "We've been hacked! Suspicious login from Russia!",
            "sentiment_score": 0.2,
            "sentiment_label": Sentiment.ANGRY,
            "category": Category.TECHNICAL,
            "kb_confidence": 0.7,
            "expected": True
        },
        {
            "message": "help",
            "sentiment_score": 0.5,
            "sentiment_label": Sentiment.NEUTRAL,
            "category": Category.GENERAL,
            "kb_confidence": 0.2,
            "expected": False  # First time, ask clarification
        },
    ]

    print("=" * 60)
    print("Escalation Engine Test")
    print("=" * 60)

    for i, test in enumerate(test_cases, 1):
        message = IncomingMessage(
            message_id=f"test-{i}",
            customer_id="test@example.com",
            channel=Channel.EMAIL,
            message_text=test["message"]
        )

        sentiment = SentimentAnalysis(
            score=test["sentiment_score"],
            confidence=0.8,
            label=test["sentiment_label"],
            detected_emotions=[]
        )

        should_escalate, reason = engine.should_escalate(
            message=message,
            sentiment=sentiment,
            category=test["category"],
            kb_results=[],
            kb_confidence=test["kb_confidence"],
            conversation_length=1
        )

        print(f"\nTest {i}: {test['message']}")
        print(f"Expected escalation: {test['expected']}")
        print(f"Actual escalation: {should_escalate}")

        if should_escalate:
            print(f"Reason: {reason.trigger} - {reason.details}")
            print(f"Priority: {reason.priority.value}")

        status = "✅ PASS" if should_escalate == test["expected"] else "❌ FAIL"
        print(status)
