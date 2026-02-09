"""
Application configuration — reads from environment variables.
"""
from __future__ import annotations

import os
from functools import lru_cache


class Settings:
    """Application settings loaded from environment."""

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://crm_user:crm_pass@localhost:5432/crm_fte"
    )
    db_pool_min: int = int(os.getenv("DB_POOL_MIN", "2"))
    db_pool_max: int = int(os.getenv("DB_POOL_MAX", "10"))

    # Kafka
    kafka_brokers: str = os.getenv("KAFKA_BROKERS", "localhost:9092")
    kafka_topic_incoming: str = os.getenv("KAFKA_TOPIC_INCOMING", "fte.tickets.incoming")
    kafka_topic_outgoing: str = os.getenv("KAFKA_TOPIC_OUTGOING", "fte.responses.outgoing")
    kafka_consumer_group: str = os.getenv("KAFKA_CONSUMER_GROUP", "fte-worker")

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Twilio (WhatsApp)
    twilio_auth_token: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    twilio_account_sid: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    twilio_phone_number: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    whatsapp_phone_number: str = os.getenv("WHATSAPP_PHONE_NUMBER", "")
    whatsapp_mock: bool = os.getenv("WHATSAPP_MOCK", "true").lower() == "true"

    # Gmail
    gmail_mock: bool = os.getenv("GMAIL_MOCK", "true").lower() == "true"
    gmail_credentials_file: str = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
    gmail_polling_interval: int = int(os.getenv("GMAIL_POLLING_INTERVAL", "30"))
    gmail_sender_email: str = os.getenv("GMAIL_SENDER_EMAIL", "")
    api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")

    # CORS
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")

    # App
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    @property
    def database_url_safe(self) -> str:
        """Database URL with password masked for logging."""
        url = self.database_url
        if "@" in url:
            pre, rest = url.split("@", 1)
            if ":" in pre:
                proto_user = pre.rsplit(":", 1)[0]
                return f"{proto_user}:***@{rest}"
        return url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
