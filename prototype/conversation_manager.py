"""
Conversation manager for multi-turn interactions.
Handles conversation state and context across multiple messages.
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from models import IncomingMessage, AgentResponse, Channel


class Message:
    """Single message in a conversation"""
    def __init__(self, sender: str, text: str, timestamp: datetime):
        self.sender = sender  # "customer" or "agent"
        self.text = text
        self.timestamp = timestamp


class Conversation:
    """Represents a single conversation thread"""
    def __init__(self, customer_id: str, channel: Channel):
        self.customer_id = customer_id
        self.channel = channel
        self.messages: List[Message] = []
        self.started_at = datetime.now()
        self.last_message_at = datetime.now()
        self.is_active = True
        self.turn_count = 0

    def add_message(self, sender: str, text: str):
        """Add a message to the conversation"""
        message = Message(sender, text, datetime.now())
        self.messages.append(message)
        self.last_message_at = datetime.now()
        self.turn_count += 1

    def get_context(self, max_messages: int = 5) -> str:
        """Get formatted conversation context for AI"""
        if not self.messages:
            return ""

        # Get last N messages
        recent = self.messages[-max_messages:]

        context_parts = ["Recent conversation:"]
        for msg in recent:
            sender_label = "Customer" if msg.sender == "customer" else "Agent"
            context_parts.append(f"{sender_label}: {msg.text}")

        return "\n".join(context_parts)

    def age_minutes(self) -> float:
        """Get conversation age in minutes"""
        return (datetime.now() - self.started_at).total_seconds() / 60

    def idle_minutes(self) -> float:
        """Get minutes since last message"""
        return (datetime.now() - self.last_message_at).total_seconds() / 60


class ConversationManager:
    """
    Manages active conversations for all customers.

    Conversations expire after 30 minutes of inactivity.
    """

    def __init__(self, timeout_minutes: int = 30):
        # Active conversations indexed by customer_id
        self.conversations: Dict[str, Conversation] = {}

        # Timeout for conversation expiry
        self.timeout_minutes = timeout_minutes

    def get_or_create_conversation(
        self,
        customer_id: str,
        channel: Channel
    ) -> Conversation:
        """
        Get existing conversation or create new one.

        If conversation exists but is on different channel, creates new conversation
        (customer switched channels).
        """
        key = self._make_key(customer_id, channel)

        # Check if conversation exists and is still active
        if key in self.conversations:
            conv = self.conversations[key]

            # Check if expired
            if conv.idle_minutes() > self.timeout_minutes:
                # Expired - archive and start new
                conv.is_active = False
                del self.conversations[key]
            else:
                return conv

        # Create new conversation
        conv = Conversation(customer_id, channel)
        self.conversations[key] = conv
        return conv

    def add_customer_message(
        self,
        customer_id: str,
        channel: Channel,
        message: str
    ):
        """Add customer message to conversation"""
        conv = self.get_or_create_conversation(customer_id, channel)
        conv.add_message("customer", message)

    def add_agent_response(
        self,
        customer_id: str,
        channel: Channel,
        response: str
    ):
        """Add agent response to conversation"""
        conv = self.get_or_create_conversation(customer_id, channel)
        conv.add_message("agent", response)

    def get_conversation_length(
        self,
        customer_id: str,
        channel: Channel
    ) -> int:
        """Get number of turns in current conversation"""
        key = self._make_key(customer_id, channel)

        if key in self.conversations:
            return self.conversations[key].turn_count

        return 0

    def get_context(
        self,
        customer_id: str,
        channel: Channel,
        max_messages: int = 5
    ) -> str:
        """Get conversation context for AI agent"""
        key = self._make_key(customer_id, channel)

        if key in self.conversations:
            return self.conversations[key].get_context(max_messages)

        return ""

    def is_follow_up(
        self,
        customer_id: str,
        channel: Channel,
        message: str
    ) -> tuple[bool, Optional[str]]:
        """
        Determine if message is a follow-up to previous conversation.

        Returns:
            (is_follow_up, follow_up_type)

        Follow-up types:
        - "thanks" - Customer thanking agent
        - "clarification" - Customer asking for clarification
        - "confirmation" - Customer confirming something worked
        - "continuation" - Customer continuing same topic
        """
        conv = self.get_or_create_conversation(customer_id, channel)

        # Must have at least one prior message
        if conv.turn_count == 0:
            return False, None

        # Check if very recent (< 5 minutes)
        if conv.idle_minutes() > 5:
            return False, None

        message_lower = message.lower().strip()

        # Check for thanks
        thanks_phrases = ["thanks", "thank you", "thx", "ty", "appreciate"]
        if any(phrase in message_lower for phrase in thanks_phrases):
            return True, "thanks"

        # Check for confirmation
        confirm_phrases = ["worked", "fixed", "solved", "that did it", "got it"]
        if any(phrase in message_lower for phrase in confirm_phrases):
            return True, "confirmation"

        # Check for clarification
        clarify_phrases = ["what do you mean", "i don't understand", "can you explain",
                          "unclear", "confused", "how"]
        if any(phrase in message_lower for phrase in clarify_phrases):
            return True, "clarification"

        # If message is very short and recent, likely continuation
        if len(message.split()) < 5 and conv.idle_minutes() < 2:
            return True, "continuation"

        return False, None

    def _make_key(self, customer_id: str, channel: Channel) -> str:
        """Create unique key for conversation"""
        return f"{customer_id.lower()}:{channel.value}"

    def cleanup_expired(self):
        """Remove expired conversations"""
        expired_keys = []

        for key, conv in self.conversations.items():
            if conv.idle_minutes() > self.timeout_minutes:
                conv.is_active = False
                expired_keys.append(key)

        for key in expired_keys:
            del self.conversations[key]

        return len(expired_keys)

    def get_stats(self) -> Dict:
        """Get conversation statistics"""
        if not self.conversations:
            return {
                "active_conversations": 0,
                "average_turns": 0,
                "average_age_minutes": 0
            }

        total_turns = sum(c.turn_count for c in self.conversations.values())
        total_age = sum(c.age_minutes() for c in self.conversations.values())

        return {
            "active_conversations": len(self.conversations),
            "average_turns": total_turns / len(self.conversations),
            "average_age_minutes": total_age / len(self.conversations)
        }


# Test the conversation manager
if __name__ == "__main__":
    import time

    print("Testing ConversationManager...\n")

    manager = ConversationManager(timeout_minutes=30)

    # Test 1: Create conversation
    print("Test 1: Create conversation")
    customer_id = "user@example.com"
    channel = Channel.EMAIL

    manager.add_customer_message(customer_id, channel, "How do I reset my password?")
    length = manager.get_conversation_length(customer_id, channel)
    print(f"Conversation length after customer message: {length}")

    manager.add_agent_response(customer_id, channel, "Here's how to reset your password...")
    length = manager.get_conversation_length(customer_id, channel)
    print(f"Conversation length after agent response: {length}\n")

    # Test 2: Get context
    print("Test 2: Get conversation context")
    context = manager.get_context(customer_id, channel)
    print(f"Context:\n{context}\n")

    # Test 3: Multi-turn conversation
    print("Test 3: Multi-turn conversation")
    manager.add_customer_message(customer_id, channel, "I still don't see the reset link")
    manager.add_agent_response(customer_id, channel, "Check your spam folder")
    manager.add_customer_message(customer_id, channel, "Found it! Thanks!")

    length = manager.get_conversation_length(customer_id, channel)
    print(f"Conversation length after 3 turns: {length}")

    context = manager.get_context(customer_id, channel, max_messages=10)
    print(f"\nFull conversation:\n{context}\n")

    # Test 4: Follow-up detection
    print("Test 4: Follow-up detection")

    test_messages = [
        ("Thanks!", "thanks"),
        ("That worked!", "confirmation"),
        ("I don't understand", "clarification"),
        ("ok", "continuation"),
    ]

    for msg, expected_type in test_messages:
        manager.add_customer_message(customer_id, channel, msg)
        is_followup, followup_type = manager.is_follow_up(customer_id, channel, msg)
        print(f"Message: '{msg}' -> Follow-up: {is_followup}, Type: {followup_type}")

    print()

    # Test 5: Channel switching
    print("Test 5: Channel switching")
    whatsapp_channel = Channel.WHATSAPP

    manager.add_customer_message(customer_id, whatsapp_channel, "Quick question")
    email_length = manager.get_conversation_length(customer_id, Channel.EMAIL)
    whatsapp_length = manager.get_conversation_length(customer_id, whatsapp_channel)

    print(f"Email conversation length: {email_length}")
    print(f"WhatsApp conversation length: {whatsapp_length}")
    print("(Separate conversations per channel)\n")

    # Test 6: Stats
    print("Test 6: Conversation statistics")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value:.1f}" if isinstance(value, float) else f"  {key}: {value}")
