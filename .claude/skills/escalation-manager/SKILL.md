# Escalation Manager Skill

## Skill Definition

**Name:** escalation-manager
**Version:** 1.0.0
**Type:** Agent Feature
**Complexity:** Intermediate

## Description

Detects escalation conditions and routes tickets to human agents with full conversation context.

## Escalation Triggers

```python
def should_escalate(message: str, sentiment: float, context: dict) -> tuple[bool, str]:
    """Determine if escalation needed."""
    
    # Legal language
    if any(word in message.lower() for word in ['lawyer', 'sue', 'legal', 'attorney']):
        return True, "legal_language_detected"
    
    # Pricing inquiries
    if any(word in message.lower() for word in ['price', 'cost', 'pricing', 'how much']):
        return True, "pricing_inquiry"
    
    # Negative sentiment
    if sentiment < 0.3:
        return True, "negative_sentiment"
    
    # Explicit human request
    if 'human' in message.lower() or 'agent' in message.lower():
        return True, "human_requested"
    
    # Cannot find answer
    if context.get('search_attempts', 0) > 2:
        return True, "no_solution_found"
    
    return False, ""

@function_tool
async def escalate_to_human(input: EscalationInput) -> str:
    """Escalate to human support with context."""
    await publish_to_kafka(TOPICS['escalations'], {
        'ticket_id': input.ticket_id,
        'reason': input.reason,
        'urgency': input.urgency,
        'conversation_history': await get_conversation_history(input.ticket_id),
        'customer_info': await get_customer_info(input.ticket_id)
    })
    return f"Escalated to human support: {input.ticket_id}"
```

## Related Skills

- **agent-specialization** - Escalation integration
- **kafka-streaming** - Escalation events
