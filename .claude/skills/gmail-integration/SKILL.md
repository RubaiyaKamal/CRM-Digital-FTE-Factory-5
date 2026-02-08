# Gmail Integration Skill

## Skill Definition

**Name:** gmail-integration
**Version:** 1.0.0
**Type:** Channel Integration
**Complexity:** Intermediate

## Description

Implements complete Gmail API integration for receiving and sending customer support emails, including Pub/Sub webhook handling, message parsing, and thread-aware replies.

## When to Use This Skill

- Setting up email as a support channel
- Processing incoming customer emails
- Sending formatted email responses
- Maintaining email thread continuity

## Inputs

### Configuration
```python
{
    "credentials_path": "path/to/credentials.json",
    "pubsub_topic": "projects/PROJECT_ID/topics/gmail-push",
    "webhook_url": "https://api.example.com/webhooks/gmail"
}
```

### Message Format (Incoming)
```python
{
    "message": {
        "data": "base64_encoded_notification",
        "messageId": "1234567890",
        "publishTime": "2026-02-06T10:00:00Z"
    }
}
```

## Outputs

### Normalized Message
```python
{
    "channel": "email",
    "channel_message_id": "msg_abc123",
    "customer_email": "user@example.com",
    "subject": "Help with API",
    "content": "I need help with...",
    "received_at": "2026-02-06T10:00:00Z",
    "thread_id": "thread_xyz789",
    "metadata": {
        "headers": {...},
        "labels": ["INBOX", "UNREAD"]
    }
}
```

## Implementation Steps

### Step 1: Setup Gmail API Client
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

credentials = Credentials.from_authorized_user_file('credentials.json')
service = build('gmail', 'v1', credentials=credentials)
```

### Step 2: Configure Push Notifications
```python
request = {
    'labelIds': ['INBOX'],
    'topicName': 'projects/PROJECT_ID/topics/gmail-push'
}
service.users().watch(userId='me', body=request).execute()
```

### Step 3: Implement Webhook Handler
```python
@app.post("/webhooks/gmail")
async def gmail_webhook(request: Request):
    body = await request.json()
    history_id = body['message']['data']
    messages = await gmail_handler.process_notification(body)
    for msg in messages:
        await publish_to_kafka('fte.tickets.incoming', msg)
    return {"status": "processed"}
```

### Step 4: Send Email Replies
```python
from email.mime.text import MIMEText
import base64

message = MIMEText(body)
message['to'] = to_email
message['subject'] = f"Re: {subject}"
raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

service.users().messages().send(
    userId='me',
    body={'raw': raw, 'threadId': thread_id}
).execute()
```

## Testing Checklist

- [ ] OAuth credentials valid and refresh token works
- [ ] Pub/Sub push notifications received
- [ ] Email body extraction handles HTML and plain text
- [ ] Thread continuity maintained in replies
- [ ] Email metadata (From, Subject, Date) parsed correctly
- [ ] Rate limiting handled gracefully
- [ ] Error responses logged and retried

## Error Handling

```python
try:
    message = service.users().messages().get(userId='me', id=msg_id).execute()
except HttpError as error:
    if error.resp.status == 429:
        # Rate limited - backoff and retry
        await asyncio.sleep(60)
    elif error.resp.status == 401:
        # Token expired - refresh credentials
        credentials.refresh(Request())
    else:
        logger.error(f"Gmail API error: {error}")
        raise
```

## Performance Considerations

- **Rate Limits:** 250 quota units/user/second (1 read = 5 units)
- **Batch Processing:** Use batch requests for multiple messages
- **Caching:** Cache message IDs to avoid duplicate processing
- **Webhook Latency:** Expect 1-5 second delay from send to notification

## Security Requirements

- Store credentials in Kubernetes Secrets
- Use service accounts for production
- Validate Pub/Sub message signatures
- Redact PII from logs

## Example Usage

```python
from channels.gmail_handler import GmailHandler

# Initialize handler
gmail = GmailHandler(credentials_path='credentials.json')

# Setup push notifications
await gmail.setup_push_notifications('projects/myproject/topics/gmail')

# Process webhook
webhook_data = await request.json()
messages = await gmail.process_notification(webhook_data)

# Send reply
await gmail.send_reply(
    to_email='customer@example.com',
    subject='Your Support Request',
    body='Thank you for contacting us...',
    thread_id='thread_123'
)
```

## Dependencies

```txt
google-auth==2.26.2
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.115.0
```

## Related Skills

- **channel-response-formatter** - Format email responses
- **customer-identification** - Identify customers by email
- **metrics-observability** - Track email metrics
