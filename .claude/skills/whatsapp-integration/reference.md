# WhatsApp Integration Reference

## Overview
This skill handles Twilio WhatsApp API integration for chat-based customer support, including webhook validation, message parsing, and concise reply formatting.

## Key Capabilities
- Twilio webhook signature validation
- WhatsApp message parsing
- Character-limited response formatting (1600 char limit)
- Message splitting for long responses
- Media handling (images, documents)

## Prerequisites
- Twilio Account SID and Auth Token
- Twilio WhatsApp-enabled phone number
- Webhook endpoint with public URL (use ngrok for local dev)

## Related Files
- `src/channels/whatsapp_handler.py` - Main implementation
- `tests/test_whatsapp_integration.py` - Integration tests
- `docs/whatsapp-setup.md` - Setup guide

## API References
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp/api)
- [Webhook Signature Validation](https://www.twilio.com/docs/usage/security#validating-requests)

## Common Issues
1. **Signature validation failures**: Check webhook URL matches exactly
2. **Message length**: WhatsApp has 1600 char limit per message
3. **Sandbox limitations**: Test numbers must join sandbox first

## Constitutional Alignment
- **Principle 1: Multi-Channel First** - WhatsApp as conversational channel
- **Principle 4: Channel-Appropriate Responses** - Concise, casual formatting
- **Principle 3: Zero Message Loss** - Persistent storage before acknowledgment
