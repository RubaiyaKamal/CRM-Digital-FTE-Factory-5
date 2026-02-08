# Discovery Log - Customer Success FTE Agent

**Project:** CRM Digital FTE Factory - Customer Success AI Agent
**Incubation Start:** 2026-02-06
**Status:** Phase 1 - Initial Exploration
**Analyst:** Claude Code (Sonnet 4.5)

---

## Executive Summary

**Problem Statement:**
Build a Customer Success AI agent for TechCorp SaaS (CloudFlow product) that handles support tickets from email, WhatsApp, and web form with 24/7 availability, achieving >75% resolution rate without human escalation while maintaining channel-appropriate tone.

**Key Findings:**
- **18 of 60 tickets (30%)** require immediate human escalation
- **42 of 60 tickets (70%)** can be handled by AI with proper knowledge base
- Channel response patterns are **dramatically different** - one-size-fits-all won't work
- Sentiment analysis is **critical** - 13% of tickets have negative/angry sentiment requiring special handling
- **Cross-channel customer identification** is essential (same customer may use email + WhatsApp)

---

## Dataset Analysis

### Ticket Distribution by Channel

| Channel | Count | % | Avg Length | Response Expectation |
|---------|-------|---|-----------|----------------------|
| Email | 27 | 45% | 150-300 words | Detailed, formal, with greeting/signature |
| WhatsApp | 20 | 33% | 5-50 words | Concise, casual, <300 chars ideal |
| Web Form | 13 | 22% | 50-150 words | Semi-formal, scannable, balanced |

**Key Insight:** WhatsApp messages are 80% shorter than email but expect 90% faster response time.

### Category Breakdown

| Category | Count | % | AI Resolvable? | Notes |
|----------|-------|---|----------------|-------|
| Technical | 16 | 27% | ✅ Mostly | Need troubleshooting logic + status page check |
| How-to | 12 | 20% | ✅ Yes | Direct answers from knowledge base |
| Sales/Pricing | 6 | 10% | ❌ Escalate | Pricing negotiation requires human judgment |
| Billing | 5 | 8% | ❌ Escalate | Disputes/refunds require payment system access |
| Legal/Compliance | 5 | 8% | ❌ Escalate | GDPR, DPA, legal threats must go to legal team |
| Feature Requests | 5 | 8% | ✅ Yes | Acknowledge + log for product team |
| Positive Feedback | 4 | 7% | ✅ Yes | Thank customer + encourage review |
| Other | 7 | 12% | 🔶 Mixed | Varies by specific request |

**Target Resolution Rate:** 70% (42/60) is achievable with proper escalation rules.

### Sentiment Analysis

| Sentiment | Count | % | Action Required |
|-----------|-------|---|-----------------|
| Neutral | 28 | 47% | Standard response |
| Positive | 12 | 20% | Thank + reinforce positive experience |
| Frustrated | 10 | 17% | Empathy + faster resolution |
| Angry | 6 | 10% | **ESCALATE** - Human empathy needed |
| Very Angry | 2 | 3% | **ESCALATE IMMEDIATELY** - P0 priority |
| Confused | 2 | 3% | Simplify explanation + visual aids |

**Critical Threshold:** Sentiment score <0.3 (angry/very-angry) → Immediate escalation

### Priority Distribution

| Priority | Count | Expected Response Time | Notes |
|----------|-------|------------------------|-------|
| Low | 25 | <24 hours | Simple how-to, feature requests |
| Medium | 20 | <12 hours | Standard technical issues |
| High | 12 | <4 hours | Integration failures, billing disputes |
| Urgent | 2 | <1 hour | Repeat angry customers, SSO blocking |
| P0 | 1 | <15 minutes | Security incidents, legal threats |

**AI Advantage:** Can provide <5 minute response for ALL priorities (even P0 escalations can be triaged faster)

---

## Key Discovery #1: Channel-Specific Response Patterns

### Email Channel (27 tickets analyzed)

**Customer Expectations:**
- Formal greeting: "Hi [FirstName],"
- Detailed step-by-step explanations (numbered lists)
- Context and empathy: "I understand this is frustrating"
- Clear next steps
- Professional signature: "Best regards, CloudFlow Support"
- Links to documentation

