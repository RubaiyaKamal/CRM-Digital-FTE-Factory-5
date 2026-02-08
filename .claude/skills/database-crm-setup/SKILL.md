# Database CRM Setup Skill

## Skill Definition

**Name:** database-crm-setup
**Version:** 1.0.0
**Type:** Infrastructure
**Complexity:** Intermediate

## Description

Creates PostgreSQL schema serving as complete CRM system with multi-channel customer tracking, conversation history, ticket management, and knowledge base with vector search.

## Schema Overview

```sql
-- Core tables for CRM functionality
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50),
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE customer_identifiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id),
    identifier_type VARCHAR(50) NOT NULL,  -- 'email', 'phone', 'whatsapp'
    identifier_value VARCHAR(255) NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(identifier_type, identifier_value)
);

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id),
    initial_channel VARCHAR(50) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'active',
    sentiment_score DECIMAL(3,2),
    resolution_type VARCHAR(50),
    metadata JSONB DEFAULT '{}'
);

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    channel VARCHAR(50) NOT NULL,
    direction VARCHAR(20) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tokens_used INTEGER,
    latency_ms INTEGER,
    tool_calls JSONB DEFAULT '[]',
    channel_message_id VARCHAR(255),
    delivery_status VARCHAR(50) DEFAULT 'pending'
);

CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    customer_id UUID REFERENCES customers(id),
    source_channel VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT
);

CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customer_identifiers_value ON customer_identifiers(identifier_value);
CREATE INDEX idx_conversations_customer ON conversations(customer_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_channel ON messages(channel);
CREATE INDEX idx_knowledge_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);
```

## Implementation

### Step 1: Setup PostgreSQL with pgvector
```bash
# Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Step 2: Customer Identification Logic
```python
async def resolve_customer(message: dict) -> str:
    """Identify or create customer from message."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Try email first
        if email := message.get('customer_email'):
            customer = await conn.fetchrow(
                "SELECT id FROM customers WHERE email = $1", email
            )
            if customer:
                return str(customer['id'])

            # Create new customer
            customer_id = await conn.fetchval("""
                INSERT INTO customers (email, name)
                VALUES ($1, $2)
                RETURNING id
            """, email, message.get('customer_name', ''))

            return str(customer_id)

        # Try phone for WhatsApp
        if phone := message.get('customer_phone'):
            identifier = await conn.fetchrow("""
                SELECT customer_id FROM customer_identifiers
                WHERE identifier_type = 'whatsapp' AND identifier_value = $1
            """, phone)

            if identifier:
                return str(identifier['customer_id'])

            # Create new customer with phone
            customer_id = await conn.fetchval("""
                INSERT INTO customers (phone) VALUES ($1) RETURNING id
            """, phone)

            await conn.execute("""
                INSERT INTO customer_identifiers
                (customer_id, identifier_type, identifier_value)
                VALUES ($1, 'whatsapp', $2)
            """, customer_id, phone)

            return str(customer_id)
```

### Step 3: Cross-Channel History Retrieval
```python
async def get_customer_history(customer_id: str, limit: int = 20) -> list:
    """Get conversation history across all channels."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        history = await conn.fetch("""
            SELECT
                c.initial_channel,
                c.started_at,
                m.content,
                m.role,
                m.channel,
                m.created_at
            FROM conversations c
            JOIN messages m ON m.conversation_id = c.id
            WHERE c.customer_id = $1
            ORDER BY m.created_at DESC
            LIMIT $2
        """, customer_id, limit)

        return [dict(row) for row in history]
```

## Related Skills

- **customer-identification** - Customer resolution logic
- **agent-specialization** - Agent integration
- **metrics-observability** - Metrics storage
