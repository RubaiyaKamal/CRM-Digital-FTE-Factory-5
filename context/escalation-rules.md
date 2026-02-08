# CloudFlow AI Agent - Escalation Rules

**Version:** 1.0
**Last Updated:** 2026-02-06
**Owner:** Support Operations Team

---

## Escalation Philosophy

**Core Principle:** Escalation is **success**, not failure.

The AI agent should escalate to human agents when:
1. The customer will get a better outcome with human intervention
2. The situation requires empathy, judgment, or relationship building
3. The AI lacks sufficient context or knowledge to provide accurate guidance
4. The situation has legal, financial, or compliance implications

**Better to escalate early than provide inaccurate information or frustrate the customer.**

---

## Immediate Escalation (No AI Response)

These scenarios require **immediate** handoff to human agents without AI attempting to respond:

### Category 1: Financial & Legal

1. **Refund Requests**
   - Customer explicitly asks for refund
   - Keywords: "refund", "money back", "charge back", "chargeback"
   - Reason: Requires payment processing and judgment call on eligibility

2. **Billing Disputes**
   - Claims of incorrect charges
   - Unauthorized charges
   - Double billing
   - Keywords: "incorrect charge", "didn't authorize", "charged wrong amount"
   - Reason: Requires access to payment processor and authority to issue credits

3. **Legal Threats or Demands**
   - Mentions lawyers, lawsuits, or legal action
   - Keywords: "lawyer", "attorney", "sue", "legal action", "lawsuit", "court"
   - Reason: Must be handled by legal team with proper documentation

4. **Contract Negotiations**
   - Enterprise plan custom pricing
   - Special terms or SLA modifications
   - Volume discounts
   - Keywords: "custom contract", "negotiate terms", "enterprise pricing"
   - Reason: Requires sales team authority and CRM context

### Category 2: Security & Compliance

5. **Security Incidents**
   - Reported security vulnerabilities
   - Suspected account breach
   - Unauthorized access
   - Data leaks or exposure
   - Keywords: "hacked", "security issue", "vulnerability", "breach", "unauthorized access"
   - Reason: Requires immediate security team investigation

6. **Data Deletion Requests (GDPR/CCPA)**
   - Right to be forgotten requests
   - Data subject access requests
   - Keywords: "delete my data", "GDPR request", "right to be forgotten", "data deletion"
   - Reason: Legal compliance requirements and identity verification needed

7. **Compliance Questions**
   - SOC 2 audit requests
   - Compliance certification questions
   - Data residency requirements
   - Keywords: "SOC 2", "compliance", "audit", "data residency", "where is data stored"
   - Reason: Requires legal/compliance team review

### Category 3: VIP & Enterprise

8. **Enterprise Customers**
   - Accounts on Enterprise plan with SLA
   - Check `customer_tier` field in database
   - Reason: SLA commitments require faster response and dedicated support

9. **High-Value Opportunities**
   - Upgrade interest from accounts >100 users
   - Keywords: "upgrade to enterprise", "add 50+ users", "enterprise features"
   - Reason: Sales team should nurture high-value deals

### Category 4: Severe Sentiment

10. **Extreme Negative Sentiment**
    - Profanity or abusive language
    - Threats to switch to competitor
    - Multiple exclamation points with angry tone
    - All caps messages indicating frustration
    - Keywords: "cancel my account", "switching to [competitor]", "worst service", "[profanity]"
    - Sentiment Score: <0.2 on scale of 0-1
    - Reason: Human empathy and de-escalation skills needed

11. **Repeated Failures**
    - Customer has contacted support 3+ times about same issue
    - Check conversation history for repeat tickets
    - Reason: Pattern indicates complex problem requiring senior agent

---

## Conditional Escalation (AI Tries First, Then Escalates)

These scenarios allow the AI to **attempt** resolution but escalate if:
- AI cannot find relevant documentation
- Customer is unsatisfied with AI response
- Situation becomes more complex than initially understood

### Category 5: Technical Issues

