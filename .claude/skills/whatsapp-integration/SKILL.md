# WhatsApp Integration Skill

## Skill Definition

**Name:** whatsapp-integration
**Version:** 1.0.0
**Type:** Channel Integration
**Complexity:** Intermediate

## Description

Implements Twilio WhatsApp API integration for conversational customer support, including webhook validation, message parsing, and character-optimized responses.

## When to Use This Skill

- Setting up WhatsApp as a support channel
- Processing incoming WhatsApp messages
- Sending concise, conversational responses
- Handling real-time chat interactions

## Inputs

### Configuration
```python
{
    "account_sid": "AC...",
    "auth_token": "...",
    "whatsapp_number": "whatsapp:+14155238886"
}
```

### Webhook Payload (Incoming)
```python
{
    "MessageSid": "SM123abc",
    "From": "whatsapp:+1234567890",
    "Body": "Hello, I need help",
    "ProfileName": "John Doe",
    "NumMedia": "0",
    "SmsStatus": "received"
}
```

## Outputs

### Normalized Message
```python
{
    "channel": "whatsapp",
    "channel_message_id": "SM123abc",
    "customer_phone": "+1234567890",
    "content": "Hello, I need help",
    "received_at": "2026-02-06T10:00:00Z",
    "metadata": {
        "profile_name": "John Doe",
        "num_media": 0,
        "status": "received"
    }
}
```

## Implementation Steps

### Step 1: Setup Twilio Client
```python
from twilio.rest import Client
from twilio.request_validator import RequestValidator

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)
validator = RequestValidator(auth_token)
```

### Step 2: Validate Webhook Signature
```python
@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request):
    # Get signature from header
    signature = request.headers.get('X-Twilio-Signature', '')
    url = str(request.url)
    form_data = await request.form()
    params = dict(form_data)

    # Validate
    if not validator.validate(url, params, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # Process message
    message = await whatsapp_handler.process_webhook(params)
    await publish_to_kafka('fte.tickets.incoming', message)

    # Return empty TwiML (agent will respond async)
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml"
    )
```

### Step 3: Send WhatsApp Message
```python
def send_message(to_phone: str, body: str):
    # Ensure WhatsApp format
    if not to_phone.startswith('whatsapp:'):
        to_phone = f'whatsapp:{to_phone}'

    # Send via Twilio
    message = client.messages.create(
        body=body,
        from_=whatsapp_number,
        to=to_phone
    )

    return {
        'channel_message_id': message.sid,
        'delivery_status': message.status
    }
```

### Step 4: Format Long Responses
```python
def format_response(response: str, max_length: int = 1600) -> list[str]:
    """Split long responses into multiple messages."""
    if len(response) <= max_length:
        return [response]

    messages = []
    while response:
        if len(response) <= max_length:
            messages.append(response)
            break

        # Find sentence break
        break_point = response.rfind('. ', 0, max_length)
        if break_point == -1:
            break_point = response.rfind(' ', 0, max_length)
        if break_point == -1:
            break_point = max_length

        messages.append(response[:break_point + 1].strip())
        response = response[break_point + 1:].strip()

    return messages
```

## Testing Checklist

- [ ] Webhook signature validation works
- [ ] Messages from Twilio Sandbox received
- [ ] Phone number normalized to E.164 format
- [ ] Long messages split correctly (<1600 chars)
- [ ] Emojis and Unicode characters handled
- [ ] Status callbacks update delivery status
- [ ] Error responses gracefully handled

## Error Handling

```python
try:
    message = client.messages.create(body=body, from_=from_num, to=to_num)
except TwilioRestException as e:
    if e.code == 21211:
        # Invalid phone number
        logger.error(f"Invalid WhatsApp number: {to_num}")
    elif e.code == 21608:
        # Unverified number (sandbox)
        logger.error(f"Number not joined to sandbox: {to_num}")
    else:
        logger.error(f"Twilio error {e.code}: {e.msg}")
    raise
```

## Performance Considerations

- **Rate Limits:** 1 message/second per number (Twilio Sandbox), 80 msg/sec production
- **Character Limit:** 1600 characters per message
- **Response Time:** Webhook must respond <15 seconds or Twilio retries
- **Media Processing:** Images/docs count toward rate limit

## Security Requirements

- ALWAYS validate X-Twilio-Signature header
- Store credentials in Kubernetes Secrets
- Use HTTPS for webhook URLs
- Redact phone numbers from logs (show last 4 digits only)

## Example Usage

```python
from channels.whatsapp_handler import WhatsAppHandler

# Initialize handler
whatsapp = WhatsAppHandler()

# Validate and process webhook
is_valid = await whatsapp.validate_webhook(request)
if is_valid:
    message = await whatsapp.process_webhook(await request.form())

    # Send response
    await whatsapp.send_message(
        to_phone='+1234567890',
        body='Thanks for contacting us! How can I help?'
    )
```

## Dependencies

```txt
twilio==8.11.1
fastapi==0.109.0
python-multipart==0.0.6
```

## Related Skills

- **channel-response-formatter** - Format WhatsApp-optimized responses
- **customer-identification** - Identify customers by phone number
- **metrics-observability** - Track WhatsApp metrics
