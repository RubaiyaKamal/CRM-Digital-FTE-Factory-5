# Gmail Email Channel Integration Setup Guide

This guide walks you through setting up the Gmail email channel for the CRM Digital FTE Factory.

## Prerequisites

1. Google Cloud Project with Gmail API enabled
2. OAuth 2.0 credentials (Desktop app type)
3. PostgreSQL database running
4. Docker and Docker Compose installed

---

## Step 1: Google Cloud Console Setup

### 1.1 Create/Select Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Note your project ID

### 1.2 Enable Gmail API
1. Navigate to **APIs & Services** > **Library**
2. Search for "Gmail API"
3. Click **Enable**

### 1.3 Configure OAuth Consent Screen
1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **Internal** (for testing) or **External**
3. Fill in required fields:
   - App name: "CRM Digital FTE Factory"
   - User support email: your-email@gmail.com
   - Developer contact: your-email@gmail.com
4. Click **Save and Continue**
5. Add scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.modify`
6. Click **Save and Continue**
7. Add test users (your Gmail address)
8. Click **Save and Continue**

### 1.4 Create OAuth 2.0 Client ID
1. Go to **APIs & Services** > **Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. Choose **Desktop app** as application type
4. Name: "CRM FTE Factory Desktop"
5. Click **Create**
6. Download the JSON file
7. Rename it to `credentials.json` and place in project root

---

## Step 2: Database Migration

Run the OAuth credentials migration:

```bash
# If using Docker
docker exec crm_postgres psql -U crm_user -d crm_fte -f /docker-entrypoint-initdb.d/002_oauth_credentials.sql

# Or copy migration and run
docker cp src/database/migrations/002_oauth_credentials.sql crm_postgres:/tmp/
docker exec crm_postgres psql -U crm_user -d crm_fte -f /tmp/002_oauth_credentials.sql
```

Verify table creation:
```bash
docker exec crm_postgres psql -U crm_user -d crm_fte -c "\d oauth_credentials"
```

---

## Step 3: Environment Configuration

### 3.1 Update `.env` file

```bash
# Gmail Configuration
GMAIL_SENDER_EMAIL=your-support-email@gmail.com
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_POLLING_INTERVAL=30
GMAIL_MOCK=false

# Ensure API URL is set
API_BASE_URL=http://localhost:8000
```

### 3.2 Verify credentials.json location

```bash
# Should be in project root
ls -la credentials.json
```

---

## Step 4: OAuth Authentication

### 4.1 Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4.2 Run OAuth setup script

```bash
python scripts/gmail_oauth_setup.py
```

**What happens:**
1. Script opens your default browser
2. Google OAuth consent screen appears
3. Sign in with the Gmail account you want to use
4. Grant permissions (read, send, modify Gmail)
5. Browser shows "The authentication flow has completed"
6. Script stores credentials in database

**Expected output:**
```
[INFO] Starting Gmail OAuth setup for your-email@gmail.com
[INFO] Using credentials file: credentials.json
[INFO] Starting OAuth flow...
[INFO] OAuth flow completed successfully
[INFO] Stored credentials for your-email@gmail.com in database
[INFO] Testing token refresh...
[INFO] Token refresh successful
============================================================
Gmail OAuth setup completed successfully!
============================================================
Account: your-email@gmail.com
Scopes: gmail.readonly, gmail.send, gmail.modify

You can now start the Gmail poller worker:
  docker-compose up gmail-poller
============================================================
```

### 4.3 Verify credentials in database

```bash
docker exec crm_postgres psql -U crm_user -d crm_fte -c \
  "SELECT service, account_identifier, created_at FROM oauth_credentials;"
```

Expected output:
```
 service |     account_identifier      |         created_at
---------+-----------------------------+----------------------------
 gmail   | your-email@gmail.com        | 2026-02-09 10:30:45.123+00