**Example Success Pattern (T001 - Password Reset):**
```markdown
Hi Sarah,

Thanks for reaching out about password reset issues!

I can see why this is frustrating. Here's how to reset your password:

1. Go to the login page at app.techcorp-cloudflow.com
2. Click "Forgot Password" below the login button
3. Enter your email address
4. Check your inbox for a reset link (expires in 1 hour)
5. Click the link and create a new password

**IMPORTANT:** Check your spam folder if you don't see the email within 5 minutes.

Let me know if this works for you!

Best regards,
CloudFlow Support Team
```

**Length:** 200-500 words acceptable
**Tone:** Professional but friendly
**Format:** Heavy use of bullets, bold, numbered steps

### WhatsApp Channel (20 tickets analyzed)

**Customer Expectations:**
- Immediate response (<2 minutes ideal)
- Ultra-concise (break into multiple short messages)
- Conversational tone
- Emojis acceptable (👋 ✅ 🎉 ⚙️)
- No formal greeting/signature

**Example Success Pattern (T002 - Add Team Members):**
```
Hey! 👋 I can help with that.

Go to Settings ⚙️ → Team → Invite Member

Or use the + icon in the top right

Need me to walk you through it?
```

**Length:** <300 characters per message
**Tone:** Casual, friendly, like texting a coworker
**Format:** Short bursts, emojis for clarity

**CRITICAL FINDING:** WhatsApp users **abandon conversations** if response >300 characters. Must break long answers into multiple messages.

### Web Form Channel (13 tickets analyzed)

**Customer Expectations:**
- Semi-formal (middle ground between email and WhatsApp)
- Scannable content (bullets, headers)
- Links to documentation
- Clear next steps
- Simple signature

**Example Success Pattern (T027 - Guest Permissions):**
```
Hi [Name],

To share a project with view-only access:

1. Open the project
2. Click "Share" (top right)
3. Enter professor's email
4. Select "Guest" role (view-only)
5. Send invitation

📚 Learn more: [Guest Permissions Guide]

Let me know if you need help!

- CloudFlow Support
```

**Length:** 100-300 words
**Tone:** Professional but approachable
**Format:** Bullets, numbered steps, occasional emoji (📚 only)

---

## Key Discovery #2: Immediate Escalation Triggers (18 Cases)

### Financial & Legal (7 cases)

| Ticket ID | Category | Reason for Escalation |
|-----------|----------|----------------------|
| T003 | Enterprise Pricing | Custom pricing requires sales negotiation |
| T009 | Billing Dispute | Double charge - needs payment system access |
| T015 | Educational Discount | Special pricing requires approval |
| T022 | Refund Request | Refund + angry sentiment = high-touch needed |
| T026 | Legal Threat | Lawyer representation - notify legal counsel immediately |
| T039 | Invoice Modification | Billing system access required |
| T054 | Trial Extension | Sales approval needed |

**Rule:** Any mention of "refund", "lawyer", "lawsuit", "double charge", or pricing negotiation → Escalate immediately

### Compliance & Security (5 cases)

| Ticket ID | Category | Reason for Escalation |
|-----------|----------|----------------------|
| T010 | SOC 2 Documentation | Compliance docs require legal team |
| T014 | GDPR Deletion | Data deletion must follow legal process |
| T020 | Security Incident | **P0** - Account breach, lock account immediately |
| T048 | EU Data Residency | Enterprise feature, sales discussion needed |
| T053 | Security Audit | Compliance team must handle questionnaire |
| T057 | GDPR DPA | Legal document, requires signature authority |

**Rule:** "GDPR", "data deletion", "breach", "security audit", "DPA" → Escalate (P0 if active security incident)

### Severe Negative Sentiment (3 cases)

| Ticket ID | Sentiment | Reason for Escalation |
|-----------|----------|----------------------|
| T004 | Angry | ALL CAPS, threats to churn, demands manager |
| T032 | Very Angry | Repeat customer (3+ contacts), severe frustration |
| T055 | Very Angry | Emoji-only angry message (😡😡😡) |

**Rule:** Sentiment score <0.3, ALL CAPS, profanity, churn threats, or repeat issues (3+) → Escalate immediately

### Enterprise Technical (3 cases)

| Ticket ID | Category | Reason for Escalation |
|-----------|----------|----------------------|
| T044 | SSO SAML Setup | Enterprise customer, blocking 200 user rollout |
| T048 | Data Residency | Enterprise compliance requirement |
| T060 | Scalability Consultation | 10,000+ tasks needs technical consultation |

