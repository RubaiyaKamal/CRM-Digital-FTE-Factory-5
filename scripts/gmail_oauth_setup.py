#!/usr/bin/env python3
"""
Gmail OAuth Setup Script

This script performs the initial OAuth authentication flow for Gmail API access.
It stores the credentials in the database for use by the Gmail poller worker.

Usage:
    python scripts/gmail_oauth_setup.py

Prerequisites:
    1. Download credentials.json from Google Cloud Console
    2. Place it in the project root
    3. Ensure database is running and migrated
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone

import asyncpg
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]


async def store_credentials_in_db(credentials: Credentials, email: str) -> None:
    """Store OAuth credentials in the database."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        credentials_dict = {
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
            INSERT INTO oauth_credentials (service, account_identifier, credentials, updated_at)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (service, account_identifier)
            DO UPDATE SET
                credentials = EXCLUDED.credentials,
                updated_at = EXCLUDED.updated_at
            """,
            "gmail",
            email,
            json.dumps(credentials_dict),
            datetime.now(timezone.utc),
        )
        logger.info(f"Stored credentials for {email} in database")
    finally:
        await conn.close()


async def load_credentials_from_db(email: str) -> Credentials | None:
    """Load OAuth credentials from the database."""
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

        return credentials
    finally:
        await conn.close()


def run_oauth_flow(credentials_file: str) -> Credentials:
    """Run the OAuth flow to get credentials."""
    if not os.path.exists(credentials_file):
        logger.error(f"Credentials file not found: {credentials_file}")
        logger.error(
            "Please download credentials.json from Google Cloud Console:\n"
            "1. Go to https://console.cloud.google.com\n"
            "2. Select your project\n"
            "3. APIs & Services > Credentials\n"
            "4. Create OAuth 2.0 Client ID (Desktop app)\n"
            "5. Download JSON and save as credentials.json"
        )
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
    credentials = flow.run_local_server(port=8080)
    logger.info("OAuth flow completed successfully")
    return credentials


async def test_token_refresh(email: str) -> bool:
    """Test that the stored credentials can be refreshed."""
    credentials = await load_credentials_from_db(email)
    if not credentials:
        logger.error("No credentials found in database")
        return False

    if credentials.expired and credentials.refresh_token:
        logger.info("Testing token refresh...")
        credentials.refresh(Request())
        await store_credentials_in_db(credentials, email)
        logger.info("Token refresh successful")
        return True
    elif not credentials.expired:
        logger.info("Token is still valid (not expired)")
        return True
    else:
        logger.error("Token expired and no refresh token available")
        return False


async def main() -> None:
    """Main setup flow."""
    credentials_file = settings.gmail_credentials_file
    sender_email = settings.gmail_sender_email

    if not sender_email:
        logger.error(
            "GMAIL_SENDER_EMAIL not set in environment variables.\n"
            "Please add to .env: GMAIL_SENDER_EMAIL=your-email@gmail.com"
        )
        sys.exit(1)

    logger.info(f"Starting Gmail OAuth setup for {sender_email}")
    logger.info(f"Using credentials file: {credentials_file}")

    # Check if credentials already exist
    existing_creds = await load_credentials_from_db(sender_email)
    if existing_creds:
        logger.info("Found existing credentials in database")
        choice = input("Do you want to re-authenticate? (y/N): ").strip().lower()
        if choice != "y":
            logger.info("Testing existing credentials...")
            if await test_token_refresh(sender_email):
                logger.info("Existing credentials are valid")
                return
            else:
                logger.warning("Existing credentials failed, re-authenticating...")

    # Run OAuth flow
    logger.info("\nStarting OAuth flow...")
    logger.info("Your browser will open for authentication.")
    logger.info(
        "If browser doesn't open, copy the URL from the console and paste in your browser."
    )

    credentials = run_oauth_flow(credentials_file)

    # Store in database
    await store_credentials_in_db(credentials, sender_email)

    # Test refresh
    logger.info("\nTesting token refresh...")
    if await test_token_refresh(sender_email):
        logger.info("\n" + "=" * 60)
        logger.info("Gmail OAuth setup completed successfully!")
        logger.info("=" * 60)
        logger.info(f"Account: {sender_email}")
        logger.info(f"Scopes: {', '.join(SCOPES)}")
        logger.info("\nYou can now start the Gmail poller worker:")
        logger.info("  docker-compose up gmail-poller")
        logger.info("=" * 60)
    else:
        logger.error("Token refresh test failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
