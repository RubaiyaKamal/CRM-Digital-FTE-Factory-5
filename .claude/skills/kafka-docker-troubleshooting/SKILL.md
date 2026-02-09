# Kafka Docker Compose Troubleshooting Skill

## Overview

This skill helps diagnose and fix Kafka startup issues in Docker Compose environments, specifically when Kafka health checks fail or dependent services can't start.

## Common Issues and Solutions

### Issue 1: Kafka Container Shows "Unhealthy" Status

**Symptoms:**
- `docker-compose ps` shows Kafka as "health: starting" for extended period
- Dependent services (API, workers) fail with "dependency failed to start: container crm_kafka is unhealthy"

**Root Cause:**
Kafka's health check takes time to pass. The default health check configuration requires:
- `start_period: 60s` - grace period before health checks count against retries
- `interval: 15s` - run health check every 15 seconds
- `retries: 10` - allow 10 failures before marking unhealthy

This means Kafka can take **2-3 minutes** to become healthy after startup.

**Solution Steps:**

1. **Verify Kafka is actually running:**
   ```bash
   docker-compose logs kafka --tail 30
   ```
   Look for: `[KafkaServer id=1] started`

2. **Test health check manually:**
   ```bash
   docker exec crm_kafka kafka-broker-api-versions --bootstrap-server localhost:9092
   ```
   If this returns API versions, Kafka is healthy - just waiting for Docker health check.

3. **Wait for health check to pass:**
   ```bash
   # Check status every 15 seconds
   watch -n 15 'docker-compose ps kafka'
   ```
   Or:
   ```bash
   # Windows: Check periodically
   docker-compose ps kafka
   ```

4. **Once healthy, start dependent services:**
   ```bash
   docker-compose up -d api web-form worker
   ```

### Issue 2: "Host Not Found in Upstream" Error (Web-Form)

**Symptoms:**
- Web-form container exits immediately
- Logs show: `nginx: [emerg] host not found in upstream "api" in /etc/nginx/conf.d/default.conf:13`

**Root Cause:**
Nginx tries to resolve upstream hostnames at startup. If the API service isn't running, nginx fails to start.

**Solution:**
```bash
# Start the full stack together
docker-compose up -d

# Or start services in order:
docker-compose up -d postgres zookeeper kafka
# Wait for Kafka health check
docker-compose up -d api worker
docker-compose up -d web-form
```

### Issue 3: Kafka Won't Start After System Reboot

**Symptoms:**
- Kafka starts but immediately exits
- Logs show: `FATAL [KafkaServer id=1] Fatal error during KafkaServer startup`

**Solution:**
```bash
# Stop all containers
docker-compose down

# Remove Kafka data volume (if safe to reset)
docker volume rm $(docker volume ls -q | grep kafka)

# Restart stack
docker-compose up -d
```

## Quick Diagnostic Commands

```bash
# Check all container statuses
docker-compose ps

# Check Kafka logs
docker-compose logs kafka --tail 50

# Check if Kafka is responding
docker exec crm_kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# Check Kafka topics
docker exec crm_kafka kafka-topics --list --bootstrap-server localhost:9092

# Test Kafka from host machine (requires kafka CLI tools)
kafka-topics --list --bootstrap-server localhost:9094
```

## Best Practices

1. **Always start full stack with `docker-compose up -d`**
   - Ensures proper startup order and dependency resolution

2. **Be patient with Kafka health checks**
   - Allow 2-3 minutes for Kafka to become healthy
   - Don't restart repeatedly - this resets the health check timer

3. **Monitor health status:**
   ```bash
   # Watch all services
   docker-compose ps

   # Focus on Kafka
   docker-compose ps kafka
   ```

4. **Check logs when troubleshooting:**
   ```bash
   # Recent logs
   docker-compose logs --tail 50

   # Follow logs live
   docker-compose logs -f kafka
   ```

5. **Clean restart if needed:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Health Check Configuration Explained

From `docker-compose.yml`:

```yaml
kafka:
  healthcheck:
    test: ["CMD", "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"]
    interval: 15s      # Run check every 15 seconds
    timeout: 10s       # Each check can take up to 10 seconds
    retries: 10        # Allow 10 failed checks
    start_period: 60s  # Grace period - checks don't count for first 60 seconds
```

**Total time to healthy:** 60s (grace) + up to 10 retries × 15s = **60-210 seconds**

## Troubleshooting Checklist

- [ ] All infrastructure services started? (`docker-compose ps`)
- [ ] Kafka logs show "started" message? (`docker-compose logs kafka`)
- [ ] Kafka health check passes manually? (`docker exec crm_kafka kafka-broker-api-versions ...`)
- [ ] Waited at least 3 minutes for health check?
- [ ] Dependent services (API, worker) exist and configured correctly?
- [ ] Nginx config references correct upstream hostnames?

## Related Skills

- `kafka-streaming` - Kafka event streaming configuration
- `kubernetes-deployment` - K8s deployment with health checks
- `database-crm-setup` - PostgreSQL setup and health checks

## Tags

#kafka #docker #troubleshooting #health-checks #startup #debugging