**Rule:** Enterprise customers with blocking technical issues → Escalate to specialist (faster SLA)

---

## Key Discovery #3: Edge Cases (8+ Critical Cases)

### 1. Empty Message (T031)

**Problem:** Customer sends blank message on WhatsApp
**Agent Behavior:** Cannot proceed without input
**Solution Required:**
```
Hey! I received your message but it looks empty. How can I help you today?
```

**Test Case:** Handle null, empty string, whitespace-only messages

### 2. Non-English Language (T019)

**Problem:** Message in Japanese: "タスクの作成方法を教えてください"
**Current Limitation:** AI may not accurately respond in non-English
**Solution Options:**
1. Detect language → Respond in same language (if confident)
2. Detect language → Escalate with note "Language barrier - Japanese"
3. Use translation API (adds latency + cost)

**Recommendation:** Escalate non-English messages with detected language to human agents with translation support

**Test Cases:** Spanish, French, German, Japanese, Chinese, Arabic

### 3. Emoji-Only Message (T055)

**Problem:** Customer sends "😡😡😡" with no text
**Interpretation:** Extreme negative sentiment
**Solution Required:**
```
I can see you're frustrated. What's going on? I'm here to help make this right.
```

**Sentiment Analysis:** Must handle emoji-only inputs and derive sentiment from emoji meanings

### 4. Vague Single-Word Request (T049)

**Problem:** Customer sends just "help"
**Agent Behavior:** Too vague to provide specific answer
**Solution Required:**
```
I'm here to help! What can I assist you with today?

Common topics:
• Password reset
• How to use features
• Billing questions
• Technical issues

Or just tell me what you need!
```

**Test Cases:** "help", "hi", "hello", "question", "problem"

### 5. Repeat Customer - Escalation History (T032)

**Problem:** Customer contacted 3 times about same issue, now very angry
**Required Context:** Need to check customer history across ALL channels
**Solution Required:**
- Detect repeat ticket by customer ID + issue similarity
- Escalate automatically on 2nd repeat (3rd total contact)
- Pass full conversation history to human agent

**Database Requirement:** Store conversation history with issue categorization

### 6. Security Incident - Active Breach (T020)

**Problem:** Enterprise customer reports suspicious login from Russia
**Criticality:** P0 - Data may be compromised
**Solution Required:**
1. Immediate auto-response: "We're treating this as a security incident. Escalating to our security team immediately."
2. Create P0 ticket
3. Notify security team via Slack/PagerDuty
4. Lock account (if system permissions allow)
5. Follow up within 15 minutes

**Test Cases:** Keywords "breach", "hacked", "unauthorized access", "suspicious activity"

### 7. Legal Threat (T026)

**Problem:** Customer's lawyer threatens legal action
**Criticality:** P0 - Must notify legal counsel
**Solution Required:**
1. Immediate escalation (no AI response)
2. Flag as "legal threat" in ticket system
3. Notify legal@techcorp.com
4. Human agent responds within 1 hour

**Test Cases:** Keywords "lawyer", "attorney", "lawsuit", "legal action", "sue"

### 8. Meta Question - "Are You a Bot?" (T037)

**Problem:** Customer asks if they're talking to AI
**Ethical Requirement:** Must be transparent
**Solution Required:**
```
Yes, I'm an AI assistant here to help! I can answer questions about CloudFlow and help troubleshoot issues.

If you'd prefer to speak with a human team member, I can connect you right away. Let me know what works best!
```

**Transparency Policy:** Never pretend to be human. Offer human escalation proactively.

### Additional Edge Cases Discovered

9. **Self-Resolved (T040):** "Forget it, I figured it out"
   - Response: Acknowledge + offer future help
   - Don't re-open issue unnecessarily

10. **Positive Feedback (T046, T050):** "This app is amazing!"
    - Response: Thank warmly + encourage review
    - Opportunity for testimonial collection

11. **Feature Request (T021, T038, T043, T052):** Customer asks for non-existent feature
    - Response: Acknowledge + explain how to submit feature request
    - Log for product team

12. **Competitor Comparison (T042):** Asks about Asana, Monday.com
    - Response: Highlight CloudFlow differentiators
    - Escalate to sales for detailed comparison (high-value opportunity)

---

## Key Discovery #4: Tool Requirements

Based on 60-ticket analysis, the AI agent MUST have these tools:

