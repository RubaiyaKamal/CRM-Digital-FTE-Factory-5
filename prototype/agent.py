"""
Customer Success FTE Agent - Main Loop
Coordinates all components to process customer messages.
"""
import time
import uuid
from pathlib import Path
from typing import Optional
from models import (
    IncomingMessage, AgentResponse, Channel, Category,
    Priority, Sentiment, SentimentAnalysis, EscalationReason, Ticket
)
from sentiment_analyzer import SentimentAnalyzer
from knowledge_base import KnowledgeBase
from channel_formatter import ChannelFormatter
from escalation_engine import EscalationEngine
from customer_store import CustomerStore
from conversation_manager import ConversationManager


class CustomerSuccessAgent:
    """Main agent that coordinates all components"""

    def __init__(self, kb_path: Optional[Path] = None):
        """
        Initialize the agent with all components.

        Args:
            kb_path: Path to product documentation (optional, will use index if available)
        """
        print("Initializing Customer Success Agent...")

        # Initialize components
        self.sentiment_analyzer = SentimentAnalyzer()
        self.channel_formatter = ChannelFormatter()
        self.escalation_engine = EscalationEngine()

        # Initialize memory components
        self.customer_store = CustomerStore()
        self.conversation_manager = ConversationManager()

        # Initialize knowledge base
        self.kb = KnowledgeBase()
        self._load_knowledge_base(kb_path)

        print("[OK] Agent initialized and ready\n")

    def _load_knowledge_base(self, kb_path: Optional[Path]):
        """Load knowledge base from index or markdown file"""
        # Try loading existing index first
        if self.kb.index_file.exists():
            print("Loading knowledge base from index...")
            self.kb.load_index()
        elif kb_path and kb_path.exists():
            print(f"Building knowledge base from {kb_path}...")
            self.kb.load_from_markdown(kb_path)
        else:
            # Try default path
            default_path = Path(__file__).parent.parent / "context" / "product-docs.md"
            if default_path.exists():
                print(f"Building knowledge base from {default_path}...")
                self.kb.load_from_markdown(default_path)
            else:
                print("⚠️ WARNING: No knowledge base found. Agent will have limited capabilities.")

    def process_message(
        self,
        message: str,
        channel: Channel,
        customer_id: str,
        subject: Optional[str] = None,
        conversation_length: int = 1
    ) -> AgentResponse:
        """
        Process a customer message and generate a response.

        Args:
            message: Customer's message text
            channel: Communication channel (email, whatsapp, web_form)
            customer_id: Customer email or phone number
            subject: Email subject (optional)
            conversation_length: Number of messages in conversation (for escalation logic)

        Returns:
            AgentResponse with formatted response and escalation decision
        """
        start_time = time.time()

        # Create incoming message object
        incoming = IncomingMessage(
            message_id=str(uuid.uuid4()),
            customer_id=customer_id,
            channel=channel,
            message_text=message,
            subject=subject
        )

        print(f"Processing message from {customer_id} via {channel.value}")
        print(f"Message: {message[:100]}{'...' if len(message) > 100 else ''}\n")

        # Memory: Add customer message to conversation
        self.conversation_manager.add_customer_message(customer_id, channel, message)

        # Memory: Get customer history
        customer_history = self.customer_store.get_customer_history(customer_id, channel)
        is_repeat_customer = customer_history.total_tickets > 0

        # Memory: Check if this is a follow-up message
        is_followup, followup_type = self.conversation_manager.is_follow_up(customer_id, channel, message)

        # Memory: Get conversation context
        conversation_context = self.conversation_manager.get_context(customer_id, channel)
        actual_conversation_length = self.conversation_manager.get_conversation_length(customer_id, channel)

        if is_repeat_customer:
            print(f"[MEMORY] Repeat customer: {customer_history.total_tickets} previous tickets")
        if is_followup:
            print(f"[MEMORY] Follow-up message detected: {followup_type}")
        if conversation_context:
            print(f"[MEMORY] Conversation context available ({actual_conversation_length} turns)")

        # Step 1: Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze(message)
        print(f"Sentiment: {sentiment.label.value} (score: {sentiment.score:.2f}, confidence: {sentiment.confidence:.2f})")

        # Step 2: Categorize message
        category = self._categorize_message(message, sentiment)
        print(f"Category: {category.value}")

        # Step 3: Search knowledge base
        kb_results, kb_confidence = self.kb.search_with_fallback(message)
        print(f"Knowledge base: Found {len(kb_results)} results (confidence: {kb_confidence:.2f})")

        # Memory: Check if customer history flags escalation
        history_escalation_needed, history_reason = self.customer_store.should_flag_for_escalation(
            customer_id, channel
        )

        # Step 4: Check if escalation needed
        should_escalate, escalation_reason = self.escalation_engine.should_escalate(
            message=incoming,
            sentiment=sentiment,
            category=category,
            kb_results=kb_results,
            kb_confidence=kb_confidence,
            conversation_length=actual_conversation_length  # Use actual conversation length from memory
        )

        # Override with history-based escalation if needed
        if history_escalation_needed and not should_escalate:
            print(f"[MEMORY] History-based escalation: {history_reason}")
            should_escalate = True
            escalation_reason = EscalationReason(
                trigger="customer_history",
                details=history_reason,
                priority=Priority.HIGH,
                suggested_sla_hours=4
            )

        if should_escalate:
            print(f"[ESCALATION] {escalation_reason.trigger} - {escalation_reason.details}")
            response_text = self._generate_escalation_response(
                customer_id=customer_id,
                escalation_reason=escalation_reason,
                sentiment=sentiment
            )
            priority = escalation_reason.priority
        else:
            print("[OK] AI can handle this")
            # Step 5: Generate response from knowledge base
            response_text = self._generate_response(
                message=message,
                kb_results=kb_results,
                kb_confidence=kb_confidence,
                category=category
            )
            priority = self.escalation_engine.determine_priority(sentiment, category, incoming)

        # Step 6: Format response for channel
        formatted_response = self.channel_formatter.format(
            response=response_text,
            channel=channel,
            customer_name=customer_id
        )

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # milliseconds

        # Create response object
        ticket_id = str(uuid.uuid4())
        agent_response = AgentResponse(
            ticket_id=ticket_id,
            customer_id=customer_id,
            channel=channel,
            response_text=response_text,
            formatted_response=formatted_response,
            should_escalate=should_escalate,
            escalation_reason=escalation_reason,
            sentiment=sentiment,
            category=category,
            priority=priority,
            kb_results=kb_results,
            confidence=kb_confidence,
            processing_time_ms=processing_time
        )

        # Memory: Save agent response to conversation
        self.conversation_manager.add_agent_response(customer_id, channel, response_text)

        # Memory: Create and save ticket to customer history
        ticket = Ticket(
            ticket_id=ticket_id,
            customer_id=customer_id,
            channel=channel,
            category=category,
            priority=priority,
            message_text=message,
            sentiment_score=sentiment.score,
            resolution_status="escalated" if should_escalate else "resolved"
        )
        self.customer_store.add_ticket(ticket)

        print(f"\n[TIME] Processed in {processing_time:.0f}ms")
        print("=" * 60 + "\n")

        return agent_response

    def _categorize_message(self, message: str, sentiment: SentimentAnalysis) -> Category:
        """
        Categorize the message based on keywords.
        (Simple keyword-based categorization for prototype)
        """
        message_lower = message.lower()

        # Technical issues
        technical_keywords = [
            "not working", "error", "bug", "broken", "crash", "slow",
            "integration", "sync", "api", "github", "slack"
        ]
        if any(kw in message_lower for kw in technical_keywords):
            return Category.TECHNICAL

        # Billing
        billing_keywords = [
            "billing", "charge", "invoice", "payment", "refund",
            "subscription", "upgrade", "downgrade", "cost", "price"
        ]
        if any(kw in message_lower for kw in billing_keywords):
            return Category.BILLING

        # Legal/Compliance
        legal_keywords = [
            "gdpr", "lawyer", "legal", "compliance", "audit",
            "data deletion", "dpa", "soc 2"
        ]
        if any(kw in message_lower for kw in legal_keywords):
            return Category.LEGAL

        # How-to
        how_to_keywords = [
            "how do i", "how to", "how can i", "where do i",
            "can i", "is it possible", "what is", "what's"
        ]
        if any(kw in message_lower for kw in how_to_keywords):
            return Category.HOW_TO

        # Feature requests
        feature_keywords = [
            "feature request", "suggestion", "would be great",
            "can you add", "please add", "wish"
        ]
        if any(kw in message_lower for kw in feature_keywords):
            return Category.FEATURE_REQUEST

        # Positive feedback
        if sentiment.label in [Sentiment.VERY_POSITIVE, Sentiment.POSITIVE] and \
           any(kw in message_lower for kw in ["thank", "amazing", "great", "love", "excellent"]):
            return Category.POSITIVE_FEEDBACK

        # Complaints
        if sentiment.label in [Sentiment.ANGRY, Sentiment.VERY_ANGRY]:
            return Category.COMPLAINT

        # Default
        return Category.GENERAL

    def _generate_response(
        self,
        message: str,
        kb_results: list,
        kb_confidence: float,
        category: Category
    ) -> str:
        """Generate response based on knowledge base results"""

        # Handle special cases
        if not kb_results or kb_confidence < 0.3:
            return self._generate_fallback_response(message, category)

        # Build response from KB results
        if category == Category.HOW_TO:
            # For how-to questions, provide direct answer
            response = self._format_how_to_response(kb_results)
        elif category == Category.TECHNICAL:
            # For technical issues, provide troubleshooting steps
            response = self._format_technical_response(kb_results)
        elif category == Category.FEATURE_REQUEST:
            # For feature requests, acknowledge and explain process
            response = "Thank you for the suggestion! We really appreciate feedback from our users.\n\n"
            response += "To submit feature requests, you can:\n"
            response += "1. Visit our community forum at community.techcorp-cloudflow.com\n"
            response += "2. Vote on existing requests or create a new one\n"
            response += "3. Our product team reviews all requests monthly\n\n"
            response += "Is there anything else I can help you with?"
        elif category == Category.POSITIVE_FEEDBACK:
            # For positive feedback, thank warmly
            response = "Thank you so much for the kind words! It really means a lot to our team.\n\n"
            response += "If you're enjoying CloudFlow, we'd love it if you could:\n"
            response += "• Leave a review (helps other teams find us!)\n"
            response += "• Refer colleagues (we have a referral program)\n\n"
            response += "Keep up the great work, and let us know if you ever need anything!"
        else:
            # General response
            response = self._format_general_response(kb_results)

        return response

    def _format_how_to_response(self, kb_results: list) -> str:
        """Format response for how-to questions"""
        best_result = kb_results[0]

        response = f"Here's how to do that:\n\n{best_result.content}\n\n"

        if best_result.url:
            response += f"📚 More details: {best_result.url}\n\n"

        response += "Let me know if you need clarification on any of the steps!"

        return response

    def _format_technical_response(self, kb_results: list) -> str:
        """Format response for technical issues"""
        best_result = kb_results[0]

        response = "Let's troubleshoot this together.\n\n"
        response += f"{best_result.content}\n\n"

        # Add status page check reminder
        response += "If the issue persists, you can also check our status page at status.techcorp-cloudflow.com "
        response += "to see if there are any ongoing incidents.\n\n"

        if best_result.url:
            response += f"📚 Troubleshooting guide: {best_result.url}\n\n"

        response += "Let me know if this resolves the issue or if you need further assistance!"

        return response

    def _format_general_response(self, kb_results: list) -> str:
        """Format general response"""
        best_result = kb_results[0]

        response = f"{best_result.content}\n\n"

        if best_result.url:
            response += f"📚 Learn more: {best_result.url}\n\n"

        response += "Does this answer your question?"

        return response

    def _generate_fallback_response(self, message: str, category: Category) -> str:
        """Generate response when KB doesn't have a good answer"""

        # Check if message is too vague
        if len(message.strip()) < 10 or message.strip().lower() in ["help", "hi", "hello", "question"]:
            return ("I'm here to help! What can I assist you with today?\n\n"
                    "Common topics:\n"
                    "• Password reset\n"
                    "• How to use features\n"
                    "• Billing questions\n"
                    "• Technical issues\n\n"
                    "Or just tell me what you need!")

        # Otherwise, admit we don't have a good answer
        return ("I want to make sure I give you accurate information. "
                "Let me connect you with a specialist on our team who can help with this.\n\n"
                "A team member will reach out within 12 hours via your registered email.")

    def _generate_escalation_response(
        self,
        customer_id: str,
        escalation_reason,
        sentiment: SentimentAnalysis
    ) -> str:
        """Generate response when escalating to human"""

        # Empathy based on sentiment
        if sentiment.score < 0.3:
            opening = "I sincerely apologize for the frustration you're experiencing. "
        else:
            opening = "Thank you for reaching out. "

        # Explain escalation
        if escalation_reason.trigger == "keywords" and "security" in escalation_reason.details.lower():
            # Security incident - urgent
            response = (f"{opening}I'm treating this as a security incident and escalating to our security team immediately.\n\n"
                       f"You'll hear from our team within {escalation_reason.suggested_sla_hours} hours. "
                       f"We take security very seriously and will investigate this thoroughly.")
        elif escalation_reason.trigger == "sentiment":
            # Angry customer - empathetic
            response = (f"{opening}I want to make sure this gets resolved properly for you. "
                       f"I'm connecting you with a specialist on our team right away.\n\n"
                       f"A team member will reach out within {escalation_reason.suggested_sla_hours} hours to personally assist you.")
        else:
            # General escalation
            response = (f"{opening}This requires specialized assistance. "
                       f"I'm escalating your request to our team.\n\n"
                       f"A specialist will reach out within {escalation_reason.suggested_sla_hours} hours at {customer_id}.")

        return response


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("Customer Success Agent - Prototype Test")
    print("=" * 60 + "\n")

    # Initialize agent
    agent = CustomerSuccessAgent()

    # Test cases
    test_cases = [
        {
            "message": "How do I reset my password?",
            "channel": Channel.EMAIL,
            "customer_id": "user@example.com"
        },
        {
            "message": "😡😡😡",
            "channel": Channel.WHATSAPP,
            "customer_id": "+1-555-0123"
        },
        {
            "message": "I need a refund. This is terrible.",
            "channel": Channel.EMAIL,
            "customer_id": "angry@customer.com"
        },
    ]

    for test in test_cases:
        result = agent.process_message(
            message=test["message"],
            channel=test["channel"],
            customer_id=test["customer_id"]
        )

        print(f"Channel: {result.channel.value}")
        print(f"Should Escalate: {result.should_escalate}")
        print(f"Response:\n{result.formatted_response}\n")
        print("=" * 60 + "\n")
