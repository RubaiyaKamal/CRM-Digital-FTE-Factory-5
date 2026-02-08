# Load Testing Skill

## Skill Definition

**Name:** load-testing
**Version:** 1.0.0
**Type:** Testing
**Complexity:** Intermediate

## Description

Load testing with Locust to verify system handles concurrent requests across all channels with acceptable latency.

## Implementation

```python
# tests/load_test.py
from locust import HttpUser, task, between
import random

class WebFormUser(HttpUser):
    """Simulate users submitting support forms."""
    wait_time = between(2, 10)
    weight = 3  # Most common channel

    @task
    def submit_support_form(self):
        self.client.post("/support/submit", json={
            "name": f"Load Test User {random.randint(1, 10000)}",
            "email": f"load{random.randint(1, 10000)}@example.com",
            "subject": f"Test Query {random.randint(1, 100)}",
            "category": random.choice(['general', 'technical', 'billing']),
            "message": "Load test message to verify performance."
        })

class HealthCheckUser(HttpUser):
    """Monitor health during load."""
    wait_time = between(5, 15)
    weight = 1

    @task
    def check_health(self):
        self.client.get("/health")
```

## Running Load Tests

```bash
# 100 concurrent users
locust -f tests/load_test.py --host=http://localhost:8000 --users=100 --spawn-rate=10

# Target: >90% success rate, <3s p95 latency
```

## Related Skills

- **kubernetes-deployment** - Scaling under load
- **metrics-observability** - Performance metrics
