"""
Customer data store with conversation history.
Tracks customers across channels and maintains interaction history.
"""
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict
from models import (
    Ticket, IncomingMessage, AgentResponse, Channel,
    CustomerHistory, SentimentAnalysis
)


class CustomerStore:
    """
    In-memory store for customer data and conversation history.

    In production, this would be backed by PostgreSQL.
    For prototype, using Python dictionaries is sufficient.
    """

    def __init__(self):
        # Primary customer data indexed by customer_id (email)
        self.customers: Dict[str, CustomerHistory] = {}

        # Phone number to email mapping for WhatsApp
        self.phone_to_email: Dict[str, str] = {}

        # Conversation sessions (active conversations)
        self.active_conversations: Dict[str, List[str]] = defaultdict(list)

        # Ticket history
        self.all_tickets: List[Ticket] = []

    def get_or_create_customer(self, customer_id: str, channel: Channel) -> CustomerHistory:
        """
        Get existing customer or create new one.

        Args:
            customer_id: Email or phone number
            channel: Communication channel

        Returns:
            CustomerHistory object
        """
        # Normalize customer ID
        normalized_id = self._normalize_customer_id(customer_id, channel)

        # Get or create customer record
        if normalized_id not in self.customers:
            self.customers[normalized_id] = CustomerHistory(
                customer_id=normalized_id,
                tickets=[],
                total_tickets=0,
                repeat_issues=0,
                average_sentiment=0.5,
                channels_used=[]
            )

        # Track channel usage
        customer = self.customers[normalized_id]
        if channel not in customer.channels_used:
            customer.channels_used.append(channel)

        return customer

    def _normalize_customer_id(self, customer_id: str, channel: Channel) -> str:
        """
        Normalize customer ID across channels.

        For WhatsApp, check if phone is linked to an email.
        Otherwise, use the provided ID.
        """
        if channel == Channel.WHATSAPP and customer_id.startswith('+'):
            # Check if this phone number is linked to an email
            if customer_id in self.phone_to_email:
                return self.phone_to_email[customer_id]

        return customer_id.lower().strip()

    def link_phone_to_email(self, phone: str, email: str):
        """Link WhatsApp phone number to customer email"""
        self.phone_to_email[phone] = email.lower().strip()

        # Merge histories if phone had separate history
        if phone in self.customers:
            phone_history = self.customers[phone]
            email_history = self.get_or_create_customer(email, Channel.EMAIL)

            # Merge tickets
            email_history.tickets.extend(phone_history.tickets)
            email_history.total_tickets += phone_history.total_tickets

            # Merge channels
            for channel in phone_history.channels_used:
                if channel not in email_history.channels_used:
                    email_history.channels_used.append(channel)

            # Remove phone-only record
            del self.customers[phone]

    def add_ticket(self, ticket: Ticket):
        """Add ticket to customer history"""
        customer = self.get_or_create_customer(ticket.customer_id, ticket.channel)

        customer.tickets.append(ticket)
        customer.total_tickets += 1

        # Update average sentiment
        total_sentiment = sum(t.sentiment_score for t in customer.tickets)
        customer.average_sentiment = total_sentiment / len(customer.tickets)

        # Track globally
        self.all_tickets.append(ticket)

    def get_customer_history(self, customer_id: str, channel: Channel) -> CustomerHistory:
        """Get customer's full interaction history"""
        normalized_id = self._normalize_customer_id(customer_id, channel)

        if normalized_id in self.customers:
            return self.customers[normalized_id]

        # Return empty history for new customer
        return CustomerHistory(
            customer_id=normalized_id,
            tickets=[],
            total_tickets=0,
            repeat_issues=0,
            average_sentiment=0.5,
            channels_used=[]
        )

    def get_recent_tickets(
        self,
        customer_id: str,
        channel: Channel,
        limit: int = 5
    ) -> List[Ticket]:
        """Get customer's N most recent tickets"""
        customer = self.get_customer_history(customer_id, channel)
        return customer.tickets[-limit:] if customer.tickets else []

    def is_repeat_customer(self, customer_id: str, channel: Channel) -> bool:
        """Check if customer has contacted support before"""
        customer = self.get_customer_history(customer_id, channel)
        return customer.total_tickets > 0

    def count_repeat_issues(
        self,
        customer_id: str,
        channel: Channel,
        current_category: str,
        lookback_days: int = 30
    ) -> int:
        """
        Count how many times customer has contacted about same category.

        Returns count of similar issues in last N days.
        """
        customer = self.get_customer_history(customer_id, channel)

        if not customer.tickets:
            return 0

        # Get recent tickets in same category
        cutoff_date = datetime.now().timestamp() - (lookback_days * 24 * 60 * 60)

        count = 0
        for ticket in customer.tickets:
            if (ticket.created_at.timestamp() > cutoff_date and
                ticket.category.value == current_category):
                count += 1

        return count

    def get_conversation_context(
        self,
        customer_id: str,
        channel: Channel,
        max_messages: int = 5
    ) -> str:
        """
        Get conversation context for AI agent.

        Returns formatted string of recent conversation history.
        """
        recent_tickets = self.get_recent_tickets(customer_id, channel, max_messages)

        if not recent_tickets:
            return "New customer - no previous interaction history."

        context_parts = []
        context_parts.append(f"Customer has {len(recent_tickets)} previous interaction(s):")

        for i, ticket in enumerate(recent_tickets, 1):
            age_hours = (datetime.now() - ticket.created_at).total_seconds() / 3600

            if age_hours < 24:
                age_str = f"{age_hours:.0f} hours ago"
            else:
                age_str = f"{age_hours/24:.0f} days ago"

            context_parts.append(
                f"{i}. [{age_str}] {ticket.category.value} - "
                f"{ticket.resolution_status} (sentiment: {ticket.sentiment_score:.2f})"
            )

        return "\n".join(context_parts)

    def should_flag_for_escalation(
        self,
        customer_id: str,
        channel: Channel
    ) -> tuple[bool, Optional[str]]:
        """
        Check if customer should be flagged for escalation based on history.

        Returns:
            (should_escalate, reason)
        """
        customer = self.get_customer_history(customer_id, channel)

        # Check 1: Too many recent contacts (5+ in last 7 days)
        recent_week = [
            t for t in customer.tickets
            if (datetime.now() - t.created_at).days < 7
        ]
        if len(recent_week) >= 5:
            return True, "Customer has contacted 5+ times in last 7 days"

        # Check 2: Deteriorating sentiment
        if len(customer.tickets) >= 3:
            recent_sentiments = [t.sentiment_score for t in customer.tickets[-3:]]
            if all(recent_sentiments[i] > recent_sentiments[i+1]
                   for i in range(len(recent_sentiments)-1)):
                return True, "Sentiment deteriorating over last 3 interactions"

        # Check 3: Multiple unresolved tickets
        unresolved = [
            t for t in customer.tickets
            if t.resolution_status in ["open", "escalated"]
        ]
        if len(unresolved) >= 3:
            return True, f"Customer has {len(unresolved)} unresolved tickets"

        # Check 4: Very low average sentiment
        if customer.total_tickets >= 2 and customer.average_sentiment < 0.3:
            return True, f"Average sentiment is very low ({customer.average_sentiment:.2f})"

        return False, None

    def get_stats(self) -> Dict:
        """Get store statistics"""
        return {
            "total_customers": len(self.customers),
            "total_tickets": len(self.all_tickets),
            "phone_mappings": len(self.phone_to_email),
            "customers_with_multiple_channels": sum(
                1 for c in self.customers.values() if len(c.channels_used) > 1
            ),
            "average_tickets_per_customer": (
                len(self.all_tickets) / len(self.customers)
                if self.customers else 0
            )
        }