```

---

## Step 5: Start Services

### 5.1 Rebuild containers with new dependencies

```bash
docker-compose build worker gmail-poller
```

### 5.2 Start all services

```bash
docker-compose up -d
```

### 5.3 Verify gmail-poller is running

```bash
docker-compose ps gmail-poller
```

Expected output:
```
NAME                COMMAND                  STATUS              PORTS
crm_gmail_poller    "python -m src.work…"    Up 2 minutes
```

### 5.4 Check logs

```bash
docker-compose logs -f gmail-poller
```

Expected output:
```
[INFO] ============================================================
[INFO] Gmail Poller Worker Starting
[INFO] ============================================================
[INFO] Account: your-email@gmail.com
[INFO] Polling Interval: 30s
[INFO] Webhook URL: http://api:8000/webhooks/email
[INFO] Mock Mode: False
[INFO] ============================================================
[INFO] Gmail poller started for your-email@gmail.com, polling every 30 seconds
[INFO] Checking inbox for unread messages...
[INFO] Found 0 unread message(s)
```

---

## Step 6: End-to-End Test

### 6.1 Send test email

From any email account, send an email to `your-support-email@gmail.com`:

**Subject:** Test Support Request
**Body:**
```
Hi,

I need help resetting my password. I forgot my login credentials.

Thanks!
```

### 6.2 Monitor logs

```bash
# Terminal 1: Gmail poller
docker-compose logs -f gmail-poller

# Terminal 2: API
docker-compose logs -f api

# Terminal 3: Worker
docker-compose logs -f worker
```

### 6.3 Expected flow

**Gmail Poller logs:**
```
[INFO] Found 1 unread message(s), processing...
[INFO] Fetching details for message 18d3f4a5b2c1e9f0
[INFO] Posting email from sender@example.com (thread=18d3f4a5...) to webhook
[INFO] Webhook accepted email from sender@example.com, status=200
[INFO] Batch complete: 1 processed, 0 failed
```

**API logs:**
```
[INFO] POST /webhooks/email - 200
[INFO] Webhook received: channel=email customer=uuid-here conversation=uuid-here
```

**Worker logs:**
```
[INFO] Processing ticket ticket-uuid for channel email
[INFO] Agent response generated in 2.3s
[INFO] Publishing response to fte.responses.outgoing
```

**Response Handler logs:**
```
[INFO] Response delivered: channel=email customer=sender@example.com escalated=False
[INFO] Email sent to sender@example.com, message_id=18d3f5c9...
```

### 6.4 Check Gmail inbox

Within 1-2 minutes, you should receive an AI-generated reply in the original email thread.

---

## Step 7: Verify Database Records

```bash
# Check customer created
docker exec crm_postgres psql -U crm_user -d crm_fte -c \
  "SELECT email, created_at FROM customers WHERE email = 'sender@example.com';"

# Check conversation
docker exec crm_postgres psql -U crm_user -d crm_fte -c \
  "SELECT id, channel, status, subject FROM conversations WHERE channel = 'email';"

# Check messages (should have 2: customer + agent)
docker exec crm_postgres psql -U crm_user -d crm_fte -c \
  "SELECT role, LEFT(content, 50) as preview, metadata->'gmail_thread_id' as thread_id
   FROM messages
   WHERE conversation_id IN (SELECT id FROM conversations WHERE channel = 'email')
   ORDER BY created_at;"
