# [Feature Name] - Implementation Plan

**Version:** 1.0.0
**Status:** Draft | In Review | Approved | In Progress | Complete
**Created:** [YYYY-MM-DD]
**Last Updated:** [YYYY-MM-DD]

## Executive Summary

[2-3 sentence summary of what will be built and the approach]

## Constitution Check

This plan complies with:
- [ ] **Agent Maturity Model:** [Incubation/Specialization stage identified]
- [ ] **Multi-Channel First:** [Channel considerations addressed]
- [ ] **Zero Message Loss:** [Persistence strategy defined]
- [ ] **Observability:** [Metrics and logging planned]
- [ ] **Test-Driven:** [Test strategy defined]

## Scope and Dependencies

### In Scope
- [Component/feature 1]
- [Component/feature 2]

### Out of Scope
- [Explicitly excluded work]

### External Dependencies
| Dependency | Owner | Status | Risk |
|------------|-------|--------|------|
| [System/API] | [Team] | Available/Pending | Low/Med/High |

## Architecture Overview

```
[ASCII or Mermaid diagram showing components and data flow]
```

### Key Components

**Component 1: [Name]**
- **Purpose:** [What it does]
- **Technology:** [Stack/framework]
- **Interfaces:** [APIs, events consumed/produced]

## Key Decisions and Rationale

### Decision 1: [Topic]
**Options Considered:**
1. **Option A:** [Description]
   - Pros: [Benefits]
   - Cons: [Drawbacks]
2. **Option B:** [Description]
   - Pros: [Benefits]
   - Cons: [Drawbacks]

**Selected:** Option [A/B]

**Rationale:** [Why this option was chosen]

**ADR:** [Link to ADR if architecturally significant]

## Data Management

### Database Changes
- [ ] New tables: [List]
- [ ] Schema migrations: [Strategy]
- [ ] Data migration: [Required? Strategy?]

### Data Flow
1. [Step 1: Where data enters]
2. [Step 2: How it's processed]
3. [Step 3: Where it's stored]
4. [Step 4: How it's consumed]

## API Contracts

### New Endpoints
- `POST /api/endpoint` - [Purpose]
- `GET /api/endpoint/:id` - [Purpose]

### Modified Endpoints
- `PUT /api/existing` - [Changes]

### Event Schema
```json
{
  "event_type": "example.event",
  "payload": {}
}
```

## Non-Functional Requirements

### Performance
- **Latency Target:** [Xms p95]
- **Throughput Target:** [X req/sec]
- **Resource Budget:** [Memory, CPU]

### Reliability
- **Availability:** [X% uptime]
- **Error Budget:** [X errors/month]
- **Degradation Strategy:** [How to gracefully degrade]

### Security
- **Authentication:** [Mechanism]
- **Authorization:** [Rules]
- **Data Protection:** [Encryption, PII handling]

## Operational Readiness

### Observability
- **Metrics:** [What to measure]
- **Logs:** [What to log]
- **Traces:** [Distributed tracing strategy]
- **Alerts:** [What triggers alerts]

### Deployment Strategy
- **Rollout:** [Canary, blue-green, rolling]
- **Rollback:** [Procedure]
- **Feature Flags:** [Required?]

### Runbooks
- [ ] Normal operation documented
- [ ] Common failures documented
- [ ] Recovery procedures documented

## Risk Analysis

### Top Risks
1. **[Risk Name]**
   - **Impact:** [Description]
   - **Likelihood:** High/Medium/Low
   - **Mitigation:** [Strategy]
   - **Kill Switch:** [How to disable if critical]

## Testing Strategy

### Unit Tests
- [Component]: [Coverage target]

### Integration Tests
- [Integration point]: [Scenarios]

### E2E Tests
- [User journey]: [Test cases]

### Load Tests
- [Load scenario]: [Expected performance]

## Implementation Phases

### Phase 1: [Name] (Est: [N] days)
- [ ] Task 1
- [ ] Task 2
**Deliverable:** [What's complete]

### Phase 2: [Name] (Est: [N] days)
- [ ] Task 1
- [ ] Task 2
**Deliverable:** [What's complete]

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Unit test coverage >85%
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Documentation complete
- [ ] Code reviewed and approved
- [ ] Security review passed (if required)
- [ ] Performance benchmarks met
- [ ] Deployed to staging
- [ ] Runbook created

## Follow-up Work

- [ ] [Future enhancement 1]
- [ ] [Technical debt to address]
- [ ] [Monitoring to establish]

## References

- **Specification:** [Link to spec.md]
- **ADRs:** [Links to relevant ADRs]
- **Related PRs:** [Links if applicable]
- **External Docs:** [Links to API docs, etc.]