### 1. `search_knowledge_base`
**Purpose:** Semantic search over product documentation
**Input:** User query (string)
**Output:** Relevant documentation sections (list of docs with relevance score)
**Success Criteria:**
- Find answer in <500ms
- Relevance score >0.7 for accurate answers
- Handle typos and synonyms
- Multimodal: support images in responses for visual guides

**Usage:** 40/60 tickets (67%) require knowledge base lookup

**Test Cases:**
- "How do I reset my password?" → Find password reset guide
- "GitHub not syncing" → Find GitHub integration troubleshooting
- "What's included in Professional?" → Find pricing/features page

### 2. `create_ticket`
**Purpose:** Log all interactions with channel metadata in CRM database
**Input:**
- customer_id (email or phone)
- channel (email | whatsapp | web_form)
- category (technical | how-to | billing | etc.)
- priority (low | medium | high | urgent | p0)
- issue_summary (string)
- full_message (string)
- sentiment_score (float 0-1)

**Output:** ticket_id (string)
**Success Criteria:**
- Creates ticket within 100ms
- Zero message loss (database ACID compliant)
- Ticket includes channel source for cross-channel tracking

**Usage:** EVERY ticket (100%) must be logged

### 3. `get_customer_history`
**Purpose:** Retrieve customer's interaction history **across ALL channels**
**Input:** customer_id (email as primary key, phone for WhatsApp)
**Output:** List of previous tickets with:
- Date/time
- Channel used
- Issue category
- Resolution status
- Sentiment over time

**Success Criteria:**
- Find customer in <200ms
- Aggregate from all channels (cross-channel continuity)
- Identify repeat issues

**Usage:** 15/60 tickets (25%) benefit from context (repeat customers, follow-ups)

**Critical for:**
- T032 (repeat angry customer)
- T040 (self-resolved - check what they figured out)
- Any customer switching channels mid-conversation

### 4. `escalate_to_human`
**Purpose:** Hand off to human agent with full context
**Input:**
- ticket_id
- escalation_reason (string)
- priority (urgent | high | p0)
- context_summary (string)
- sentiment_score (float)
- suggested_sla (hours)

**Output:** escalation_id + confirmation
**Success Criteria:**
- Creates escalation within 500ms
- Human agent receives full conversation transcript
- SLA clock starts immediately
- Customer receives acknowledgment

**Usage:** 18/60 tickets (30%) require escalation

**Escalation Message Template:**
```
Thank you for your patience. I'm connecting you with one of our support specialists who can assist you further with [specific issue].

A team member will reach out to you via email within [SLA timeframe] at [customer email].

Your ticket reference number is [TICKET-ID].
```

### 5. `send_response`
**Purpose:** Send response via appropriate channel with channel-specific formatting
**Input:**
- ticket_id
- message (string)
- channel (email | whatsapp | web_form)
- attachments (optional)

**Output:** delivery_status (sent | failed | queued)
**Success Criteria:**
- Channel-aware formatting:
  - Email: Add greeting, signature, HTML formatting
  - WhatsApp: Keep <300 chars, break into multiple messages if needed, support emojis
  - Web Form: Semi-formal, markdown formatting
- Delivery confirmation
- Retry logic for failures

**Usage:** EVERY response (100%)

### 6. `analyze_sentiment`
**Purpose:** Analyze customer message sentiment for escalation decisions
**Input:** message_text (string)
**Output:**
- sentiment_score (float 0-1, where 0=very negative, 1=very positive)
- confidence (float 0-1)
- detected_emotion (neutral | happy | frustrated | angry | confused)

**Success Criteria:**
- Detects anger/frustration with >90% accuracy
- Confidence >0.8 for escalation decisions
- Handles emoji sentiment (😡 = very negative)
- Handles ALL CAPS, profanity, exclamation marks

**Usage:** EVERY message (100%) - critical for auto-escalation

**Escalation Threshold:** sentiment_score <0.3 → Immediate escalation

### 7. `check_status_page`
**Purpose:** Check if there are ongoing system outages/incidents
**Input:** None (or optional: service_name)
**Output:**
- status (operational | degraded | outage)
- incidents (list of active incidents)
- last_updated (timestamp)

**Success Criteria:**
- Fast check (<200ms)
- Real-time incident data
- Integration with status.techcorp-cloudflow.com

**Usage:** 5/60 tickets (8%) related to performance/outage issues

**Example:**
- T025: "App is SO SLOW today" → Check status page before troubleshooting

