# Customer Identification Skill

## Skill Definition

**Name:** customer-identification
**Version:** 1.0.0
**Type:** Utility
**Complexity:** Intermediate

## Description

Identifies or creates customers from multi-channel messages, merging identifiers (email, phone) into unified customer records.

## Implementation

```python
async def resolve_customer(message: dict) -> str:
    """Resolve or create customer from message identifiers."""
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
                WHERE identifier_type = 'whatsapp'
                AND identifier_value = $1
            """, phone)

            if identifier:
                return str(identifier['customer_id'])

            # Create new customer with phone
            customer_id = await conn.fetchval("""
                INSERT INTO customers (phone)
                VALUES ($1)
                RETURNING id
            """, phone)

            await conn.execute("""
                INSERT INTO customer_identifiers
                (customer_id, identifier_type, identifier_value)
                VALUES ($1, 'whatsapp', $2)
            """, customer_id, phone)

            return str(customer_id)

    raise ValueError("Could not resolve customer")
```

## Related Skills

- **database-crm-setup** - Schema design
- **agent-specialization** - Customer context
