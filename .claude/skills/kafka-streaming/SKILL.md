# Kafka Event Streaming Skill

## Skill Definition

**Name:** kafka-streaming
**Version:** 1.0.0
**Type:** Infrastructure
**Complexity:** Intermediate

## Description

Implements Kafka event streaming for asynchronous, scalable message processing with guaranteed delivery and dead letter queue handling.

## Topic Design

```python
TOPICS = {
    # Unified incoming from all channels
    'tickets_incoming': 'fte.tickets.incoming',

    # Channel-specific (optional routing)
    'email_inbound': 'fte.channels.email.inbound',
    'whatsapp_inbound': 'fte.channels.whatsapp.inbound',
    'webform_inbound': 'fte.channels.webform.inbound',

    # Response routing
    'email_outbound': 'fte.channels.email.outbound',
    'whatsapp_outbound': 'fte.channels.whatsapp.outbound',

    # Escalations to human agents
    'escalations': 'fte.escalations',

    # Metrics and monitoring
    'metrics': 'fte.metrics',

    # Dead letter queue
    'dlq': 'fte.dlq'
}
```

## Implementation

### Producer with Acknowledgment
```python
from aiokafka import AIOKafkaProducer
import json

class FTEKafkaProducer:
    def __init__(self):
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',  # Wait for all replicas
            retries=3
        )
        await self.producer.start()

    async def publish(self, topic: str, event: dict):
        """Publish with acknowledgment before proceeding."""
        event["timestamp"] = datetime.utcnow().isoformat()
        await self.producer.send_and_wait(topic, event)
```

### Consumer with Error Handling
```python
from aiokafka import AIOKafkaConsumer

class FTEKafkaConsumer:
    def __init__(self, topics: list, group_id: str):
        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers='kafka:9092',
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            enable_auto_commit=False  # Manual commit after processing
        )

    async def start(self):
        await self.consumer.start()

    async def consume(self, handler):
        async for msg in self.consumer:
            try:
                # Process message
                await handler(msg.topic, msg.value)

                # Commit only after successful processing
                await self.consumer.commit()

            except Exception as e:
                logger.error(f"Processing failed: {e}")

                # Publish to DLQ
                await dlq_producer.publish(TOPICS['dlq'], {
                    'original_topic': msg.topic,
                    'original_message': msg.value,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })

                # Commit to prevent reprocessing
                await self.consumer.commit()
```

## Usage Pattern

```python
# Initialize producer
producer = FTEKafkaProducer()
await producer.start()

# Channel handler publishes event
@app.post("/webhooks/gmail")
async def gmail_webhook(request: Request):
    messages = await gmail_handler.process_notification(await request.json())

    for msg in messages:
        # Publish to Kafka with acknowledgment
        await producer.publish(TOPICS['tickets_incoming'], msg)

    return {"status": "processed"}

# Worker consumes events
consumer = FTEKafkaConsumer(
    topics=[TOPICS['tickets_incoming']],
    group_id='fte-message-processor'
)
await consumer.start()
await consumer.consume(process_message_handler)
```

## Related Skills

- **agent-specialization** - Worker implementation
- **kubernetes-deployment** - Worker scaling
- **metrics-observability** - Event metrics
