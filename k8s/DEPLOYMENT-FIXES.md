# Deployment Fixes & Troubleshooting Guide
## CRM Digital FTE Factory - KIND Deployment

**Date:** 2026-02-12
**Status:** ✅ Application Images Built | ⚠️ Infrastructure Images Blocked by Network

---

## 🔧 Critical Fixes Applied

### 1. Frontend Dockerfile - Node Version Update

**Issue:** Frontend build failed with error:
```
You are using Node.js 18.20.8. For Next.js, Node.js version ">=20.9.0" is required.
```

**Fix:** Updated all stages in `omni-desk-frontend/Dockerfile`:
```diff
- FROM node:18-alpine AS deps
+ FROM node:20-alpine AS deps

- FROM node:18-alpine AS builder
+ FROM node:20-alpine AS builder

- FROM node:18-alpine AS runner
+ FROM node:20-alpine AS runner
```

**File:** `omni-desk-frontend/Dockerfile` (lines 15, 28, 48)

---

### 2. Frontend Dockerfile - Build Dependencies

**Issue:** TypeScript not available during build because only production dependencies were installed:
```
ERROR: Failed to transpile "next.config.ts".
Failed to install TypeScript, please install it manually to continue
```

**Root Cause:** The builder stage was copying `node_modules` from deps stage which only had production dependencies (`npm ci --only=production`).

**Fix:** Install ALL dependencies (including devDependencies) in builder stage:
```diff
 # Stage 2: Builder (All Dependencies)
 FROM node:20-alpine AS builder

 WORKDIR /app

+# Copy package files
+COPY package.json package-lock.json* ./
+
-# Copy dependencies from deps stage
-COPY --from=deps /app/node_modules ./node_modules
+# Install ALL dependencies (including devDependencies for building)
+RUN npm ci

 # Copy application code
 COPY . .
```

**File:** `omni-desk-frontend/Dockerfile` (lines 27-44)

---

### 3. TypeScript Type Errors

**Issue #1:** Property 'name' does not exist on type '{}'
```typescript
// app/api/conversations/route.ts:24
const customer = customerMap.get(conv.customer_id);
const customerName = customer?.name || customer?.email || customer?.phone || 'Unknown Customer';
//                            ^^^^
// ERROR: Property 'name' does not exist on type '{}'
```

**Fix:** Add proper TypeScript interface:
```typescript
interface Customer {
  id: number;
  name?: string;
  email?: string;
  phone?: string;
}

// Update Map type
const customerMap = new Map<number, Customer>(customers.map((c: any) => [c.id, c]));
```

**File:** `omni-desk-frontend/app/api/conversations/route.ts` (lines 3-27)

---

**Issue #2:** Cannot find name 'vi' (Vitest test setup)
```typescript
// vitest.setup.ts:14
vi.mock('next/navigation', () => ({ ... }))
// ERROR: Cannot find name 'vi'
```

**Fix:** Exclude test files from production TypeScript checking:
```diff
   "exclude": [
     "node_modules",
+    "**/*.test.ts",
+    "**/*.test.tsx",
+    "**/*.spec.ts",
+    "**/*.spec.tsx",
+    "vitest.config.ts",
+    "vitest.setup.ts"
   ]
```

**File:** `omni-desk-frontend/tsconfig.json` (line 33)

---

## 📦 Build Results

All application images successfully built:

```bash
$ docker images | grep crm-fte
crm-fte-api:latest        51b05f769df9   639MB   129MB
crm-fte-frontend:latest   446159108597   294MB   71.3MB
crm-fte-worker:latest     bc46f85b0f8b   639MB   129MB
```

**Build Times:**
- Backend API: ~30s (cached layers)
- Worker: ~30s (cached layers)
- Frontend: ~25 minutes (first build)
  - npm ci: ~10 minutes
  - Next.js build: ~7.2 minutes
  - TypeScript checks: ~4.3 minutes
  - Static page generation: ~12 seconds

---

## 🚀 Deployment to KIND

### Successfully Deployed:

```bash
✅ Namespace: crm-digital-fte
✅ ConfigMaps: backend-config, frontend-config
✅ Secrets: backend-secrets (with test values), gmail-credentials
✅ Deployments:
   - backend (2 replicas, HPA 2-5)
   - frontend (2 replicas)
   - worker (2 replicas, HPA 2-10)
✅ Services: backend, frontend
✅ Ingress: crm-digital-fte-ingress
✅ Application images loaded into KIND cluster
```

### Commands Used:

