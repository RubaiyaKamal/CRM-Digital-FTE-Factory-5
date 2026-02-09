-- Migration: OAuth Credentials Table
-- Purpose: Store Gmail OAuth access/refresh tokens for API authentication
-- Date: 2026-02-09

CREATE TABLE IF NOT EXISTS oauth_credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service VARCHAR(50) NOT NULL,
    account_identifier VARCHAR(255) NOT NULL,
    credentials JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(service, account_identifier)
);

-- Index for fast service lookups
CREATE INDEX IF NOT EXISTS idx_oauth_credentials_service ON oauth_credentials(service);

-- Index for account lookups
CREATE INDEX IF NOT EXISTS idx_oauth_credentials_account ON oauth_credentials(service, account_identifier);

-- Add comment for documentation
COMMENT ON TABLE oauth_credentials IS 'Stores OAuth credentials for external service integrations (Gmail, etc.)';
COMMENT ON COLUMN oauth_credentials.service IS 'Service name (e.g., gmail, outlook)';
COMMENT ON COLUMN oauth_credentials.account_identifier IS 'Email or account identifier for the service';
COMMENT ON COLUMN oauth_credentials.credentials IS 'JSON containing access_token, refresh_token, token_uri, client_id, client_secret, scopes, expiry';
