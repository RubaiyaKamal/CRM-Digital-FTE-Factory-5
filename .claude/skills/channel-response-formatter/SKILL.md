# Channel Response Formatter Skill

## Skill Definition

**Name:** channel-response-formatter
**Version:** 1.0.0
**Type:** Utility
**Complexity:** Beginner

## Description

Formats agent responses for channel-specific constraints including length limits, tone, and structure.

## Implementation

```python
from enum import Enum

class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"

async def format_for_channel(
    response: str,
    channel: Channel,
    ticket_id: str
) -> str:
    """Format response for channel."""

    if channel == Channel.EMAIL:
        return f"""Dear Customer,

Thank you for reaching out to TechCorp Support.

{response}

If you have any further questions, please don't hesitate to reply.

Best regards,
TechCorp AI Support Team
---
Ticket Reference: {ticket_id}
"""

    elif channel == Channel.WHATSAPP:
        # Keep it short
        if len(response) > 300:
            response = response[:297] + "..."
        return f"{response}\n\n📱 Reply 'human' for live support."

    else:  # web_form
        return f"""{response}

---
Need more help? Visit our support portal."""
```

## Related Skills

- **agent-specialization** - Formats agent output
- **whatsapp-integration** - WhatsApp constraints
- **gmail-integration** - Email formatting
