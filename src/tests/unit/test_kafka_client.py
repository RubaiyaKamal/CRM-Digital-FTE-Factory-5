"""Unit tests for Kafka client helpers."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestKafkaClient:
    @pytest.mark.asyncio
    async def test_create_consumer_returns_consumer(self):
        with patch("src.kafka_client.AIOKafkaConsumer") as mock_consumer_cls:
            mock_consumer_cls.return_value = MagicMock()
            from src.kafka_client import create_consumer
            consumer = create_consumer(["test-topic"], "test-group")
            assert consumer is not None
            mock_consumer_cls.assert_called_once()

    @pytest.mark.asyncio
    async def test_stop_producer_handles_none(self):
        """stop_producer should not error when producer is None."""
        import src.kafka_client as kc
        original = kc._producer
        kc._producer = None
        from src.kafka_client import stop_producer
        await stop_producer()  # Should not raise
        kc._producer = original

    @pytest.mark.asyncio
    async def test_get_producer_creates_and_starts(self):
        """get_producer should create and start a new producer when none exists."""
        import src.kafka_client as kc
        original = kc._producer
        kc._producer = None
        mock_producer = AsyncMock()
        try:
            with patch("src.kafka_client.AIOKafkaProducer", return_value=mock_producer):
                from src.kafka_client import get_producer
                result = await get_producer()
                assert result is mock_producer
                mock_producer.start.assert_called_once()
        finally:
            kc._producer = original

    @pytest.mark.asyncio
    async def test_get_producer_returns_existing(self):
        """get_producer should return existing producer without recreating."""
        import src.kafka_client as kc
        original = kc._producer
        mock_producer = MagicMock()
        kc._producer = mock_producer
        try:
            from src.kafka_client import get_producer
            result = await get_producer()
            assert result is mock_producer
        finally:
            kc._producer = original

    @pytest.mark.asyncio
    async def test_stop_producer_stops_and_clears(self):
        """stop_producer should stop the producer and set _producer to None."""
        import src.kafka_client as kc
        original = kc._producer
        mock_producer = AsyncMock()
        kc._producer = mock_producer
        try:
            from src.kafka_client import stop_producer
            await stop_producer()
            mock_producer.stop.assert_called_once()
            assert kc._producer is None
        finally:
            kc._producer = original

    @pytest.mark.asyncio
    async def test_publish_sends_message(self):
        """publish should call send_and_wait on the producer."""
        import src.kafka_client as kc
        original = kc._producer
        mock_producer = AsyncMock()
        kc._producer = mock_producer
        try:
            from src.kafka_client import publish
            await publish("test-topic", {"key": "value"}, key="cust-1")
            mock_producer.send_and_wait.assert_called_once_with(
                "test-topic", value={"key": "value"}, key=b"cust-1"
            )
        finally:
            kc._producer = original

    @pytest.mark.asyncio
    async def test_publish_without_key(self):
        """publish without key should pass None as key."""
        import src.kafka_client as kc
        original = kc._producer
        mock_producer = AsyncMock()
        kc._producer = mock_producer
        try:
            from src.kafka_client import publish
            await publish("test-topic", {"data": "test"})
            mock_producer.send_and_wait.assert_called_once_with(
                "test-topic", value={"data": "test"}, key=None
            )
        finally:
            kc._producer = original
