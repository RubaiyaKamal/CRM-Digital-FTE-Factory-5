# WhatsApp Channel Integration Setup Guide

This guide walks you through setting up the WhatsApp channel for the CRM Digital FTE Factory using Twilio's WhatsApp Business API.

## Prerequisites

1. Twilio account with WhatsApp enabled
2. WhatsApp Business profile (or use Twilio Sandbox for testing)
3. PostgreSQL database running
4. Docker and Docker Compose installed
5. Public HTTPS endpoint for webhooks (ngrok for local dev)

---

## Setup Options

### Option A: Twilio Sandbox (Recommended for Testing)

**Best for:** Quick testing, hackathons, POC
**Limitations:** Requires users to send "join [code]" first, 24-hour session limit
**Time:** 10 minutes
**Cost:** Free

### Option B: Twilio Production WhatsApp Number

**Best for:** Production deployment
**Requirements:** Business verification, approved templates
**Time:** 2-7 days for approval
**Cost:** $25/month + per-message fees

---

## Option A: Twilio Sandbox Setup (Quick Start)

### Step 1: Twilio Account Setup

#### 1.1 Create Twilio Account
1. Go to [Twilio Console](https://www.twilio.com/console)
2. Sign up for free trial (includes $15 credit)
3. Verify your phone number

#### 1.2 Get Credentials
1. In Twilio Console, go to **Account > API Keys & Tokens**
2. Copy your **Account SID** and **Auth Token**
3. Keep these secure - you'll add them to `.env`

#### 1.3 Enable WhatsApp Sandbox
1. Navigate to **Messaging > Try it out > Send a WhatsApp message**
2. Note your sandbox number (e.g., `+1 415 523 8886`)
3. Note your sandbox code (e.g., `join capital-party`)

### Step 2: Join Sandbox (For Each Test User)

Send a WhatsApp message from your phone:
1. Add contact: `+1 415 523 8886` (or your sandbox number)
2. Send message: `join capital-party` (use your specific code)
3. You'll receive confirmation: "Sandbox: You are all set!"

**Note:** Each tester must do this. Sandbox sessions expire after 24 hours of inactivity.

### Step 3: Configure Webhook URL

#### 3.1 Expose Local Development Server

Using ngrok (recommended for local testing):

```bash
# Install ngrok
# Download from https://ngrok.com/download

# Start ngrok tunnel to port 8000
ngrok http 8000
```

You'll see output like:
```
Forwarding https://abc123.ngrok.io -> http://localhost:8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

#### 3.2 Set Webhook in Twilio

1. In Twilio Console, go to **Messaging > Settings > WhatsApp sandbox settings**
2. Under "When a message comes in":
   - URL: `https://abc123.ngrok.io/webhooks/whatsapp`
   - Method: `POST`
3. Click **Save**

### Step 4: Environment Configuration

Update `.env` file:

```bash
# Twilio (WhatsApp)
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_PHONE_NUMBER=+14155238886
WHATSAPP_PHONE_NUMBER=whatsapp:+14155238886
WHATSAPP_MOCK=false
```

**Important:** The sandbox number is typically `+1 415 523 8886` but check your Twilio console.

### Step 5: Install Dependencies & Start Services

```bash
# Install Python dependencies
pip install -r requirements.txt

# Start Docker services
docker-compose up -d

# Check logs
docker-compose logs -f api worker
```

### Step 6: End-to-End Test

#### 6.1 Send Test Message

From your WhatsApp (after joining sandbox), send:
```
Hello, I need help with my account
```

#### 6.2 Monitor Logs

```bash
# Terminal 1: API logs
docker-compose logs -f api

# Terminal 2: Worker logs
docker-compose logs -f worker
```

Expected flow:
```
[API] POST /webhooks/whatsapp - 200
[API] Webhook received: channel=whatsapp customer=+14155551234
[Worker] Processing ticket for whatsapp channel
[Worker] Agent response generated
[Worker] Sending WhatsApp message to +14155551234
```

#### 6.3 Receive AI Response

Within 5-10 seconds, you should receive an AI-generated response in WhatsApp.

---

## Option B: Production WhatsApp Number Setup

### Step 1: Request WhatsApp Business Access

1. Go to **Messaging > Senders > WhatsApp senders**
2. Click **Add a WhatsApp sender**
3. Follow the business verification process
4. Submit required documents:
   - Business registration
   - Tax ID
   - Address verification
   - Website/social media

**Timeline:** 2-7 business days for approval

### Step 2: Create Message Templates

WhatsApp requires approved templates for the first message to users.

#### 2.1 Create Template in Twilio

1. Go to **Messaging > Content > Content templates**
2. Click **Create new template**
3. Example template:

**Name:** `customer_support_greeting`
**Category:** `UTILITY`
**Language:** `English (US)`
**Body:**
```
Hello {{1}},

Thank you for contacting {{2}} support. We're here to help!

How can we assist you today?
```

**Variables:**
- `{{1}}` - Customer name
- `{{2}}` - Company name

#### 2.2 Submit for Approval

1. Submit template to WhatsApp for review
2. Wait for approval (usually 24-48 hours)
3. Once approved, note the **Content SID** (starts with `HX...`)

### Step 3: Update Code for Templates

Modify `src/workers/response_handler.py` to use templates for first contact:

```python
from src.channels.whatsapp_client import send_whatsapp_template

# Check if this is first message to customer
is_first_message = await _check_first_message(conversation_id)

if channel_name == "whatsapp" and is_first_message:
    # Use approved template
    success = await send_whatsapp_template(
        to=customer_identifier,
        template_sid="HXa1b2c3...",  # Your template SID
        content_variables={
            "1": customer_name,
            "2": "Your Company"
        }
    )
else:
    # Normal freeform message
    success = await adapter.send(customer_identifier, formatted, **send_kwargs)
```

### Step 4: Production Webhook

Use a production domain (not ngrok):

1. Deploy API to production server with HTTPS
2. Configure webhook in Twilio:
   - URL: `https://your-domain.com/webhooks/whatsapp`
   - Method: `POST`

---

## Database Verification

Check that WhatsApp messages create proper records:

```bash
# Check customers
docker exec crm_postgres psql -U crm_user -d crm_fte -c \
  "SELECT phone, created_at FROM customers WHERE phone LIKE '+1415%';"

# Check conversations
docker exec crm_postgres psql -U crm_user -d crm_fte -c \
  "SELECT id, channel, status FROM conversations WHERE channel = 'whatsapp';"

# Check messages with metadata
docker exec crm_postgres psql -U crm_user -d crm_fte -c \
  "SELECT role, content, metadata FROM messages
   WHERE conversation_id IN (SELECT id FROM conversations WHERE channel = 'whatsapp')
   ORDER BY created_at DESC LIMIT 5;"
```

Expected metadata:
```json
{
  "twilio_message_sid": "SMa1b2c3d4e5...",
  "twilio_to": "whatsapp:+14155238886",
  "twilio_from": "whatsapp:+14155551234",
  "profile_name": "John Doe",
  "num_media": "0"
}
```

---

## Dashboard Verification

1. Open: http://localhost:3003/dashboard/conversations
2. Should see WhatsApp conversations with green "REAL" badge
3. Click to view - full message history
4. Customer name from WhatsApp profile should display

---

## Troubleshooting

### Issue: "Webhook validation failed"

**Error:** `403 Invalid Twilio signature`

**Causes:**
1. Wrong `TWILIO_AUTH_TOKEN` in environment
2. Webhook URL mismatch (ngrok changed)
3. Request body modified by middleware

**Solution:**
```bash
# Verify auth token
echo $TWILIO_AUTH_TOKEN

# Check webhook URL in Twilio Console
# Ensure it exactly matches your ngrok URL

# Temporarily disable validation for testing (not recommended for production)
TWILIO_AUTH_TOKEN="" docker-compose up -d
```

---

### Issue: "Message not received by AI"

**Symptoms:** Send WhatsApp message, but no response

**Debugging steps:**

1. Check ngrok is running:
   ```bash
   curl https://your-ngrok-url.ngrok.io/health
   # Should return {"status": "healthy"}
   ```

2. Check webhook received:
   ```bash
   docker-compose logs -f api | grep whatsapp
   # Should show POST /webhooks/whatsapp - 200
   ```

3. Check worker processing:
   ```bash
   docker-compose logs -f worker
   # Should show ticket processing
   ```

4. Check Twilio debugger:
   - Go to **Monitor > Logs > Errors & Warnings**
   - Look for webhook failures

---

### Issue: "Message sent but not received on phone"

**Possible causes:**

1. **Sandbox not joined:**
   - Re-send `join [code]` to sandbox number
   - Check confirmation message received

2. **Session expired (24 hours):**
   - Sandbox sessions expire after 24h inactivity
   - Re-join by sending `join [code]` again

3. **Phone number format incorrect:**
   ```bash
   # Check logs for formatted number
   docker-compose logs worker | grep "Sent WhatsApp"
   # Should show: "Sent WhatsApp message to whatsapp:+14155551234"
   ```

4. **Twilio account suspended/trial limits:**
   - Check Twilio Console > Account > Status
   - Trial accounts can only send to verified numbers

---

### Issue: "Invalid 'To' phone number"

**Error:** `[21211] Invalid To phone number`

**Solution:**
Ensure phone number is E.164 format:
- ✅ Correct: `+14155551234`
- ❌ Wrong: `4155551234` (missing +)
- ❌ Wrong: `+1 (415) 555-1234` (spaces/parens)

The `whatsapp_client.py` auto-formats, but verify in logs.

---

### Issue: "Permission denied"

**Error:** `[21408] Permission to send an SMS/MMS has not been enabled`

**For Sandbox:**
- Ensure user sent `join [code]` first
- Check in Twilio Console > Sandbox > Active Users

**For Production:**
- Ensure customer opted-in via approved template
- Cannot send freeform message as first contact

---

## Message Limits & Best Practices

### Sandbox Limitations

- **Session Duration:** 24 hours after last message
- **User Limit:** Unlimited test users (each must join)
- **Message Rate:** 100 messages/second
- **Character Limit:** 1600 characters per message
- **Templates:** Not required in sandbox

### Production Limitations

- **Templates Required:** First message must use approved template
- **24-Hour Window:** Freeform messages allowed within 24h of customer message
- **Media Support:** Images, documents, audio (up to 16MB)
- **Rate Limits:** 80 messages/second (can request increase)

### Best Practices

1. **Keep messages concise:** Aim for <500 characters
2. **Use formatting:** WhatsApp supports *bold*, _italic_, ~strikethrough~
3. **Emojis:** Use unicode escapes, not literal emojis (e.g., `\U0001f44d` for 👍)
4. **Error handling:** Always check `send_whatsapp_message()` return value
5. **Template fallback:** If freeform send fails, try template
6. **Monitor quota:** Watch Twilio usage dashboard

---

## Advanced Features (Optional)

### Media Messages

Handle image/document attachments:

```python
# In whatsapp_client.py
async def send_whatsapp_media(
    to: str,
    media_url: str,
    caption: str = "",
) -> bool:
    client = _get_twilio_client()

    twilio_message = client.messages.create(
        from_=settings.whatsapp_phone_number,
        to=_format_phone_number(to),
        body=caption,
        media_url=[media_url]
    )

    return True
```

### Rich Text Formatting

```python
message = """
*Customer Support*

Hello! Here's what we found:

1. _Issue_: Password reset
2. _Status_: ✅ Resolved
3. _Action_: Check your email

~Previous request is now closed~

Reply with any questions!
"""
```

### Read Receipts

Track message delivery status:

```python
# Configure status callback in Twilio webhook settings
# URL: https://your-domain.com/webhooks/whatsapp/status

# Handle in routes
@router.post("/webhooks/whatsapp/status")
async def whatsapp_status(request: Request):
    payload = await request.form()
    message_sid = payload.get("MessageSid")
    status = payload.get("MessageStatus")  # sent, delivered, read, failed

    # Update database
    await update_message_status(message_sid, status)
```

---

## Cost Analysis

### Twilio Sandbox
- **Free** for testing
- No per-message charges in sandbox mode
- Unlimited messages during trial ($15 credit)

### Production Pricing (US)
- **Phone Number:** $25/month (Twilio WhatsApp number)
- **Inbound Messages:** $0.005 per message
- **Outbound Messages:** $0.005 per message
- **Template Messages:** $0.005 per message

**Example monthly cost (1000 conversations, 3 messages each):**
```
Phone rental:     $25.00
Inbound (1000):   $5.00
Outbound (2000):  $10.00
Total:            $40.00 (~$0.04 per conversation)
```

---

## Security Best Practices

1. **Always validate signatures:** Keep `TWILIO_AUTH_TOKEN` secure
2. **HTTPS only:** Never use HTTP for webhook endpoints
3. **Rate limiting:** Implement on `/webhooks/whatsapp` endpoint
4. **PII handling:** WhatsApp phone numbers are personal data - handle per GDPR
5. **Opt-out:** Provide way for users to stop messages (`STOP` keyword)
6. **Audit logs:** Log all WhatsApp interactions for compliance

---

## Migration from Sandbox to Production

When ready for production:

1. **Request WhatsApp Business Account** (Step 1 of Option B)
2. **Create & approve templates** (Step 2 of Option B)
3. **Update environment variables:**
   ```bash
   WHATSAPP_PHONE_NUMBER=whatsapp:+19995551234  # Your approved number
   ```
4. **Update webhook URL** to production domain (no more ngrok)
5. **Update code** to use templates for first contact
6. **Test thoroughly** with real customer scenarios
7. **Monitor Twilio dashboard** for errors/quota

---

## Testing Checklist

Before going live, verify:

- [ ] Sandbox joined successfully
- [ ] ngrok tunnel active and webhook configured
- [ ] Environment variables set correctly
- [ ] Send message → receive AI response
- [ ] Database records created (customers, conversations, messages)
- [ ] Metadata stored correctly (twilio_message_sid, profile_name)
- [ ] Multi-turn conversation works
- [ ] Dashboard shows WhatsApp conversations
- [ ] Signature validation working (real TWILIO_AUTH_TOKEN)
- [ ] Message length truncation tested (>1600 chars)
- [ ] Error handling tested (invalid phone number, etc.)

---

## Success Criteria

✅ **Webhook Integration** - Twilio POSTs to `/webhooks/whatsapp` successfully
✅ **Signature Validation** - Invalid signatures rejected with 403
✅ **Message Receiving** - WhatsApp messages create database records
✅ **AI Responses** - Agent generates contextual replies
✅ **Message Sending** - Twilio API sends replies successfully
✅ **Conversation Continuity** - Multi-turn dialogues maintained
✅ **Metadata Capture** - Profile name, message SID stored
✅ **Dashboard Display** - WhatsApp conversations visible with REAL badge

---

## Next Steps After WhatsApp

With Email + WhatsApp + Web Form complete:

1. ✅ **Production deployment** to Kubernetes/cloud
2. ✅ **Template management** for WhatsApp first contact
3. ✅ **Media handling** for images/documents
4. ✅ **Analytics dashboard** for channel metrics
5. ✅ **Multi-language support** for global customers
6. ✅ **Automated testing** for all three channels

---

## Support & Resources

### Twilio Documentation
- [WhatsApp API Docs](https://www.twilio.com/docs/whatsapp)
- [Webhook Security](https://www.twilio.com/docs/usage/webhooks/webhooks-security)
- [Error Codes](https://www.twilio.com/docs/api/errors)

### Debugging Tools
- Twilio Console: [Monitor > Logs](https://console.twilio.com/monitor/logs)
- ngrok Inspector: `http://localhost:4040` (when ngrok running)
- Docker logs: `docker-compose logs -f api worker`

### Common Issues
- [WhatsApp Sandbox FAQ](https://support.twilio.com/hc/en-us/articles/360033645574)
- [Phone Number Formatting](https://www.twilio.com/docs/glossary/what-e164)

For implementation issues, check project logs and database state first!