```bash
# Load application images into KIND
kind load docker-image crm-fte-api:latest crm-fte-worker:latest crm-fte-frontend:latest --name kind

# Create namespace and configs
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml

# Create secrets with test values
kubectl create secret generic backend-secrets \
  --from-literal=DATABASE_PASSWORD='crm_pass' \
  --from-literal=OPENAI_API_KEY='sk-test-key-placeholder' \
  --from-literal=TWILIO_ACCOUNT_SID='AC-placeholder-account-sid' \
  --from-literal=TWILIO_AUTH_TOKEN='placeholder-auth-token' \
  --from-literal=TWILIO_PHONE_NUMBER='+14155238886' \
  --from-literal=WHATSAPP_PHONE_NUMBER='whatsapp:+1234567890' \
  --from-literal=GMAIL_SENDER_EMAIL='support@example.com' \
  --namespace=crm-digital-fte

kubectl create secret generic gmail-credentials \
  --from-literal='credentials.json={"installed":{"client_id":"placeholder"}}' \
  --namespace=crm-digital-fte

# Deploy infrastructure
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/kafka.yaml

# Deploy application services
kubectl apply -f k8s/api.yaml
kubectl apply -f k8s/worker.yaml
kubectl apply -f k8s/web-form.yaml
```

---

## ⚠️ Current Blocker: Network Issue

### Problem:
PostgreSQL, Kafka, and Zookeeper pods stuck in `ImagePullBackOff` due to network timeouts pulling from Docker Hub:

```bash
$ kubectl get pods -n crm-digital-fte
NAME                       READY   STATUS                  RESTARTS   AGE
kafka-0                    0/1     ImagePullBackOff        0          9m
kafka-topics-init-xxx      0/1     ImagePullBackOff        0          9m
postgres-0                 0/1     Init:ImagePullBackOff   0          9m
zookeeper-0                0/1     ImagePullBackOff        0          9m
```

**Error Details:**
```
Failed to pull image "postgres:16": failed to pull and unpack image "docker.io/library/postgres:16":
failed to copy: httpReadSeeker: failed open: failed to do request:
Get "https://docker-images-prod.6aa30f8b08e16409b46e0173d6de2f56.r2.cloudflarestorage.com/...":
TLS handshake timeout
```

**Root Cause:** Regional/ISP network connectivity issue to Docker Hub CDN (Cloudflare R2).

---

## 🔧 Solution: Pre-Pull Infrastructure Images

When network is stable, manually pull and load images:

### Step 1: Pull Images Locally

```bash
# Pull infrastructure images
docker pull postgres:16
docker pull pgvector/pgvector:pg16
docker pull confluentinc/cp-zookeeper:7.5.0
docker pull confluentinc/cp-kafka:7.5.0
docker pull busybox:1.36  # Used by init containers
```

### Step 2: Load into KIND

```bash
# Load all infrastructure images into KIND cluster
kind load docker-image postgres:16 --name kind
kind load docker-image pgvector/pgvector:pg16 --name kind
kind load docker-image confluentinc/cp-zookeeper:7.5.0 --name kind
kind load docker-image confluentinc/cp-kafka:7.5.0 --name kind
kind load docker-image busybox:1.36 --name kind
```

### Step 3: Restart Failed Pods

```bash
# Delete pods to trigger recreation (they'll now use locally loaded images)
kubectl delete pod postgres-0 -n crm-digital-fte
kubectl delete pod kafka-0 -n crm-digital-fte
kubectl delete pod zookeeper-0 -n crm-digital-fte
kubectl delete pod kafka-topics-init-<xxx> -n crm-digital-fte

# Or restart entire namespace
kubectl delete namespace crm-digital-fte
# Then re-run deployment commands from above
```

---

## ✅ Verification Steps (After Infrastructure is Running)

### 1. Check Pod Status

```bash
# All pods should show READY 1/1 and STATUS Running
kubectl get pods -n crm-digital-fte

# Expected output:
NAME                       READY   STATUS    RESTARTS   AGE
backend-xxx-yyy            1/1     Running   0          5m
backend-xxx-zzz            1/1     Running   0          5m
frontend-xxx-yyy           1/1     Running   0          5m
frontend-xxx-zzz           1/1     Running   0          5m
worker-xxx-yyy             1/1     Running   0          5m
worker-xxx-zzz             1/1     Running   0          5m
postgres-0                 1/1     Running   0          6m
kafka-0                    1/1     Running   0          6m
zookeeper-0                1/1     Running   0          6m
```

### 2. Test Health Endpoints

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pods -n crm-digital-fte -l component=backend -o jsonpath="{.items[0].metadata.name}")

# Test backend health from inside cluster
kubectl exec -n crm-digital-fte $BACKEND_POD -- curl -s http://localhost:8000/health

# Expected response:
{"status":"healthy","env":"production"}
```

### 3. Port Forward Services

```bash
# Frontend (Web Support Form)
kubectl port-forward svc/frontend 3000:3000 -n crm-digital-fte
# Then open: http://localhost:3000

# Backend API
kubectl port-forward svc/backend 8000:8000 -n crm-digital-fte
# Then test: http://localhost:8000/health

# PostgreSQL (for debugging)
kubectl port-forward svc/postgres 5432:5432 -n crm-digital-fte
```

### 4. Check Logs

```bash
# Backend logs
kubectl logs -f -l component=backend -n crm-digital-fte

# Frontend logs
kubectl logs -f -l component=frontend -n crm-digital-fte

# Worker logs
kubectl logs -f -l component=worker -n crm-digital-fte

