# Project Constitution

**Project Name:** CRM Digital FTE Factory - Customer Success AI Employee
**Constitution Version:** 1.0.0
**Ratification Date:** 2026-02-06
**Last Amended:** 2026-02-06

## Purpose

This constitution establishes the non-negotiable principles, standards, and governance rules for building a production-grade 24/7 Customer Success Digital FTE (Full-Time Equivalent). This AI employee handles customer support across multiple channels (Email, WhatsApp, Web Form) with zero downtime, operating at <$1,000/year versus $75,000+ for human equivalents.

## Core Principles

### Principle 1: Multi-Channel First Architecture

**Statement:** Every component MUST support Email, WhatsApp, and Web Form channels as first-class citizens with channel-aware response formatting, unified customer identification, and cross-channel conversation continuity.

**Rationale:** Customers expect seamless support regardless of channel. Channel-specific implementations that don't unify customer identity create fragmented experiences and lost context. A customer starting on email and continuing on WhatsApp must not repeat themselves.

**Enforcement:**
- All message handlers MUST normalize input to a unified schema with `channel` metadata
- Database schema MUST track `initial_channel` and per-message `channel` separately
- Customer identification MUST merge identifiers across channels (email, phone, etc.)
- Response formatting MUST adapt to channel constraints (email: 2000 chars, WhatsApp: 300 chars preferred)
- All tests MUST verify cross-channel scenarios

### Principle 2: Agent Maturity Model Compliance

**Statement:** Development MUST follow the two-stage evolution: (1) Incubation with Claude Code for exploration and prototyping, (2) Specialization with OpenAI Agents SDK for production deployment.

**Rationale:** The Agent Maturity Model prevents premature productionization. Incubation discovers hidden requirements and edge cases. Specialization hardens prototypes into reliable systems with proper error handling, typing, and observability.

**Enforcement:**
- Incubation phase MUST produce: discovery log, working prototype, MCP server, edge case documentation
- Transition MUST include: test suite validating prototype behavior, tool migration from MCP to @function_tool, Pydantic input validation
- Specialization phase MUST add: PostgreSQL state management, Kafka event streaming, Kubernetes deployment, channel integrations
- No production deployment without completing both stages

### Principle 3: Zero Message Loss Guarantee

**Statement:** Every customer message MUST be persisted to PostgreSQL and published to Kafka before acknowledgment. System failures MUST NOT result in lost customer communications.

**Rationale:** Lost messages destroy customer trust and violate support SLAs. A 24/7 FTE must be more reliable than human operators who forget context or lose emails.

**Enforcement:**
- Channel webhooks MUST write to database before returning 200 OK
- Kafka publishes MUST use `send_and_wait` for acknowledgment
- Failed processing MUST route to Dead Letter Queue with retry logic
- All messages MUST have `delivery_status` tracking (pending/sent/delivered/failed)
- Recovery procedures MUST handle Kafka consumer lag and database downtime

### Principle 4: Channel-Appropriate Response Quality

**Statement:** Responses MUST adapt tone, length, and formatting to match channel expectations while maintaining brand consistency.

**Rationale:** A formal 500-word email response fails on WhatsApp where users expect <300 character replies. Generic responses feel robotic. Channel-appropriate communication increases satisfaction and resolution rates.

**Enforcement:**
- Email responses MUST include greeting, signature, ticket reference
- WhatsApp responses MUST be conversational, use emojis appropriately, stay under 300 chars primary message
- Web form responses MUST be semi-formal with clear next steps
- All responses MUST pass through `format_for_channel()` function
- Response templates MUST exist for each channel in `channel_configs` table

### Principle 5: Intelligent Escalation, Not Avoidance

**Statement:** The agent MUST escalate to human support when it detects pricing inquiries, legal language, negative sentiment (<0.3), or inability to find relevant information after 2 attempts. Escalation is success, not failure.

**Rationale:** Poor AI responses cause more damage than admitting limitations. Customers respect honest escalation. The goal is customer satisfaction, not automation at all costs.

**Enforcement:**
- Escalation triggers MUST be explicitly defined in system prompt
- All escalations MUST include: ticket_id, reason, conversation context, sentiment score
- Escalation events MUST publish to `fte.escalations` Kafka topic
- Human agents MUST receive full conversation history across all channels
- Escalation rate >25% triggers review, but <10% suggests under-escalation

### Principle 6: Production-Grade Observability

**Statement:** Every interaction MUST emit structured metrics including: channel, latency_ms, tokens_used, tools_called, sentiment_score, escalation_reason, delivery_status. Observability is not optional.

**Rationale:** A 24/7 FTE operates autonomously. Without metrics, failures are invisible until customers complain. Channel-specific metrics reveal performance differences and capacity planning needs.

