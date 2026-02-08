# Agent Incubation Skill

## Skill Definition

**Name:** agent-incubation
**Version:** 1.0.0
**Type:** Agent Development
**Complexity:** Intermediate

## Description

Guides the incubation phase of agent development - the exploration stage where you discover requirements, test approaches, and prototype capabilities before productionization.

## When to Use This Skill

- Starting a new agent project
- Unclear requirements that need exploration
- Prototyping agent capabilities
- Discovering edge cases and failure modes
- Testing prompt strategies
- Before committing to production architecture

## Inputs

### Business Problem
```markdown
## Problem Statement
Build a Customer Success AI agent that handles support tickets from
email, WhatsApp, and web form with 24/7 availability.

## Success Criteria
- <85% of tickets resolved without escalation
- <3 second response time
- Appropriate tone per channel
- No message loss
```

### Context Files
```
context/
├── company-profile.md      # Business context
├── product-docs.md         # Knowledge base content
├── sample-tickets.json     # Real customer inquiries
├── escalation-rules.md     # When to escalate
└── brand-voice.md          # Communication guidelines
```

## Outputs

### Discovery Log
```markdown
# Discovery Log - Customer Success Agent

## Incubation Period
**Start:** 2026-02-06
**Duration:** 16 hours
**Outcome:** Spec crystallized, ready for specialization

## Key Discoveries

### 1. Channel-Specific Response Patterns
- **Email:** Customers expect formal, detailed responses with greeting/signature
- **WhatsApp:** Users abandon if response >300 characters
- **Web Form:** Semi-formal works best, avoid overly casual language

### 2. Edge Cases Found
1. **Empty messages** - System crashed, now prompts for clarification
2. **Pricing questions** - Initially tried to answer, now escalates immediately
3. **Multi-language** - 15% of WhatsApp messages in Spanish
4. **Angry customers** - Needed sentiment analysis to detect frustration early

### 3. Working Prompts
[Attach successful system prompts that worked during testing]

### 4. Tool Performance
- `search_knowledge_base`: 92% accuracy when query >5 words
- `escalate_to_human`: Initially under-used (8%), now 22% (better)
- `send_response`: Channel formatting critical for satisfaction
```

### Crystallized Specification
```markdown
# Customer Success FTE - Specification

## Purpose
Handle routine support queries with speed and consistency across channels.

## Scope
### In Scope
- Product feature questions
- How-to guidance
- Bug report intake
- Cross-channel conversation continuity

### Out of Scope (Escalate)
- Pricing negotiations
- Refund requests
- Legal questions
- Sentiment <0.3

## Tools Required
1. `search_knowledge_base` - Semantic search over docs
2. `create_ticket` - Log all interactions with channel
3. `get_customer_history` - Cross-channel history retrieval
4. `escalate_to_human` - Hand off with context
5. `send_response` - Channel-aware formatting
```

## Implementation Steps

### Phase 1: Initial Exploration (2-3 hours)

**Prompt Claude Code:**
```
I need to build a Customer Success AI agent for a SaaS company.

The agent should:
- Answer customer questions from product documentation
- Accept tickets from THREE channels: Gmail, WhatsApp, and Web Form
- Know when to escalate to humans
- Track all interactions with channel source metadata

I've provided company context in the /context folder.
Help me explore what this system should look like.
Start by analyzing the sample tickets and identifying patterns across channels.
```

**Activities:**
1. Upload context files to Claude Code
2. Let Claude analyze sample tickets
3. Ask probing questions: "What patterns do you see? What could go wrong?"
4. Document findings in discovery log

### Phase 2: Prototype Core Loop (4-5 hours)

**Prompt Claude Code:**
```
Based on our analysis, let's prototype the core customer interaction loop.
Build a simple version that:
1. Takes a customer message as input (with channel metadata)
2. Normalizes the message regardless of source channel
3. Searches the product docs for relevant information
4. Generates a helpful response
5. Formats response appropriately for the channel
6. Decides if escalation is needed

Use Python. Start simple - we'll iterate.
```

**Iteration Prompts:**
```
# After first version works:
"This crashes when the customer asks about pricing.
Add handling for pricing-related queries."

# Channel-specific iteration:
"WhatsApp messages are much shorter and more casual.
Adjust response style based on channel."

# After testing with scenarios:
"The responses are too long for WhatsApp. Customers want concise answers.
Optimize for brevity on chat channels while keeping detail on email."
```

### Phase 3: Add Memory and State (3-4 hours)

**Prompt Claude Code:**
```
Our agent needs to remember context across a conversation.
If a customer asks follow-up questions, the agent should understand
they're continuing the same topic - even if they switch channels!

Add conversation memory. Also track:
- Customer sentiment (is this interaction going well?)
- Topics discussed (for reporting)
- Resolution status (solved/pending/escalated)
- Original channel and any channel switches
- Customer identifier (email address as primary key)
```