### 8. `get_plan_tier`
**Purpose:** Get customer's subscription tier for feature availability and SLA
**Input:** customer_id (email)
**Output:**
- plan_tier (starter | professional | enterprise | trial)
- features_enabled (list)
- sla_hours (float)
- users_count (int)

**Success Criteria:**
- Retrieve in <100ms from CRM database
- Used to determine feature availability and escalation priority

**Usage:** 15/60 tickets (25%) involve plan-specific features or need tier context

**Examples:**
- T034: "Time tracking feature - where?" → Check plan (Starter doesn't have it)
- T044: Enterprise customer SSO issue → Faster escalation SLA

---

## Key Discovery #5: Channel Formatting Rules (CRITICAL)

### Email Formatting Engine

**Structure:**
```
Hi [FirstName],

[Empathy statement acknowledging their issue]

[Main content with numbered steps or bullets]

[Important warnings in bold]

[Next steps or offer for further help]

Best regards,
CloudFlow Support Team

📚 Related docs:
- [Link 1]
- [Link 2]
```

**Rules:**
- Always use first name in greeting
- Include greeting and signature (unlike WhatsApp)
- Use HTML formatting (bold, bullets, links)
- Length: 200-500 words acceptable
- Attach helpful documentation links
- Professional tone

### WhatsApp Formatting Engine

**Structure:**
```
Hey! 👋

[Ultra-concise answer]

[If needed: break into 2-3 short messages]

Let me know if you need more help! 😊
```

**Rules:**
- NO formal greeting/signature
- Break responses >300 chars into multiple messages
- Use emojis sparingly (👋 ✅ 🎉 ⚙️ 😊)
- Use arrows for navigation: Settings → Team
- Conversational tone ("Hey" not "Dear")
- Maximum 1600 chars total (WhatsApp API limit)

### Web Form Formatting Engine

**Structure:**
```
Hi [FirstName],

[Brief intro acknowledging question]

[Numbered steps or bullets]

📚 Learn more: [Link]

Let me know if you need more help!

- CloudFlow Support
```

**Rules:**
- Semi-formal (middle ground)
- Use markdown formatting (bullets, numbered lists)
- Include documentation link
- Simple signature (just "- CloudFlow Support")
- Length: 100-300 words

---

## Key Discovery #6: Escalation Decision Tree

```mermaid
graph TD
    A[New Message] --> B{Check Sentiment}
    B -->|Score <0.3| C[ESCALATE - Angry Customer]
    B -->|Score >=0.3| D{Check Keywords}

    D -->|refund, lawyer, breach| C
    D -->|No red flags| E{Check Category}

    E -->|Billing/Legal/Security| C
    E -->|Technical/How-to| F{Search Knowledge Base}

    F -->|Found answer, confidence >0.7| G[AI Response]
    F -->|No answer or confidence <0.7| H{Check Attempt Count}

    H -->|First attempt| I[Ask clarifying question]
    H -->|2nd attempt, still unclear| C

    G --> J{Customer Satisfied?}
    J -->|Yes or no response| K[Close Ticket]
    J -->|No, frustrated| C
    J -->|Follow-up question| F
```

**Key Decision Points:**

1. **Sentiment Check** (First line of defense)
   - Score <0.3 → Escalate immediately
   - ALL CAPS → Escalate
   - Profanity → Escalate

2. **Keyword Triggers** (Automatic escalation)
   - Financial: "refund", "charge", "billing dispute", "money back"
   - Legal: "lawyer", "attorney", "lawsuit", "legal action"
   - Security: "breach", "hacked", "unauthorized"
   - Compliance: "GDPR", "data deletion", "SOC 2", "audit"

3. **Category-Based** (Rule-based escalation)
   - Billing disputes → Always escalate
   - Legal/Compliance → Always escalate
   - Enterprise technical (SSO, data residency) → Escalate

4. **Confidence Threshold** (Knowledge-based escalation)
   - KB relevance score <0.7 → Try once more or escalate
   - After 2 failed attempts → Escalate
   - Can't find answer after 3 searches → Escalate

5. **Conversation Length** (Prevent loops)
   - >6 messages without resolution → Escalate
   - Customer repeats same question 3 times → Escalate

6. **Repeat Customer** (Historical context)
   - Same issue reported 2+ times → Escalate on next occurrence
   - Customer has 5+ tickets in 30 days → Flag for proactive outreach

---

## Key Discovery #7: Cross-Channel Customer Identification

### Problem Statement
Customer starts conversation on email, then switches to WhatsApp mid-issue. Agent must maintain context.

**Example Scenario:**
1. T001: sarah.johnson@techstartup.com emails about password reset (Monday 9am)
2. T005: +1-415-555-XXXX WhatsApps "tasks disappeared" (Monday 2pm)
3. **Question:** Is this the same customer? How do we know?

### Solution Requirements

**Primary Customer ID:** Email address (most stable)
**Secondary ID:** Phone number (for WhatsApp-only users)

**Linking Strategy:**
1. When WhatsApp message comes in, check if phone number is linked to any account
2. If not linked, search recent tickets for similar issue or name match
3. If found, link phone → email in CRM
4. Future messages from that phone inherit email-linked history

**Database Schema Required:**
```sql
CREATE TABLE customers (
    customer_id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    phone VARCHAR UNIQUE,
    first_name VARCHAR,
    last_name VARCHAR,
    plan_tier VARCHAR,
    created_at TIMESTAMP
);

CREATE TABLE tickets (
    ticket_id UUID PRIMARY KEY,
    customer_id UUID REFERENCES customers(customer_id),
    channel VARCHAR NOT NULL, -- email | whatsapp | web_form
    message_text TEXT,
    sentiment_score FLOAT,
    category VARCHAR,
    priority VARCHAR,
    resolution_status VARCHAR, -- open | resolved | escalated
    created_at TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE TABLE messages (
    message_id UUID PRIMARY KEY,
    ticket_id UUID REFERENCES tickets(ticket_id),
    sender VARCHAR NOT NULL, -- customer | agent | ai
    message_text TEXT,
    channel VARCHAR,
    sent_at TIMESTAMP
);
```

**Cross-Channel Continuity Test Cases:**
- Customer emails, then WhatsApps same issue → Agent recognizes repeat
- Customer uses different email than account email → Agent asks for confirmation
- Customer switches mid-conversation → Agent: "I see you emailed us earlier about X. Is this related?"

---

## Key Discovery #8: Performance Baseline

### Speed Requirements (from company profile)

| Metric | Target | Current (Human) | AI Capability |
|--------|--------|-----------------|---------------|
| First Response Time | <5 minutes | 4-6 hours | <30 seconds ✅ |
| Resolution Time (Simple) | <15 minutes | 24-48 hours | <2 minutes ✅ |
| Resolution Time (Complex) | <4 hours | 24-48 hours | Escalate (humans handle) |
| Availability | 99.9% (24/7) | 9am-6pm CST only | 24/7 ✅ |

**AI Advantage:** 48x faster first response (6 hours → 30 seconds)

### Throughput Requirements

| Metric | Current | With AI |
|--------|---------|---------|
| Daily Ticket Volume | 200 | 200 |
| Tickets Handled by AI | 0 | 140 (70%) |
| Tickets Escalated | 200 | 60 (30%) |
| Cost per Ticket | $15 (human) | $0.05 (AI) for 70% |
| Annual Savings | $0 | ~$700,000 (with AI handling 70%) |

### Latency Budget

| Operation | Target Latency | Rationale |
|-----------|----------------|-----------|
| Sentiment Analysis | <50ms | Real-time decision making |
| Knowledge Base Search | <500ms | User expects quick answer |
| Ticket Creation | <100ms | Database write operation |
| Customer History Lookup | <200ms | Database read with index |
| Channel Formatting | <50ms | Simple text transformation |
| Total Response Time | <1.5 seconds | Industry standard for chat |

**99th Percentile Target:** <3 seconds end-to-end

---

## Incubation Phase Deliverables (Checklist)

### Phase 1: Exploration ✅ (Complete)
- [x] Analyzed 60 sample tickets across all channels
- [x] Identified 8+ critical edge cases
- [x] Documented channel-specific response patterns
- [x] Defined escalation decision tree
- [x] Calculated target resolution rate (70%)
- [x] Discovered cross-channel continuity requirement

### Phase 2: Prototype Core Loop (Next)
- [ ] Build simple Python prototype
- [ ] Implement message normalization (all channels → standard format)
- [ ] Implement knowledge base search (mock or use embeddings)
- [ ] Implement channel-specific response formatting
- [ ] Test with 10 sample tickets per channel (30 total)

### Phase 3: Add Memory and State (Next)
- [ ] Add conversation history tracking
- [ ] Implement customer identification logic
- [ ] Add sentiment analysis (use existing library)
- [ ] Track resolution status
- [ ] Test cross-channel conversation continuity

### Phase 4: Build MCP Server (Next)
- [ ] Define 8 tool signatures (Python decorators)
- [ ] Implement mock versions of each tool
- [ ] Test tool calling from Claude
- [ ] Document tool usage patterns

### Phase 5: Define Agent Skills (Next)
- [ ] Create skills manifest (YAML)
- [ ] Define success criteria per skill
- [ ] Document working system prompt
- [ ] Test with all 60 tickets
- [ ] Measure resolution rate

---

## Risks and Mitigation

### Risk 1: Knowledge Base Accuracy
**Risk:** AI finds wrong documentation or misinterprets
**Probability:** Medium
**Impact:** High (wrong information damages trust)
**Mitigation:**
- Use relevance score threshold (>0.7)
- Include disclaimer: "Based on our documentation..."
- Easy escalation path if customer disagrees

### Risk 2: Sentiment Analysis False Positives
**Risk:** AI escalates unnecessarily, overwhelming human agents
**Probability:** Medium
**Impact:** Medium (wastes human time, higher cost)
**Mitigation:**
- Tune sentiment threshold carefully (0.3 may be too strict)
- A/B test different thresholds
- Monitor escalation rate (target 25-30%, not 50%)

### Risk 3: Cross-Channel Identification Failures
**Risk:** Can't link customer across channels, lose context
**Probability:** High (phone numbers not always in account)
**Impact:** Medium (customer has to repeat themselves)
**Mitigation:**
- Prompt customer: "Are you emailing from your account email?"
- Use fuzzy matching on issue description
- Ask confirming questions if unsure

### Risk 4: WhatsApp Message Length
**Risk:** AI generates 500-word response, customer abandons
**Probability:** High (without explicit formatting rules)
**Impact:** High (defeats purpose of channel choice)
**Mitigation:**
- Hard limit: 300 chars per message
- Auto-split long responses into multiple messages
- Monitor WhatsApp abandonment rate

### Risk 5: Non-English Language Handling
**Risk:** Customer messages in Spanish, AI responds in English
**Probability:** Medium (15% of WhatsApp is non-English per edge case notes)
**Impact:** High (customer feels ignored)
**Mitigation:**
- Implement language detection (simple library)
- Escalate non-English with detected language tag
- Future: Add multi-language support in Phase 2

---

## Next Steps (Immediate Actions)

1. **Create Prototype** (Phase 2)
   - Build core interaction loop in Python
   - Test with 10 tickets per channel (30 total)
   - Validate response formatting per channel

2. **Define MCP Tools** (Phase 4)
   - Write tool signatures with type hints
   - Mock implementations for testing
   - Document expected inputs/outputs

3. **Build Escalation Logic** (Phase 2)
   - Implement decision tree from Key Discovery #6
   - Test with 18 escalation cases
   - Measure false positive/negative rate

4. **Create System Prompt** (Phase 5)
   - Draft initial system prompt with channel awareness
   - Include escalation rules explicitly
   - Test prompt with Claude on sample tickets

5. **Crystallize Specification** (Phase 5)
   - Write formal spec document
   - Define acceptance criteria per feature
   - Get stakeholder sign-off

---

## Open Questions (Need Clarification)

1. **Multi-language Support:** Do we escalate all non-English or support Spanish/French?
   - **Recommendation:** Start with escalation, add languages in v2

2. **Channel Response Time SLA:** Different SLA per channel?
   - Email: <5 minutes acceptable?
   - WhatsApp: <30 seconds expected?
   - **Recommendation:** Same SLA (1-2 minutes) but WhatsApp feels faster

3. **Escalation Message:** Should AI send holding message or wait for human?
   - **Recommendation:** AI sends immediate acknowledgment with SLA expectation

4. **Knowledge Base Format:** Markdown? HTML? PDF?
   - **Recommendation:** Markdown with embeddings for semantic search

5. **Customer Identification:** Require account email or allow any email?
   - **Recommendation:** Link any email to customer record, confirm identity

---

**Document Status:** Phase 1 Complete ✅
**Next Milestone:** Build working prototype (Phase 2)
**Estimated Time:** 4-5 hours for Phase 2

---

*This discovery log will be continuously updated as we prototype and test in Phases 2-5.*
