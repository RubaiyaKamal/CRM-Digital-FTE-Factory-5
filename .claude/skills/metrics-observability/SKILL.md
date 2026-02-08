# Metrics & Observability Skill

## Skill Definition

**Name:** metrics-observability
**Version:** 1.0.0
**Type:** Infrastructure
**Complexity:** Intermediate

## Description

Implements production observability with structured logging, metrics collection, and channel-specific monitoring.

## Implementation

```python
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

async def collect_metrics(
    event_type: str,
    channel: str,
    latency_ms: float,
    **kwargs
):
    """Collect interaction metrics."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO agent_metrics
            (metric_name, metric_value, channel, dimensions, recorded_at)
            VALUES ($1, $2, $3, $4, NOW())
        """, event_type, latency_ms, channel, json.dumps(kwargs))

# Structured logging
logger.info(
    "message_processed",
    extra={
        "channel": "whatsapp",
        "latency_ms": 1250,
        "escalated": False,
        "customer_id": "uuid-123"
    }
)
```

## Related Skills

- **agent-specialization** - Metrics integration
- **kubernetes-deployment** - Health endpoints