# PostgreSQL logs
kubectl logs postgres-0 -n crm-digital-fte

# Kafka logs
kubectl logs kafka-0 -n crm-digital-fte
```

### 5. Verify Ingress Configuration

```bash
# Check ingress
kubectl get ingress -n crm-digital-fte

# Describe ingress
kubectl describe ingress crm-digital-fte-ingress -n crm-digital-fte

# Expected routes:
# Host: crm-digital-fte.local
# Paths:
#   /           → frontend:3000  (Next.js Web Form)
#   /api        → backend:8000   (FastAPI)
#   /webhooks   → backend:8000   (WhatsApp, Gmail webhooks)
```

---

## 🐛 Common Issues & Solutions

### Issue: HPA Warning "failed to get metrics"

```
Warning: FailedComputeMetricsReplicas: invalid metrics (1 invalid out of 1)
```

**Cause:** KIND cluster doesn't have metrics-server installed by default.

**Solution (Optional):** Install metrics-server:
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Patch to work with KIND (insecure TLS)
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
```

**Note:** HPA will still scale based on replica counts, just won't have CPU/memory metrics.

---

### Issue: Secrets with "illegal base64 data"

```
Error from server (BadRequest): Secret in version "v1" cannot be handled as a Secret:
illegal base64 data at input byte 7
```

**Cause:** `k8s/secret.yaml` contains placeholder values that aren't valid base64.

**Solution:** Use `kubectl create secret` instead:
```bash
# See "Deployment to KIND" section above for secret creation commands
kubectl create secret generic backend-secrets --from-literal=KEY=value ...
```

---

### Issue: Init Containers Waiting

```
pod/backend-xxx-yyy   0/1   Init:0/1   0   5m
```

**Cause:** Init containers waiting for PostgreSQL and Kafka to be ready.

**Check:**
```bash
# View init container logs
kubectl logs <pod-name> -n crm-digital-fte -c wait-for-dependencies

# Check if postgres and kafka services exist
kubectl get svc -n crm-digital-fte | grep -E "postgres|kafka"
```

**Solution:** Ensure PostgreSQL and Kafka pods are Running before backend/worker pods will start.

---

## 📊 Resource Requirements

### Minimum Cluster Resources:
- **CPU:** 4 cores minimum (8 recommended)
- **Memory:** 8GB minimum (16GB recommended)
- **Disk:** 20GB free

### Pod Resource Requests:
```yaml
Backend API (per pod):
  requests: cpu=250m, memory=512Mi
  limits: cpu=1, memory=2Gi

Frontend (per pod):
  requests: cpu=100m, memory=256Mi
  limits: cpu=500m, memory=1Gi

Worker (per pod):
  requests: cpu=250m, memory=512Mi
  limits: cpu=1, memory=2Gi

PostgreSQL:
  requests: cpu=500m, memory=1Gi
  limits: cpu=2, memory=4Gi

Kafka:
  requests: cpu=500m, memory=1Gi
  limits: cpu=2, memory=4Gi
```

---

## 🔄 Clean Slate Redeployment

To completely reset and redeploy:

```bash
# Delete entire namespace
kubectl delete namespace crm-digital-fte

# Wait for deletion to complete
kubectl get namespace crm-digital-fte

# Rebuild images (if needed)
docker build -t crm-fte-api:latest -f Dockerfile .
docker build -t crm-fte-worker:latest -f Dockerfile.worker .
docker build -t crm-fte-frontend:latest -f omni-desk-frontend/Dockerfile ./omni-desk-frontend

# Load all images into KIND
kind load docker-image crm-fte-api:latest crm-fte-worker:latest crm-fte-frontend:latest --name kind
kind load docker-image postgres:16 pgvector/pgvector:pg16 confluentinc/cp-zookeeper:7.5.0 confluentinc/cp-kafka:7.5.0 --name kind

# Run deployment script
.\k8s\deploy-kind.ps1
```

---

## ✅ Success Criteria

**Task #8: Ingress Configuration**
- [x] Ingress resource defined in `k8s/web-form.yaml`
- [x] Routes configured for /, /api, /webhooks
- [x] Host: crm-digital-fte.local
- [x] Services correctly referenced

**Task #9: Health Checks**
- [x] Backend: GET /health endpoint implemented (src/api/main.py:77-80)
- [x] Backend: Readiness + Liveness probes configured (k8s/api.yaml:70-86)
- [x] Frontend: Readiness + Liveness probes on / (k8s/web-form.yaml:46-62)
- [x] Worker: Process-based liveness probe (k8s/worker.yaml:72-81)
- [x] Init containers wait for dependencies (all deployments)

---

## 📚 References

- [KIND Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [KIND Ingress Setup](https://kind.sigs.k8s.io/docs/user/ingress/)
- [Kubernetes Health Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Next.js Docker Best Practices](https://nextjs.org/docs/deployment#docker-image)

---

**Last Updated:** 2026-02-12
**Status:** Application ready, waiting for infrastructure image availability