### Phase 4: Build MCP Server (3-4 hours)

**Create MCP Tool Definitions:**
```python
# mcp_server.py
from mcp.server import Server
from mcp.types import Tool
from enum import Enum

class Channel(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"

server = Server("customer-success-fte")

@server.tool("search_knowledge_base")
async def search_kb(query: str) -> str:
    """Search product documentation for relevant information."""
    # Your prototype implementation
    pass

@server.tool("create_ticket")
async def create_ticket(
    customer_id: str,
    issue: str,
    priority: str,
    channel: Channel
) -> str:
    """Create a support ticket in the system with channel tracking."""
    pass

@server.tool("get_customer_history")
async def get_customer_history(customer_id: str) -> str:
    """Get customer's interaction history across ALL channels."""
    pass

@server.tool("send_response")
async def send_response(
    ticket_id: str,
    message: str,
    channel: Channel
) -> str:
    """Send response via the appropriate channel."""
    pass
```

### Phase 5: Define Agent Skills (2-3 hours)

**Create Skills Manifest:**
```yaml
# skills.yaml
skills:
  - name: Knowledge Retrieval
    trigger: Customer asks product questions
    inputs:
      - query_text: string
    outputs:
      - relevant_docs: list[Document]
    success_criteria:
      - "Finds answer in <500ms"
      - "Relevance score >0.7"

  - name: Sentiment Analysis
    trigger: Every customer message
    inputs:
      - message_text: string
    outputs:
      - sentiment: float  # -1.0 to 1.0
      - confidence: float
    success_criteria:
      - "Detects anger/frustration correctly"
      - "Confidence >0.8 for escalation decisions"

  - name: Channel Adaptation
    trigger: Before sending any response
    inputs:
      - response_text: string
      - target_channel: Channel
    outputs:
      - formatted_response: string
    success_criteria:
      - "Email: includes greeting and signature"
      - "WhatsApp: <300 chars preferred, <1600 max"
      - "Web: semi-formal, <300 words"
```

## Testing During Incubation

### Test Scenarios by Channel

**Email Scenarios:**
```python
scenarios = [
    {
        "input": "I can't log in to my account",
        "expected": "Detailed troubleshooting steps with links",
        "expected_length": "200-500 words"
    },
    {
        "input": "How much does the enterprise plan cost?",
        "expected": "Immediate escalation to sales",
        "expected_action": "escalate"
    }
]
```

**WhatsApp Scenarios:**
```python
scenarios = [
    {
        "input": "help",
        "expected": "Brief menu of options",
        "expected_length": "<100 chars"
    },
    {
        "input": "How do I reset my password?",
        "expected": "Concise steps with link",
        "expected_length": "<300 chars"
    }
]
```

### Edge Case Testing

Test these during incubation:
1. Empty messages
2. Messages in different languages
3. Very long messages (>1000 words)
4. Rapid-fire follow-ups
5. Profanity and aggressive language
6. Questions about competitors
7. Requests for features that don't exist
8. Customer switching channels mid-conversation

## Incubation Deliverables Checklist

Before transitioning to specialization:

- [ ] Working prototype handles queries from any channel
- [ ] Discovery log documents all findings
- [ ] MCP server with 5+ tools exposed
- [ ] Agent skills defined and tested
- [ ] Edge cases documented (minimum 20)
- [ ] Escalation rules crystallized
- [ ] Channel-specific response templates discovered
- [ ] Performance baseline measured
- [ ] Specification document created
- [ ] Working system prompt documented

## Common Pitfalls

1. **Over-engineering**: Don't build production features during incubation
2. **Skipping documentation**: Discovery log is critical for specialization
3. **Ignoring edge cases**: They become production bugs
4. **Not testing channels differently**: Each channel has unique constraints
5. **Premature optimization**: Focus on discovering requirements first

## Success Metrics

### Quantitative
- Tested with 50+ sample tickets per channel
- Discovered 20+ edge cases
- Achieved >85% accuracy on test set
- Escalation rate 15-25% (not too high/low)

### Qualitative
- Clear understanding of when agent works vs. fails
- Documented channel-specific requirements
- Confidence in moving to production
- Stakeholder buy-in on approach

## Transition Criteria

You're ready for specialization when:
✅ All deliverables complete
✅ Prototype demonstrates feasibility
✅ Edge cases documented with handling strategies
✅ Team agrees specification is complete
✅ No major unknowns remaining

## Related Skills

- **mcp-to-agents-migration** - Next step: convert to production
- **agent-specialization** - Production implementation
- **channel-response-formatter** - Implement channel formatting
