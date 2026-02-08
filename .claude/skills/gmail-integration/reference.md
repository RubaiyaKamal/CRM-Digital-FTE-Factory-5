# Gmail Integration Reference

## Overview
This skill handles Gmail API integration for email-based customer support, including webhook setup, message parsing, and reply sending.

## Key Capabilities
- Gmail Pub/Sub push notification setup
- Incoming email parsing and normalization
- Thread-aware reply sending
- Email metadata extraction (From, Subject, Body)
- Attachment handling

## Prerequisites
- Gmail API credentials (`credentials.json`)
- Google Cloud Pub/Sub topic configured
- OAuth 2.0 tokens with gmail.modify scope

## Related Files
- `src/channels/gmail_handler.py` - Main implementation
- `tests/test_gmail_integration.py` - Integration tests
- `docs/gmail-setup.md` - Setup guide

## API References
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Pub/Sub Push Notifications](https://developers.google.com/gmail/api/guides/push)

## Common Issues
1. **Token expiration**: Implement refresh token handling
2. **Rate limits**: 250 quota units/user/second
3. **Webhook signature validation**: Verify Pub/Sub messages

## Constitutional Alignment
- **Principle 1: Multi-Channel First** - Email as first-class channel
- **Principle 3: Zero Message Loss** - Persistent storage before acknowledgment
- **Principle 4: Channel-Appropriate Responses** - Formal email formatting