**Enforcement:**
- All messages MUST write to `agent_metrics` table
- Kafka `fte.metrics` topic MUST receive real-time events
- Metrics MUST be queryable by: channel, time range, customer_id, status
- Dashboards MUST show: messages/hour by channel, p95 latency by channel, escalation rate by channel, sentiment trends
- Alerts MUST trigger on: latency >5s, escalation rate >30%, delivery failures >5%

### Principle 7: Database as CRM (No External Dependencies)

**Statement:** The PostgreSQL database IS the CRM system. No external CRM integration (Salesforce, HubSpot) is required. The schema MUST provide complete customer lifecycle tracking.

**Rationale:** Building a custom CRM teaches fundamentals and removes external dependencies. The `customers`, `conversations`, `tickets`, `messages` tables provide all functionality needed for a working Digital FTE.

**Enforcement:**
- Database schema MUST include: customers, customer_identifiers, conversations, messages, tickets, knowledge_base, channel_configs, agent_metrics
- Customer identification MUST support multiple identifiers (email, phone, external IDs)
- Conversation history MUST persist across all channels
- Ticket lifecycle MUST be fully tracked (open/processing/escalated/resolved)
- No references to external CRM APIs in production code

### Principle 8: Kubernetes-Native Deployment

**Statement:** The FTE MUST deploy to Kubernetes with horizontal pod autoscaling, health checks, and zero-downtime rolling updates. Local development MUST use Docker Compose.

**Rationale:** Kubernetes provides the infrastructure for 24/7 availability. Manual server management cannot compete with orchestrated pod scheduling, automatic restarts, and horizontal scaling during traffic spikes.

**Enforcement:**
- All services MUST have Dockerfiles with multi-stage builds
- Kubernetes manifests MUST include: Deployments, Services, ConfigMaps, Secrets, HPA, Ingress
- API pods MUST have: livenessProbe, readinessProbe, resource limits
- Worker pods MUST scale based on Kafka consumer lag
- ConfigMaps MUST externalize all configuration (no hardcoded values)
- Secrets MUST use Kubernetes Secrets or external secret managers

### Principle 9: Test-Driven Reliability

**Statement:** Every channel integration, agent tool, and escalation rule MUST have automated tests. Multi-channel E2E tests MUST pass before deployment.

**Rationale:** A 24/7 FTE cannot rely on manual QA. Regressions in channel handlers or agent logic cause immediate customer impact. Tests are the only scalable verification mechanism.

**Enforcement:**
- Unit tests MUST cover: all @function_tool functions, channel handlers, customer identification logic
- Integration tests MUST cover: Kafka event flow, database transactions, agent workflows
- E2E tests MUST cover: web form submission → agent response, email webhook → reply, WhatsApp message → formatted response
- Cross-channel tests MUST verify: customer identification across channels, conversation continuity, history retrieval
- Test coverage MUST be: backend >85%, critical paths >95%

### Principle 10: Spec-Driven Development Compliance

**Statement:** All work MUST follow SDD workflow: constitution → specification → plan → tasks → implementation. Every user interaction MUST generate a PHR (Prompt History Record).

**Rationale:** Undocumented decisions create technical debt. PHRs provide learning history and audit trails. Specifications prevent scope creep. Plans surface architectural issues before coding.

**Enforcement:**
- Constitution exists at `.specify/memory/constitution.md` and governs all decisions
- Feature specs MUST exist at `specs/<feature>/spec.md` before implementation
- Architectural plans MUST exist at `specs/<feature>/plan.md` with ADR links
- Tasks MUST exist at `specs/<feature>/tasks.md` with acceptance criteria
- PHRs MUST be created after every user interaction at `history/prompts/{constitution|<feature>|general}/`
- ADRs MUST be created for significant decisions at `history/adr/`

## Code Quality Standards

### Language and Framework Standards

- **Backend:** Python 3.11+ with FastAPI, OpenAI Agents SDK, asyncio, asyncpg
- **Frontend (Web Form):** React 18+ with Next.js 14+, TypeScript, Tailwind CSS
- **Database:** PostgreSQL 16+ with pgvector extension for semantic search
- **Streaming:** Apache Kafka 3.x with aiokafka client
- **Orchestration:** Kubernetes 1.28+ with Helm charts (optional)

### Code Style

- **Python:** Follow PEP 8, use Black formatter, type hints required
- **TypeScript:** Use strict mode, ESLint with Airbnb config
- **Naming:** snake_case for Python, camelCase for TypeScript, SCREAMING_SNAKE_CASE for constants
- **Imports:** Absolute imports preferred, grouped (stdlib, third-party, local)

### Documentation Requirements

- All @function_tool decorators MUST have detailed docstrings explaining: purpose, when to use, inputs, outputs, edge cases
- All API endpoints MUST have OpenAPI/Swagger documentation
- All channel handlers MUST document webhook signature validation
- Database schema MUST have comments explaining table purposes and relationships
- README MUST include: architecture diagram, deployment instructions, local development setup