12. **Critical Outages**
    - User reports complete inability to access product
    - Error messages indicating system-wide issues
    - Keywords: "can't login", "site is down", "nothing is loading"
    - **AI Action:** Check status page first
    - **Escalate if:** Status page shows ongoing incident OR user has unique issue not on status page

13. **Data Loss or Corruption**
    - Tasks disappeared
    - Projects not loading
    - Data showing incorrectly
    - Keywords: "lost my tasks", "data is gone", "everything disappeared"
    - **AI Action:** Ask clarifying questions (did you check archive? filter settings?)
    - **Escalate if:** User confirms data genuinely missing

14. **Integration Failures**
    - Slack/GitHub/Jira integrations not working
    - API errors
    - Keywords: "integration broken", "Slack not working", "API error"
    - **AI Action:** Provide standard troubleshooting (re-authorize, check permissions)
    - **Escalate if:** Standard steps don't resolve after 2 attempts

15. **Performance Issues**
    - Extremely slow loading times
    - Timeouts
    - Keywords: "very slow", "timing out", "taking forever to load"
    - **AI Action:** Suggest browser troubleshooting and check status page
    - **Escalate if:** Issue persists after clearing cache and trying different browser

### Category 6: Account Management

16. **Account Access Issues** (Non-password)
    - Locked accounts
    - Deactivated users
    - SSO configuration problems
    - **AI Action:** Explain common causes and self-service options
    - **Escalate if:** User is admin and needs manual unlock OR SSO config issue

17. **Ownership Transfer**
    - Need to transfer workspace to different owner
    - Change billing admin
    - Keywords: "transfer ownership", "change owner", "new admin"
    - **AI Action:** Explain process and requirements
    - **Escalate if:** User needs help executing the transfer

18. **Bulk Operations**
    - Need to bulk delete/move/update tasks
    - Import large datasets
    - Keywords: "bulk", "import", "mass update", "delete all"
    - **AI Action:** Provide documentation on bulk features
    - **Escalate if:** Request exceeds product capabilities OR requires API/custom script

### Category 7: Complex How-To Questions

19. **Multi-Step Workflows**
    - Questions requiring 5+ steps to answer
    - Complex automation setup
    - Custom field configurations
    - **AI Action:** Provide step-by-step guidance
    - **Escalate if:** User is confused after 2 rounds of clarification OR workflow is edge case not in docs

20. **Feature Limitations**
    - Asking to do something the product doesn't support
    - Workarounds needed
    - Keywords: "can I do [unusual thing]", "is there a way to"
    - **AI Action:** Explain limitation and suggest alternatives
    - **Escalate if:** User pushes back or needs custom solution

21. **Mobile App Issues** (Complex)
    - App crashes frequently
    - Sync issues
    - Features not working on mobile
    - **AI Action:** Suggest standard troubleshooting (update app, reinstall)
    - **Escalate if:** Issue persists after standard fixes

### Category 8: Feedback & Requests

22. **Feature Requests**
    - User asks for new features
    - Suggestions for improvements
    - Keywords: "can you add", "would be great if", "feature request"
    - **AI Action:** Thank user and explain how to submit feedback
    - **Escalate if:** User is Enterprise customer OR feature request is time-sensitive for their business

23. **Bug Reports**
    - User reports unexpected behavior
    - Reproducible issues
    - Keywords: "bug", "not working as expected", "used to work"
    - **AI Action:** Gather details (steps to reproduce, screenshots, environment)
    - **Escalate if:** Confirmed bug OR user is frustrated and wants acknowledgment from team

---

## Escalation Triggers (Automated)

### Sentiment Analysis Thresholds

Monitor ongoing conversation for these triggers:

- **Negative Sentiment Score <0.3:** Escalate immediately
- **Frustration Indicators:**
  - Multiple question marks ("????")
  - Sarcasm or passive aggression
  - Repeated rephrasing of same question
  - Statements like "this is ridiculous" or "waste of my time"

### Conversation Metrics

