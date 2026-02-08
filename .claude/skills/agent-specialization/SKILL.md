# Agent Specialization Skill

## Skill Definition

**Name:** agent-specialization
**Version:** 1.0.0
**Type:** Agent Development
**Complexity:** Advanced

## Description

Transforms incubation prototypes into production-grade agents using OpenAI Agents SDK with proper typing, error handling, observability, and deployment readiness.

## When to Use This Skill

- After completing incubation phase
- Converting prototype to production
- Implementing production agent with OpenAI SDK
- Hardening agent for 24/7 operation
- Adding proper error handling and logging

## Inputs

### From Incubation
```
incubation/
├── discovery-log.md        # Requirements discovered
├── prototype/              # Working prototype code
├── mcp_server.py           # MCP tool definitions
├── working-prompts.md      # Successful prompts
└── edge-cases.md           # Known failure modes
```

## Outputs

### Production Agent Structure
```
production/
├── agent/
│   ├── customer_success_agent.py  # Main agent
│   ├── tools.py                    # @function_tool definitions
│   ├── prompts.py                  # System prompts
│   └── formatters.py               # Channel formatting
├── tests/
│   ├── test_agent.py               # Unit tests
│   └── test_transition.py          # Validates incubation behavior
└── config/
    └── agent_config.yaml           # Agent configuration
```

## Implementation Steps

### Step 1: Extract Working Prompts (30 min)

**From Incubation to Production:**
```python
# production/agent/prompts.py

CUSTOMER_SUCCESS_SYSTEM_PROMPT = """You are a Customer Success agent for TechCorp SaaS.

## Your Purpose
Handle routine customer support queries with speed, accuracy, and empathy across multiple channels.

## Channel Awareness
You receive messages from three channels. Adapt your communication style:
- **Email**: Formal, detailed responses. Include proper greeting and signature.
- **WhatsApp**: Concise, conversational. Keep responses under 300 characters when possible.
- **Web Form**: Semi-formal, helpful. Balance detail with readability.

## Required Workflow (ALWAYS follow this order)
1. FIRST: Call `create_ticket` to log the interaction
2. THEN: Call `get_customer_history` to check for prior context
3. THEN: Call `search_knowledge_base` if product questions arise
4. FINALLY: Call `send_response` to reply

## Hard Constraints (NEVER violate)
- NEVER discuss pricing → escalate immediately
- NEVER promise features not in documentation
- NEVER process refunds → escalate with reason "refund_request"
- NEVER respond without using send_response tool
- NEVER exceed response limits: Email=500 words, WhatsApp=300 chars, Web=300 words

## Escalation Triggers
[Copy from discovery log]
"""
```

### Step 2: Convert MCP Tools to Production Tools (2-3 hours)

**Before (MCP):**
```python
@server.tool("search_knowledge_base")
async def search_kb(query: str) -> str:
    results = simple_search(query)
    return str(results)
```

**After (OpenAI Agents SDK):**
```python
from agents import function_tool
from pydantic import BaseModel
from typing import Optional

class KnowledgeSearchInput(BaseModel):
    """Input schema with validation."""
    query: str
    max_results: int = 5
    category: Optional[str] = None

@function_tool
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    """Search product documentation.

    Use this when customer asks about product features or needs help.

    Args:
        input: Search parameters

    Returns:
        Formatted search results with relevance scores
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Vector similarity search
            embedding = await generate_embedding(input.query)

            results = await conn.fetch("""
                SELECT title, content,
                       1 - (embedding <=> $1::vector) as similarity
                FROM knowledge_base
                WHERE ($2::text IS NULL OR category = $2)
                ORDER BY embedding <=> $1::vector
                LIMIT $3
            """, embedding, input.category, input.max_results)

            if not results:
                return "No relevant documentation found. Consider escalating."

            formatted = []
            for r in results:
                formatted.append(
                    f"**{r['title']}** (relevance: {r['similarity']:.2f})\n"
                    f"{r['content'][:500]}"
                )

            return "\n\n---\n\n".join(formatted)

    except Exception as e:
        logger.error(f"Knowledge search failed: {e}")
        return "Knowledge base temporarily unavailable. Please try again."
```

### Step 3: Create Production Agent (2 hours)

