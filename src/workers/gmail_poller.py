"""
Gmail Poller Worker

Polls Gmail inbox every N seconds for unread messages and posts them to the
email webhook endpoint for processing.

This worker:
1. Fetches unread messages from Gmail API
2. Parses email details (sender, subject, body, threadId)
3. Normalizes to webhook payload format
4. POSTs to /webhooks/email endpoint
5. Marks message as read after successful processing
"""
from __future__ import annotations

import asyncio
import logging
import signal
import sys
from datetime import datetime

import httpx

from src.channels.gmail_client import (
    fetch_unread_messages,
    get_message_details,
    mark_as_read,
)
from src.config import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_flag = False


def signal_handler(signum, frame):
    """Handle shutdown signals."""
    global shutdown_flag
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    shutdown_flag = True


async def normalize_email_to_webhook(email_data: dict) -> dict:
    """
    Normalize Gmail message to webhook payload format.

    Args:
        email_data: Parsed email data from get_message_details()

    Returns:
        Webhook payload dict matching email webhook schema
    """
    return {
        "email": email_data["from"],
        "subject": email_data.get("subject", "(No Subject)"),
        "message": email_data["body"],
        "session_id": email_data["threadId"],
        "metadata": {
            "gmail_message_id": email_data["id"],
            "gmail_thread_id": email_data["threadId"],
            "from_full": email_data.get("from_full", email_data["from"]),
            "date": email_data.get("date", ""),
        },
    }


async def process_message(message_metadata: dict, http_client: httpx.AsyncClient) -> bool:
    """
    Process a single Gmail message: parse, post to webhook, mark as read.

    Args:
        message_metadata: Dict with 'id' and 'threadId' from Gmail API
        http_client: HTTP client for webhook requests

    Returns:
        True if processed successfully, False otherwise
    """
    message_id = message_metadata["id"]

    try:
        # Parse full email details
        logger.debug(f"Fetching details for message {message_id}")
        email_data = await get_message_details(message_id)

        # Normalize to webhook payload
        payload = await normalize_email_to_webhook(email_data)

        # POST to webhook endpoint
        webhook_url = f"{settings.api_base_url}/webhooks/email"
        logger.info(
            f"Posting email from {email_data['from']} (thread={email_data['threadId'][:8]}...) to webhook"
        )

        response = await http_client.post(webhook_url, json=payload, timeout=30.0)
        response.raise_for_status()

        logger.info(
            f"Webhook accepted email from {email_data['from']}, status={response.status_code}"
        )

        # Mark as read only after successful webhook processing
        await mark_as_read(message_id)

        return True

    except httpx.HTTPStatusError as e:
        logger.error(
            f"Webhook returned error for message {message_id}: {e.response.status_code} - {e.response.text}"
        )
        return False
    except httpx.RequestError as e:
        logger.error(f"Failed to reach webhook for message {message_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error processing message {message_id}: {e}", exc_info=True)
        return False


async def poll_gmail_inbox():
    """Main polling loop with error handling and backoff."""
    logger.info(
        f"Gmail poller started for {settings.gmail_sender_email}, "
        f"polling every {settings.gmail_polling_interval} seconds"
    )

    if settings.gmail_mock:
        logger.warning("GMAIL_MOCK=true - poller will not run. Set to 'false' for real polling.")
        return

    consecutive_errors = 0
    max_consecutive_errors = 5
    base_interval = settings.gmail_polling_interval

    async with httpx.AsyncClient() as http_client:
        while not shutdown_flag:
            try:
                # Fetch unread messages
                logger.debug("Checking inbox for unread messages...")
                messages = await fetch_unread_messages(max_results=10)

                if not messages:
                    logger.debug("No unread messages found")
                else:
                    logger.info(f"Found {len(messages)} unread message(s), processing...")

                    # Process each message
                    processed_count = 0
                    failed_count = 0

                    for msg_meta in messages:
                        if shutdown_flag:
                            break

                        success = await process_message(msg_meta, http_client)
                        if success:
                            processed_count += 1
                        else:
                            failed_count += 1

                    logger.info(
                        f"Batch complete: {processed_count} processed, {failed_count} failed"
                    )

                # Reset error counter on success
                consecutive_errors = 0

            except Exception as e:
                consecutive_errors += 1
                logger.error(
                    f"Polling error ({consecutive_errors}/{max_consecutive_errors}): {e}",
                    exc_info=True,
                )

                if consecutive_errors >= max_consecutive_errors:
                    logger.critical(
                        f"Too many consecutive errors ({consecutive_errors}), stopping poller"
                    )
                    break

            # Wait before next poll (with backoff on errors)
            if consecutive_errors > 0:
                backoff_interval = min(base_interval * (2**consecutive_errors), 300)
                logger.info(f"Backing off for {backoff_interval}s due to errors")
                await asyncio.sleep(backoff_interval)
            else:
                await asyncio.sleep(base_interval)

    logger.info("Gmail poller stopped")


async def health_check_endpoint():
    """
    Simple health check that could be exposed via a minimal HTTP server.
    For now, just logs readiness.
    """
    logger.info("Health check: Gmail poller is running")


async def main():
    """Entry point for Gmail poller worker."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("=" * 60)
    logger.info("Gmail Poller Worker Starting")
    logger.info("=" * 60)
    logger.info(f"Account: {settings.gmail_sender_email}")
    logger.info(f"Polling Interval: {settings.gmail_polling_interval}s")
    logger.info(f"Webhook URL: {settings.api_base_url}/webhooks/email")
    logger.info(f"Mock Mode: {settings.gmail_mock}")
    logger.info("=" * 60)

    try:
        await poll_gmail_inbox()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.critical(f"Fatal error in poller: {e}", exc_info=True)
        sys.exit(1)

    logger.info("Gmail poller shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