- **Message Count:** If conversation exceeds 6 messages without resolution, escalate
- **Clarification Loops:** If AI asks for clarification 3+ times, escalate
- **Time Spent:** If conversation spans >15 minutes without resolution, escalate

### Knowledge Gaps

Escalate when:
- AI searches documentation 3+ times without finding relevant answer
- Confidence score <0.6 for retrieved documentation
- User question involves product areas not covered in knowledge base
- User mentions a feature/product area unfamiliar to AI

### Explicit Customer Request

Always honor these requests:
- "I want to speak to a human"
- "Connect me with your team"
- "Can I talk to someone real?"
- "I need a person"
- "This isn't helpful, I need real support"

---

## Escalation Handoff Process

### Information to Collect Before Escalating

**Minimum Required:**
1. Customer name and email
2. Account/Company name
3. Plan tier (Starter, Professional, Enterprise)
4. Issue summary (1-2 sentences)
5. Customer sentiment (Positive, Neutral, Negative, Angry)
6. Conversation history (full transcript)

**Additional Context (if available):**
7. Steps already attempted
8. Error messages or screenshots
9. Browser/device information
10. Related tickets or previous interactions
11. Priority level (Low, Medium, High, Urgent)

### Escalation Message to Customer

**Template:**

```
Thank you for your patience. I'm connecting you with one of our support specialists who can assist you further with [specific issue].

A team member will reach out to you via email within [timeframe based on plan tier] at [customer email].

Your ticket reference number is [TICKET-ID]. Please mention this if you need to follow up.

Is there anything else I can help you with in the meantime?
```

**Timeframe Commitments:**
- **Starter:** Within 24 hours
- **Professional:** Within 12 hours
- **Enterprise:** Within 4 hours

### Internal Escalation Handoff

**Create ticket in support system with:**

**Subject:** [ESCALATED] [Category] - [Brief description]

**Priority:**
- **P0 (Urgent):** Security incidents, complete outages, legal threats
- **P1 (High):** Enterprise customers, billing disputes, severe negative sentiment
- **P2 (Medium):** Technical issues, account access, complex how-to
- **P3 (Low):** Feature requests, feedback, minor bugs

**Tags:**
- `ai-escalation`
- Channel (email, whatsapp, web_form)
- Category (billing, technical, account, etc.)
- Sentiment (positive, neutral, negative, angry)

**Description:**
```
ESCALATION FROM: AI Agent
ESCALATION REASON: [Reason]
CUSTOMER: [Name] ([Email])
ACCOUNT: [Company name]
PLAN: [Starter/Professional/Enterprise]
SENTIMENT: [Positive/Neutral/Negative/Angry]

ISSUE SUMMARY:
[2-3 sentence summary]

CONVERSATION TRANSCRIPT:
[Full conversation history with timestamps]

ATTEMPTED SOLUTIONS:
- [What AI tried]
- [What didn't work]

NEXT STEPS NEEDED:
[What human agent should focus on]
```

---

## Do NOT Escalate (Handle with AI)

These should **never** be escalated - AI should always attempt resolution:

### Simple How-To Questions
- "How do I create a task?"
- "Where do I find my projects?"
- "How do I invite team members?"
- "How do I attach a file?"

**Reason:** Well-documented, straightforward features

### Password Resets
- "I forgot my password"
- "Password reset link not working"
- "Can't login"

**Reason:** Self-service flow available, AI can guide through process

### Account Settings
- "How do I change my email?"
- "How do I update my profile?"
- "How do I change notification settings?"

**Reason:** Settings pages are straightforward with good UX

### Basic Billing Information
- "What's included in Professional plan?"
- "How much does Enterprise cost?"
- "What's the difference between Starter and Professional?"

**Reason:** Pricing page has all details, can link directly (DO NOT quote custom Enterprise pricing)

### Status/Availability Questions
- "Is the service down?"
- "Are you having issues?"
- "Is this a known bug?"

**Reason:** Can check status page programmatically

### Documentation Links
- "Where can I find documentation on [feature]?"
- "Do you have tutorials?"
- "Is there a video guide?"

**Reason:** Knowledge base search and direct links available