```

### 6.5 Test thread continuity

Reply to the AI's email with:
```
Thanks! What if I also forgot my username?
```

**Expected behavior:**
- Poller picks up reply within 30 seconds
- Same `conversation_id` in database
- AI responds in the same email thread
- Thread shows full conversation history

---

## Step 8: Dashboard Verification

1. Open dashboard: http://localhost:3003/dashboard/conversations
2. Should see email conversation with green "REAL" badge
3. Click to view details - full email thread with AI responses
4. Subject line should match original email

---

## Troubleshooting

### OAuth Authentication Failed

**Error:** `No credentials found for your-email@gmail.com`

**Solution:**
```bash
# Re-run OAuth setup
python scripts/gmail_oauth_setup.py
```

---

### Token Refresh Failed

**Error:** `Authentication failed. Re-run: python scripts/gmail_oauth_setup.py`

**Solution:**
1. Delete existing credentials:
   ```bash
   docker exec crm_postgres psql -U crm_user -d crm_fte -c \
     "DELETE FROM oauth_credentials WHERE service = 'gmail';"
   ```
2. Re-run OAuth setup

---

### Poller Not Finding Messages

**Symptoms:** Logs show "Found 0 unread messages" but inbox has unread emails

**Checks:**
1. Verify correct Gmail account:
   ```bash
   # Check GMAIL_SENDER_EMAIL in .env
   grep GMAIL_SENDER_EMAIL .env
   ```
2. Ensure email is in INBOX (not Spam, not archived)
3. Ensure email is unread
4. Check OAuth scopes include `gmail.readonly`

---

### Emails Not Sending

**Error:** `Failed to send email to customer@example.com`

**Checks:**
1. Verify OAuth scopes include `gmail.send`
2. Check rate limits (250 quota units/user/second)
3. Verify `GMAIL_MOCK=false` in environment
4. Check gmail-poller container has credentials.json mounted:
   ```bash
   docker exec crm_gmail_poller ls -la /app/credentials.json
   ```

---

### Thread ID Not Preserved

**Symptoms:** Each AI reply starts a new email thread

**Checks:**
1. Verify metadata stored in database:
   ```bash
   docker exec crm_postgres psql -U crm_user -d crm_fte -c \
     "SELECT metadata FROM messages WHERE channel = 'email' AND role = 'customer';"
   ```
   Should show: `{"gmail_thread_id": "...", ...}`

2. Check response_handler logs for thread_id retrieval

---

## Performance Tuning

### Adjust Polling Interval

For faster response times (costs more API quota):
```bash
# .env
GMAIL_POLLING_INTERVAL=10  # Poll every 10 seconds
```

For slower response times (conserves API quota):
```bash
# .env
GMAIL_POLLING_INTERVAL=60  # Poll every 60 seconds
```

### Rate Limits

Gmail API quotas (per user):
- **250 quota units/user/second**
- **1 billion quota units/day**

Operations:
- List messages: 5 units
- Get message: 5 units
- Send message: 100 units
- Modify message: 5 units

At 30-second polling with 10 messages/poll:
- List: 5 units × 2880 polls/day = 14,400 units/day
- Get: 5 units × 10 msg × 2880 = 144,000 units/day
- **Total: ~158,000 units/day (0.016% of daily quota)**

---

## Upgrading to Push Notifications (Optional)

For real-time email notifications instead of polling:

1. Enable Cloud Pub/Sub API
2. Create Pub/Sub topic: `projects/YOUR-PROJECT/topics/gmail-push`
3. Update Gmail watch:
   ```python
   service.users().watch(
       userId='me',
       body={
           'topicName': 'projects/YOUR-PROJECT/topics/gmail-push',
           'labelIds': ['INBOX']
       }
   ).execute()
   ```
4. Replace poller with Pub/Sub subscriber
5. Process watch notifications instead of polling

**Benefits:** <100ms latency vs 30s polling

---

## Security Best Practices

1. **Never commit credentials.json** - added to `.gitignore`
2. **Rotate OAuth tokens** every 90 days
3. **Use service accounts** for production (not user OAuth)
4. **Encrypt credentials at rest** in database (future enhancement)
5. **Monitor quota usage** in Google Cloud Console
6. **Enable 2FA** on Gmail account
7. **Review OAuth scopes** regularly - minimize permissions

---

## Next Steps

After Gmail is working:

1. ✅ Add WhatsApp channel (similar pattern, ~4-6 hours)
2. ✅ Add HTML email formatting with company branding
3. ✅ Handle email attachments
4. ✅ Upgrade to Push Notifications (Pub/Sub)
5. ✅ Add multiple Gmail account support
6. ✅ Implement email signature customization

---

## Support

For issues:
1. Check logs: `docker-compose logs -f gmail-poller api worker`
2. Verify database state: Check customers, conversations, messages tables
3. Test OAuth: `python scripts/gmail_oauth_setup.py`
4. Review this guide's Troubleshooting section

**Success Criteria:**
✅ OAuth authentication completed
✅ Poller fetches unread emails every 30s
✅ Incoming emails create database records
✅ AI generates appropriate responses
✅ Replies sent via Gmail API with threading
✅ Follow-up emails maintain conversation continuity
✅ Dashboard shows email conversations
✅ Zero crashes in 1-hour test period
