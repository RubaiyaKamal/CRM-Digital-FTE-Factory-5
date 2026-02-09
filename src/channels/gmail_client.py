"""
Gmail API Client Module

Provides functions for authenticating with Gmail API and performing operations:
- Fetching unread messages
- Parsing email details
- Sending email replies with threading
- Marking messages as read

Uses OAuth credentials stored in the database.
"""
from __future__ import annotations

import asyncio
import base64
import email
import json
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

import asyncpg
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.config import settings

logger = logging.getLogger(__name__)


async def _load_credentials_from_db(email: str) -> Credentials | None:
    """Load OAuth credentials from database and refresh if expired."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        row = await conn.fetchrow(
            """
            SELECT credentials FROM oauth_credentials
            WHERE service = $1 AND account_identifier = $2
            """,
            "gmail",
            email,
        )
        if not row:
            logger.error(f"No credentials found for {email}")
            return None

        creds_dict = json.loads(row["credentials"])
        credentials = Credentials(
            token=creds_dict.get("token"),
            refresh_token=creds_dict.get("refresh_token"),
            token_uri=creds_dict.get("token_uri"),
            client_id=creds_dict.get("client_id"),
            client_secret=creds_dict.get("client_secret"),
            scopes=creds_dict.get("scopes"),
        )
        if creds_dict.get("expiry"):
            credentials.expiry = datetime.fromisoformat(creds_dict["expiry"])

        # Refresh if expired
        if credentials.expired and credentials.refresh_token:
            logger.info("Refreshing expired token")
            await asyncio.to_thread(credentials.refresh, Request())

            # Update in database
            updated_dict = {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
                "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
            }
            await conn.execute(
                """
                UPDATE oauth_credentials
                SET credentials = $1, updated_at = NOW()
                WHERE service = $2 AND account_identifier = $3
                """,
                json.dumps(updated_dict),
                "gmail",
                email,
            )
            logger.info("Token refreshed and updated in database")

        return credentials
    finally:
        await conn.close()


async def get_gmail_service():
    """Build authenticated Gmail API service with auto token refresh."""
    credentials = await _load_credentials_from_db(settings.gmail_sender_email)
    if not credentials:
        raise RuntimeError(
            f"No Gmail credentials found for {settings.gmail_sender_email}. "
            "Run: python scripts/gmail_oauth_setup.py"
        )

    service = await asyncio.to_thread(
        build, "gmail", "v1", credentials=credentials, cache_discovery=False
    )
    return service


async def fetch_unread_messages(max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch unread emails from inbox.

    Args:
        max_results: Maximum number of messages to fetch

    Returns:
        List of message metadata dicts with id and threadId
    """
    try:
        service = await get_gmail_service()

        # List unread messages
        results = await asyncio.to_thread(
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX", "UNREAD"], maxResults=max_results)
            .execute
        )

        messages = results.get("messages", [])
        logger.info(f"Found {len(messages)} unread messages")
        return messages

    except HttpError as error:
        if error.resp.status == 401:
            logger.error("Authentication failed. Re-run: python scripts/gmail_oauth_setup.py")
        else:
            logger.error(f"Gmail API error: {error}")
        return []
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return []


def _decode_mime_words(text: str) -> str:
    """Decode MIME encoded-words in email headers."""
    if not text:
        return ""
    try:
        decoded_parts = email.header.decode_header(text)
        result = []
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                result.append(part.decode(encoding or "utf-8", errors="ignore"))
            else:
                result.append(part)
        return "".join(result)
    except Exception as e:
        logger.warning(f"Failed to decode header: {text}, error: {e}")
        return text


def _extract_body(payload: Dict[str, Any]) -> str:
    """Extract plain text body from email payload."""
    body = ""

    # Check for plain text in current part
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        data = payload["body"]["data"]
        body = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="ignore")
        return body

    # Check for multipart
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                data = part["body"]["data"]
                body = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="ignore")
                break
            # Recursive for nested parts
            elif "parts" in part:
                nested_body = _extract_body(part)
                if nested_body:
                    body = nested_body
                    break

    # Fallback to HTML if no plain text
    if not body and "parts" in payload:
        for part in payload["parts"]:
            if part.get("mimeType") == "text/html" and part.get("body", {}).get("data"):
                data = part["body"]["data"]
                html = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="ignore")
                # Simple HTML strip (for hackathon - could use BeautifulSoup)
                import re

                body = re.sub(r"<[^>]+>", "", html)
                break

    return body.strip()


async def get_message_details(message_id: str) -> Dict[str, Any]:
    """
    Parse full email message including headers, body, threadId.

    Args:
        message_id: Gmail message ID

    Returns:
        Dict with keys: id, threadId, subject, from, body, date
    """
    try:
        service = await get_gmail_service()

        message = await asyncio.to_thread(
            service.users().messages().get(userId="me", id=message_id, format="full").execute
        )

        headers = message["payload"]["headers"]
        header_dict = {h["name"].lower(): h["value"] for h in headers}

        subject = _decode_mime_words(header_dict.get("subject", "(No Subject)"))
        from_email = header_dict.get("from", "unknown@example.com")
        date = header_dict.get("date", "")

        # Extract email address from "Name <email@domain.com>" format
        import re

        email_match = re.search(r"[\w\.-]+@[\w\.-]+", from_email)
        from_address = email_match.group(0) if email_match else from_email

        body = _extract_body(message["payload"])

        return {
            "id": message["id"],
            "threadId": message["threadId"],
            "subject": subject,
            "from": from_address,
            "from_full": from_email,
            "body": body,
            "date": date,
        }

    except HttpError as error:
        logger.error(f"Error fetching message {message_id}: {error}")
        raise
    except Exception as e:
        logger.error(f"Error parsing message {message_id}: {e}")
        raise


async def send_email(
    to: str, subject: str, body: str, thread_id: Optional[str] = None
) -> bool:
    """
    Send email reply via Gmail API with proper threading and MIME formatting.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Plain text email body
        thread_id: Optional Gmail thread ID for threading replies

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        service = await get_gmail_service()

        # Create MIME message
        message = MIMEMultipart("alternative")
        message["To"] = to
        message["From"] = settings.gmail_sender_email
        message["Subject"] = subject

        # Add plain text part
        text_part = MIMEText(body, "plain")
        message.attach(text_part)

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        # Build request body
        send_body = {"raw": raw_message}
        if thread_id:
            send_body["threadId"] = thread_id

        # Send message
        result = await asyncio.to_thread(
            service.users().messages().send(userId="me", body=send_body).execute
        )

        logger.info(f"Email sent to {to}, message_id={result['id']}, thread_id={result.get('threadId')}")
        return True

    except HttpError as error:
        logger.error(f"Failed to send email to {to}: {error}")
        return False
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False


async def mark_as_read(message_id: str) -> bool:
    """
    Mark message as read after processing.

    Args:
        message_id: Gmail message ID

    Returns:
        True if successful, False otherwise
    """
    try:
        service = await get_gmail_service()

        await asyncio.to_thread(
            service.users()
            .messages()
            .modify(userId="me", id=message_id, body={"removeLabelIds": ["UNREAD"]})
            .execute
        )

        logger.debug(f"Marked message {message_id} as read")
        return True

    except HttpError as error:
        logger.error(f"Failed to mark message {message_id} as read: {error}")
        return False
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
        return False