# Test the customer store
if __name__ == "__main__":
    from models import Category, Priority

    print("Testing CustomerStore...\n")

    store = CustomerStore()

    # Test 1: Create customer
    print("Test 1: Create customer")
    customer = store.get_or_create_customer("user@example.com", Channel.EMAIL)
    print(f"Customer ID: {customer.customer_id}")
    print(f"Total tickets: {customer.total_tickets}\n")

    # Test 2: Add ticket
    print("Test 2: Add ticket")
    ticket = Ticket(
        ticket_id="T001",
        customer_id="user@example.com",
        channel=Channel.EMAIL,
        category=Category.HOW_TO,
        priority=Priority.LOW,
        message_text="How do I reset my password?",
        sentiment_score=0.5,
        resolution_status="resolved"
    )
    store.add_ticket(ticket)

    customer = store.get_customer_history("user@example.com", Channel.EMAIL)
    print(f"Total tickets after adding: {customer.total_tickets}")
    print(f"Average sentiment: {customer.average_sentiment}\n")

    # Test 3: Cross-channel identification
    print("Test 3: Cross-channel identification")
    # Customer contacts via WhatsApp
    whatsapp_customer = store.get_or_create_customer("+1-555-0123", Channel.WHATSAPP)
    print(f"WhatsApp customer ID: {whatsapp_customer.customer_id}")

    # Link phone to email
    store.link_phone_to_email("+1-555-0123", "user@example.com")

    # Now phone number maps to email
    linked_customer = store.get_or_create_customer("+1-555-0123", Channel.WHATSAPP)
    print(f"After linking, customer ID: {linked_customer.customer_id}")
    print(f"Channels used: {[c.value for c in linked_customer.channels_used]}\n")

    # Test 4: Repeat issue detection
    print("Test 4: Repeat issue detection")
    repeat_count = store.count_repeat_issues("user@example.com", Channel.EMAIL, "how-to")
    print(f"Repeat issues in 'how-to' category: {repeat_count}\n")

    # Test 5: Conversation context
    print("Test 5: Conversation context")
    context = store.get_conversation_context("user@example.com", Channel.EMAIL)
    print(f"Context:\n{context}\n")

    # Test 6: Stats
    print("Test 6: Store statistics")
    stats = store.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