```python
# production/agent/customer_success_agent.py

from openai import OpenAI
from agents import Agent
from agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response
)
from agent.prompts import CUSTOMER_SUCCESS_SYSTEM_PROMPT

customer_success_agent = Agent(
    name="Customer Success FTE",
    model="gpt-4o",
    instructions=CUSTOMER_SUCCESS_SYSTEM_PROMPT,
    tools=[
        search_knowledge_base,
        create_ticket,
        get_customer_history,
        escalate_to_human,
        send_response
    ],
)

# Usage in worker
async def process_message(message: dict):
    result = await customer_success_agent.run(
        messages=[{"role": "user", "content": message['content']}],
        context={
            'customer_id': message['customer_id'],
            'channel': message['channel'],
            'conversation_id': message['conversation_id']
        }
    )
    return result
```

### Step 4: Add Channel-Aware Formatting (1-2 hours)

```python
# production/agent/formatters.py

from enum import Enum

class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"

async def format_for_channel(response: str, channel: Channel, ticket_id: str) -> str:
    """Format response appropriately for channel."""

    if channel == Channel.EMAIL:
        return f"""Dear Customer,

Thank you for reaching out to TechCorp Support.

{response}

If you have any further questions, please don't hesitate to reply to this email.

Best regards,
TechCorp AI Support Team
---
Ticket Reference: {ticket_id}
"""

    elif channel == Channel.WHATSAPP:
        # Keep it short
        if len(response) > 300:
            response = response[:297] + "..."
        return f"{response}\n\n📱 Reply for more help or type 'human' for live support."

    else:  # web_form
        return f"""{response}

---
Need more help? Reply to this message or visit our support portal."""
```

### Step 5: Write Transition Tests (2 hours)

```python
# tests/test_transition.py
"""Validate production agent matches incubation behavior."""

import pytest
from agent.customer_success_agent import customer_success_agent

class TestTransitionFromIncubation:
    """Tests based on edge cases discovered during incubation."""

    @pytest.mark.asyncio
    async def test_edge_case_pricing_escalation(self):
        """Pricing questions must escalate (from discovery log)."""
        result = await customer_success_agent.run(
            messages=[{
                "role": "user",
                "content": "How much does the enterprise plan cost?"
            }],
            context={"channel": "email", "customer_id": "test-1"}
        )

        assert result.escalated == True
        assert "pricing" in result.escalation_reason.lower()

    @pytest.mark.asyncio
    async def test_channel_response_length_whatsapp(self):
        """WhatsApp responses must be concise (from discovery)."""
        result = await customer_success_agent.run(
            messages=[{
                "role": "user",
                "content": "How do I reset my password?"
            }],
            context={"channel": "whatsapp", "customer_id": "test-2"}
        )

        # Should be much shorter than email
        assert len(result.output) < 500
```

## Production Checklist

- [ ] All MCP tools converted to @function_tool
- [ ] Pydantic input validation on all tools
- [ ] Error handling with graceful fallbacks
- [ ] System prompt extracted to prompts.py
- [ ] Channel formatting implemented
- [ ] Transition tests passing
- [ ] Database connection pooling
- [ ] Structured logging configured
- [ ] Metrics collection built-in
- [ ] Configuration externalized

## Error Handling Patterns

```python
@function_tool
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    try:
        # Primary logic
        results = await search_database(input.query)
        return format_results(results)

    except asyncpg.PostgresError as e:
        # Database errors
        logger.error(f"Database error in knowledge search: {e}")
        return "Knowledge base temporarily unavailable. Please try again."

    except Exception as e:
        # Unexpected errors
        logger.exception(f"Unexpected error in knowledge search: {e}")
        return "An error occurred while searching. A human agent will follow up."
```

## Performance Optimization

### Connection Pooling
```python
# Global connection pool
_db_pool = None

async def get_db_pool():
    global _db_pool
    if _db_pool is None:
        _db_pool = await asyncpg.create_pool(
            dsn=DATABASE_URL,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
    return _db_pool
```

### Caching
```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=1000)
def get_cached_knowledge(query: str, ttl_minutes: int = 60):
    # Cache knowledge base results
    pass
```

## Observability

```python
import time
import logging

logger = logging.getLogger(__name__)

@function_tool
async def search_knowledge_base(input: KnowledgeSearchInput) -> str:
    start_time = time.time()

    try:
        result = await _search(input)

        # Log metrics
        latency_ms = (time.time() - start_time) * 1000
        logger.info(
            "knowledge_search_completed",
            extra={
                "query_length": len(input.query),
                "results_count": result.count,
                "latency_ms": latency_ms
            }
        )

        return result

    except Exception as e:
        logger.error(
            "knowledge_search_failed",
            extra={"error": str(e), "query": input.query}
        )
        raise
```

## Related Skills

- **agent-incubation** - Previous phase
- **database-crm-setup** - Database integration
- **kafka-streaming** - Event streaming
- **kubernetes-deployment** - Deployment