## Testing Standards

### Test Coverage Requirements

- Backend unit tests: >85% coverage
- Critical paths (message processing, escalation): >95% coverage
- All channel integrations: E2E tests required
- All agent tools: Unit tests with mocked dependencies
- Load tests: Must handle 100 concurrent requests with <3s p95 latency

### Test Organization

- Unit tests: `tests/test_*.py` mirroring `src/` structure
- Integration tests: `tests/integration/`
- E2E tests: `tests/e2e/`
- Load tests: `tests/load_test.py` using Locust

### Test Data

- Sample tickets: `context/sample-tickets.json` with 50+ examples per channel
- Edge cases: Documented in `specs/discovery-log.md` with corresponding test cases
- Test database: Seed scripts in `database/test_data/`

## Performance Standards

### Latency Requirements

- Message processing: <3 seconds (agent execution time)
- End-to-end delivery: <30 seconds (including channel API latency)
- Database queries: <100ms (p95)
- Knowledge base search: <500ms (p95)

### Throughput Requirements

- Minimum: 10 messages/second per worker pod
- Target: 50 messages/second cluster-wide
- Peak: 200 messages/second with HPA scaling

### Resource Limits

- API pod: 512Mi RAM request, 1Gi limit; 250m CPU request, 500m limit
- Worker pod: 512Mi RAM request, 1Gi limit; 250m CPU request, 500m limit
- Database: 2Gi RAM minimum, 4 CPU minimum for production

## Security Standards

### Authentication and Authorization

- Channel webhooks MUST validate signatures (Twilio X-Twilio-Signature, Gmail Pub/Sub tokens)
- API endpoints MUST use API keys for programmatic access
- Database credentials MUST use Kubernetes Secrets, never hardcoded
- Environment variables MUST be validated at startup

### Data Protection

- Customer PII MUST be encrypted at rest (PostgreSQL encryption)
- API communication MUST use TLS 1.3
- Secrets MUST never appear in logs or error messages
- Message content MUST be sanitized before logging (PII redaction)

### Compliance

- GDPR: Customer data deletion endpoint required
- Data retention: Messages older than 2 years archived/deleted
- Audit logs: All escalations and data access logged
- Incident response: Runbook required in `docs/runbook.md`

## Architecture Principles

### Microservices Boundaries

- **API Service:** FastAPI application handling all webhook endpoints
- **Message Processor Workers:** Kafka consumers running agent logic
- **Database:** PostgreSQL as single source of truth
- **Event Bus:** Kafka for async message processing and metrics

### Data Flow

1. Channel webhook receives message → validates signature → writes to DB → publishes to Kafka → returns 200 OK
2. Worker consumes Kafka event → identifies customer → loads history → runs agent → stores response → publishes to output topic
3. Response handler consumes output topic → formats for channel → sends via channel API → updates delivery status

### Scalability Strategy

- API pods: Scale based on CPU utilization (target 70%)
- Worker pods: Scale based on Kafka consumer lag (target <10 messages)
- Database: Read replicas for queries, master for writes
- Kafka: Partition by customer_id for ordered processing per customer

## Governance

### Amendment Procedure

1. Proposed changes MUST be discussed in project documentation
2. Constitutional amendments MUST increment version according to semver
3. Major changes (new principles, removed principles) require version bump to next major
4. Minor changes (expanded guidance, new sections) bump minor version
5. Patch changes (clarifications, typos) bump patch version
6. Amended constitution MUST update `LAST_AMENDED` date
7. Sync Impact Report MUST be generated as HTML comment at top of file

### Version History

- **1.0.0** (2026-02-06): Initial constitution ratified for Customer Success Digital FTE project

### Compliance Review

- Code reviews MUST verify principle adherence
- PRs violating principles MUST be rejected with constitutional reference
- Monthly architecture reviews MUST assess constitutional alignment
- Incidents MUST be evaluated for constitutional violations

### Conflict Resolution

- When principles conflict, prioritize in order: (1) Zero Message Loss, (2) Multi-Channel First, (3) Intelligent Escalation, (4) remaining principles
- Unresolvable conflicts escalate to project lead for constitutional amendment proposal

## Success Metrics

### Business Metrics

- Cost per interaction: <$0.05 (vs $15-25 for human agent)
- Customer satisfaction: >80% positive sentiment
- First response time: <5 minutes (24/7)
- Resolution rate: >75% without escalation

### Technical Metrics

- Uptime: >99.9% (24-hour test)
- Message loss rate: 0%
- Cross-channel identification accuracy: >95%
- p95 latency: <3 seconds (all channels)

### Operational Metrics

- Deployment frequency: Multiple per day
- Mean time to recovery: <15 minutes
- Change failure rate: <5%
- Incident response time: <30 minutes to acknowledgment