---

## Special Handling Rules

### After-Hours (6 PM - 9 AM CST, Weekends, Holidays)

- **Default behavior:** Inform customer of business hours and provide self-service resources
- **Exception:** Enterprise customers with P0/P1 issues → Page on-call engineer
- **Set expectations:** "Our team will respond within [SLA timeframe] on the next business day"

### Language Barriers

- If customer messages in non-English language:
  - Respond in same language if AI has translation capability
  - If unclear or low confidence, escalate with note: "Language barrier - may need translator"
  - Do NOT use auto-translate for legal, financial, or contract discussions

### Repeat Customers

- Check interaction history for customer
- If customer has had 5+ interactions in last 30 days, flag for proactive outreach
- If same issue reported 2+ times, escalate on second occurrence
- Build rapport - reference previous conversations when appropriate

### VIP Program

**Automatic VIP status for:**
- Enterprise tier customers
- Accounts with 200+ users
- Customers who are brand advocates (speak at conferences, write case studies)
- Churned customers attempting to return

**VIP Treatment:**
- Priority routing to senior agents
- Faster SLA (cut standard timeframes in half)
- More lenient escalation thresholds
- Account manager CC'd on all tickets

---

## Metrics & Monitoring

### AI Agent Escalation Metrics (Target KPIs)

- **Escalation Rate:** <25% (75%+ tickets resolved by AI)
- **False Escalations:** <5% (tickets that shouldn't have been escalated)
- **Missed Escalations:** <2% (tickets that should have been escalated but weren't)
- **Customer Satisfaction After Escalation:** >4.2/5.0
- **Time to Escalation Decision:** <2 minutes

### Weekly Review

Support team reviews:
1. All escalated tickets from previous week
2. Identify patterns (what's causing most escalations?)
3. Update escalation rules or improve documentation
4. Provide feedback to AI training team

---

## Edge Cases & Judgment Calls

When in doubt, **err on the side of escalation**. These guidelines help:

### Ambiguous Situations

**"This isn't working"** - Not clear what "this" refers to
- **AI Action:** Ask clarifying question: "I want to help! Can you tell me what specifically isn't working?"
- **Escalate if:** After 2 clarification attempts, still unclear

**Mixed Messages** - Customer says one thing but tone suggests another
- Example: "It's fine, don't worry about it" but tone is clearly frustrated
- **AI Action:** Acknowledge and offer continued help: "I want to make sure this is fully resolved for you. Are you certain everything is working as expected?"
- **Escalate if:** Any indication of suppressed frustration

**Uncertainty About Escalation Category**
- If unsure whether situation fits escalation rules, escalate with note: "Uncertain classification - needs human review"
- Better safe than sorry

---

## Training & Continuous Improvement

### Feedback Loop

1. **Human agents mark escalations:**
   - ✅ Good escalation (needed human touch)
   - ❌ Unnecessary escalation (AI could have handled)
   - ⚠️ Missed escalation (should have escalated earlier)

2. **Monthly calibration:**
   - Review edge cases and add to this document
   - Update AI training based on patterns
   - Celebrate great escalation decisions

3. **Documentation updates:**
   - When human agents answer questions not in docs, add to knowledge base
   - Reduce future escalations by improving self-service content

---

## Quick Reference Checklist

Before escalating, ask:
- [ ] Did I search the knowledge base thoroughly?
- [ ] Did I attempt standard troubleshooting?
- [ ] Have I asked clarifying questions if context is unclear?
- [ ] Is this explicitly listed as immediate escalation?
- [ ] Is the customer frustrated or sentiment negative?
- [ ] Have we exchanged 6+ messages without resolution?
- [ ] Am I confident I have the right answer?
- [ ] Would a human agent provide significantly better outcome?

If **ANY** of these suggest escalation, escalate.

---

**Document Owner:** Support Operations Team
**Review Cadence:** Monthly
**Last Review:** 2026-02-06
**Next Review:** 2026-03-06

*For questions about these escalation rules, contact support-ops@techcorp.com*
