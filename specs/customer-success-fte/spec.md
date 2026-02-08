# Customer Success FTE Agent — Specification

**Version:** 1.0.0
**Status:** Active
**Phase:** Specialization (Stage 2)

---

## Overview

A multi-channel AI Customer Success agent that handles support tickets from Email, WhatsApp, and Web Form channels. Replaces 1 FTE by automating first-response for 75%+ of tickets, escalating to humans only when required.

## Goals

- P95 response latency < 3 seconds
- Zero message loss (Kafka durability)
- >75% resolution rate without escalation
- Cost per interaction < $0.05

## Functional Requirements

### FR-1: Channel Ingestion
- Accept webhooks from Gmail, Twilio (WhatsApp), and React Web Form
- Each webhook validates payload, writes to DB, publishes to Kafka, returns 200 OK within 500ms

### FR-2: Customer Identification
- Unified customer record keyed by `(identifier, identifier_type)`
- Cross-channel: same email used via web form + email → same customer
- Phone normalization for WhatsApp identifiers

### FR-3: AI Agent Processing
- OpenAI Agents SDK with 5 tools:
  1. `create_ticket` — stores ticket in DB
  2. `get_customer_history` — loads past interactions
  3. `search_knowledge_base` — pgvector semantic search
  4. `escalate_to_human` — flags for human with reason + priority
  5. `send_response` — formats for channel and writes to output

### FR-4: Escalation Logic
- Immediate: billing disputes, legal keywords, security incidents
- Sentiment-based: score < 0.3 (VADER)
- Category: BILLING, LEGAL, COMPLIANCE, SALES
- Conversation depth: > 6 turns without resolution
- Customer explicit request

### FR-5: Response Formatting
- Email: formal greeting, markdown, professional signature
- WhatsApp: ultra-concise, casual, ≤ 300 chars per message segment
- Web Form: semi-formal, markdown rendered, SSE stream for real-time

### FR-6: Observability
- Structured JSON logs on all services
- Kafka consumer lag metrics
- DB pool metrics
- Agent tool call traces

## Non-Functional Requirements

| NFR | Target |
|-----|--------|
| Uptime | >99.9% (24h test) |
| Message loss | 0% |
| P95 latency | <3s (all channels) |
| Test coverage | >85% backend |
| Cost/interaction | <$0.05 |

## Data Model (summary)

- `customers(id, name, email, phone, created_at)`
- `customer_identifiers(id, customer_id, identifier, type, channel)` — links email/phone to customer
- `conversations(id, customer_id, channel, status, created_at, updated_at)`
- `messages(id, conversation_id, role, content, channel, metadata, created_at)`
- `tickets(id, conversation_id, customer_id, channel, category, priority, status, sentiment_score)`
- `knowledge_base(id, title, content, embedding vector(1536), section)`
- `agent_metrics(id, ticket_id, tool_calls, latency_ms, model, tokens_used)`

## Channels

| Channel | Inbound | Outbound |
|---------|---------|----------|
| Email (Gmail) | Webhook parse | Mock send (log) |
| WhatsApp (Twilio) | Webhook + sig validation | Mock send (log) |
| Web Form (React) | POST /webhooks/web_form | SSE stream |

## Event Flow

```
Webhook → POST /webhooks/{channel}
  → validate payload
  → upsert customer_identifier
  → insert conversation + message (DB)
  → publish fte.tickets.incoming (Kafka)
  → return 200 OK

Kafka consumer (message_processor)
  → consume fte.tickets.incoming
  → load customer history
  → run OpenAI Agent (tools)
  → publish fte.responses.outgoing (Kafka)

Kafka consumer (response_handler)
  → consume fte.responses.outgoing
  → format for channel
  → send via channel adapter
  → update ticket status in DB
```

## Acceptance Criteria

- [ ] `docker-compose up` starts all services without error
- [ ] POST /webhooks/web_form with sample payload returns 200 in < 500ms
- [ ] Web form UI submits ticket → agent responds within 3s
- [ ] Same email via email + web_form maps to single customer record
- [ ] Security keyword triggers immediate P0 escalation
- [ ] `pytest src/tests/ --cov=src --cov-fail-under=85` passes
