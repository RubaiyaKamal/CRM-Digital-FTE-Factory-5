# Customer Success FTE - Prototype

**Purpose:** Incubation phase prototype for exploring agent capabilities before production implementation.

**Status:** Phase 2 - Core Loop Development

---

## What This Is

This is a **prototype** for discovering requirements and testing approaches. It is:
- ✅ Good for exploration and learning
- ✅ Good for testing with sample tickets
- ✅ Good for discovering edge cases
- ❌ NOT production-ready
- ❌ NOT optimized for performance
- ❌ NOT secure (uses mock APIs)

---

## Architecture

```
prototype/
├── agent.py              # Main agent loop
├── knowledge_base.py     # KB search with embeddings
├── sentiment_analyzer.py # Sentiment analysis
├── channel_formatter.py  # Channel-specific formatting
├── escalation_engine.py  # Escalation decision logic
├── models.py             # Data models (Message, Ticket, etc.)
├── requirements.txt      # Python dependencies
└── test_agent.py         # Test runner with sample tickets
```

---

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Load knowledge base
python knowledge_base.py --load ../context/product-docs.md

# Run tests
python test_agent.py
```

---

## Usage

```python
from agent import CustomerSuccessAgent

agent = CustomerSuccessAgent()

# Process a message
result = agent.process_message(
    message="How do I reset my password?",
    channel="email",
    customer_id="user@example.com"
)

print(result.response)
print(f"Should escalate: {result.should_escalate}")
```

---

## Key Learnings (Updated as we test)

### What Works
- [To be filled during testing]

### What Doesn't Work
- [To be filled during testing]

### Edge Cases Discovered
- [To be filled during testing]

---

## Transition to Production

After incubation completes:
1. Convert tools to MCP server (Phase 4)
2. Migrate to OpenAI Agents SDK (agent-specialization skill)
3. Add production database (PostgreSQL)
4. Add production channels (Gmail API, Twilio, React form)
5. Deploy to Kubernetes

---

*This prototype is for incubation only. Do not use in production.*
