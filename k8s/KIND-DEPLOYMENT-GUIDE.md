# KIND Cluster Deployment Guide
## CRM Digital FTE Factory

This guide explains how to deploy to your KIND (Kubernetes IN Docker) cluster.

## Quick Start

### 1. Deploy Everything
```powershell
cd "C:\Users\Lap Zone\kids-book\CRM-Digital-FTE-Factory-5"
.\k8s\deploy-kind.ps1
```

This script will:
- ✓ Check Docker is running
- ✓ Verify KIND cluster exists
- ✓ Build all 3 Docker images (API, Worker, Frontend)
- ✓ **Load images into KIND cluster** (critical step!)
- ✓ Deploy namespace, ConfigMaps, Secrets
- ✓ Deploy PostgreSQL and Kafka
- ✓ Deploy Backend API, Worker, Frontend
- ✓ Verify health checks (Task #9)
- ✓ Display Ingress configuration (Task #8)

### 2. Verify Deployment
```powershell
.\k8s\verify-kind.ps1
```

This will check:
- Task #8: Ingress configuration
- Task #9: All health probes (Backend, Frontend, Worker)
- Pod readiness status
- Service endpoints

---

## Why KIND is Different from Minikube

### Image Loading (Critical!)

**Minikube:**
```bash
eval $(minikube docker-env)  # Share Docker daemon
docker build -t app:latest .  # Build directly
```

**KIND:**
```bash
docker build -t app:latest .          # Build locally
kind load docker-image app:latest     # Load into cluster
```

**Our Solution:** `deploy-kind.ps1` handles this automatically!

---

## Access Your Application

### Option 1: Port Forwarding (Recommended for KIND)

#### Frontend (Web Support Form)
```powershell
kubectl port-forward svc/frontend 3000:3000 -n crm-digital-fte
```
Then open: **http://localhost:3000**

#### Backend API
```powershell
kubectl port-forward svc/backend 8000:8000 -n crm-digital-fte
```
Then test: **http://localhost:8000/health**

Expected response:
```json
{"status":"healthy","env":"production"}
```

### Option 2: Ngrok (Already Running!)

You already have ngrok forwarding to port 8000:
```
https://stepless-erose-yessenia.ngrok-free.dev → http://localhost:8000
```

1. Start port-forward: `kubectl port-forward svc/backend 8000:8000 -n crm-digital-fte`
2. Your ngrok URL will now route to the Kubernetes backend!
3. Test: `https://stepless-erose-yessenia.ngrok-free.dev/health`

---

## Task #8: Ingress Verification ✅

### Configuration Located
File: `k8s/web-form.yaml:88-123`

### Routes Defined
```yaml
Host: crm-digital-fte.local
Routes:
  /           → frontend:3000  (Next.js Web Form)
  /api        → backend:8000   (FastAPI)
  /webhooks   → backend:8000   (WhatsApp, Gmail webhooks)
```

### KIND Ingress Setup

KIND doesn't include an Ingress controller by default. Two options:

#### Option A: Use Port Forwarding (Simplest)
Already documented above - no additional setup needed!

#### Option B: Install Ingress Controller (Optional)
```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for it to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s

# Add to hosts file
echo "127.0.0.1 crm-digital-fte.local" | sudo tee -a /etc/hosts

# Access via Ingress
http://crm-digital-fte.local/
```

---

## Task #9: Health Checks Verification ✅

### Backend API (`k8s/api.yaml:70-86`)
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5

livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 10
```

**Endpoint:** `src/api/main.py:77-80`
```python
@app.get("/health")
async def health():
    return {"status": "healthy", "env": settings.app_env}
```

### Frontend (`k8s/web-form.yaml:46-62`)
```yaml
readinessProbe:
  httpGet:
    path: /
    port: 3000

livenessProbe:
  httpGet:
    path: /
    port: 3000
```

### Worker (`k8s/worker.yaml:72-81`)
```yaml
livenessProbe:
  exec:
    command: ["sh", "-c", "pgrep -f src.workers.response_handler"]
  initialDelaySeconds: 30
  periodSeconds: 30
```

---

## Monitoring & Troubleshooting

### Check All Resources
```powershell
kubectl get all -n crm-digital-fte
```

### Pod Status
```powershell
kubectl get pods -n crm-digital-fte -o wide
```

Expected output:
```
NAME                       READY   STATUS    RESTARTS   AGE
backend-xxx-yyy            1/1     Running   0          5m
backend-xxx-zzz            1/1     Running   0          5m
frontend-xxx-yyy           1/1     Running   0          5m
frontend-xxx-zzz           1/1     Running   0          5m
worker-xxx-yyy             1/1     Running   0          5m
worker-xxx-zzz             1/1     Running   0          5m
postgres-0                 1/1     Running   0          6m
kafka-0                    1/1     Running   0          6m
```

### View Logs
```powershell
# Backend logs
kubectl logs -f -l component=backend -n crm-digital-fte

# Frontend logs
kubectl logs -f -l component=frontend -n crm-digital-fte

# Worker logs
kubectl logs -f -l component=worker -n crm-digital-fte

# Specific pod
kubectl logs <pod-name> -n crm-digital-fte
```

### Describe Pod (for events)
```powershell
kubectl describe pod <pod-name> -n crm-digital-fte
```

### Test Health Endpoint from Inside Cluster
```powershell
$backendPod = kubectl get pods -n crm-digital-fte -l component=backend -o jsonpath="{.items[0].metadata.name}"
kubectl exec -n crm-digital-fte $backendPod -c api -- curl http://localhost:8000/health
```

---

## Common Issues & Solutions

### Issue: ImagePullBackOff
**Cause:** Docker image not loaded into KIND cluster

**Solution:**
```powershell
# Rebuild and reload
docker build -t crm-fte-api:latest -f Dockerfile .
kind load docker-image crm-fte-api:latest --name kind

# Restart deployment
kubectl rollout restart deployment/backend -n crm-digital-fte
```

### Issue: CrashLoopBackOff
**Cause:** Application errors or missing dependencies

**Solution:**
```powershell
# Check logs
kubectl logs <pod-name> -n crm-digital-fte

# Check if secrets exist
kubectl get secrets -n crm-digital-fte

# Verify environment variables
kubectl exec <pod-name> -n crm-digital-fte -- env | grep DATABASE_URL
```

### Issue: Init Container Waiting
**Cause:** PostgreSQL or Kafka not ready

**Solution:**
```powershell
# Check PostgreSQL
kubectl get pod postgres-0 -n crm-digital-fte
kubectl logs postgres-0 -n crm-digital-fte

# Check Kafka
kubectl get pod kafka-0 -n crm-digital-fte
kubectl logs kafka-0 -n crm-digital-fte

# Check init container logs
kubectl logs <pod-name> -n crm-digital-fte -c wait-for-dependencies
```

---

## Clean Up & Redeploy

### Quick Restart
```powershell
# Restart specific component
kubectl rollout restart deployment/backend -n crm-digital-fte
kubectl rollout restart deployment/frontend -n crm-digital-fte
kubectl rollout restart deployment/worker -n crm-digital-fte
```

### Full Redeploy
```powershell
# Delete namespace (removes all resources)
kubectl delete namespace crm-digital-fte

# Redeploy everything
.\k8s\deploy-kind.ps1
```

### Nuclear Option (Complete Reset)
```powershell
# Delete KIND cluster
kind delete cluster --name kind

# Recreate and deploy
kind create cluster --name kind
.\k8s\deploy-kind.ps1
```

---

## Deployment Timeline

Based on your hardware (4 CPUs, 8GB RAM):

1. **Docker image builds:** ~3-5 minutes
2. **Image loading to KIND:** ~1-2 minutes
3. **PostgreSQL ready:** ~30-60 seconds
4. **Kafka ready:** ~30-60 seconds
5. **Backend/Frontend ready:** ~30-60 seconds
6. **Total time:** ~6-10 minutes

---

## Success Criteria

### Task #8: Ingress ✅
- [x] Ingress resource defined in `k8s/web-form.yaml`
- [x] Routes configured for /, /api, /webhooks
- [x] Host: crm-digital-fte.local
- [x] Services correctly referenced

### Task #9: Health Checks ✅
- [x] Backend: GET /health endpoint implemented
- [x] Backend: Readiness + Liveness probes configured
- [x] Frontend: Readiness + Liveness probes on /
- [x] Worker: Process-based liveness probe
- [x] Init containers wait for dependencies

---

## Next Steps

1. **Run deployment:** `.\k8s\deploy-kind.ps1`
2. **Verify health:** `.\k8s\verify-kind.ps1`
3. **Port forward frontend:** `kubectl port-forward svc/frontend 3000:3000 -n crm-digital-fte`
4. **Test web form:** Open http://localhost:3000
5. **Submit a test ticket** and verify it flows through Kafka → Worker → Database

---

## Integration with Your Ngrok Setup

Your ngrok is already forwarding to port 8000. To integrate:

1. **Start backend port-forward:**
   ```powershell
   kubectl port-forward svc/backend 8000:8000 -n crm-digital-fte
   ```

2. **Your ngrok URL now routes to Kubernetes!**
   - WhatsApp webhook: `https://stepless-erose-yessenia.ngrok-free.dev/webhooks/whatsapp`
   - Health check: `https://stepless-erose-yessenia.ngrok-free.dev/health`

3. **Update Twilio webhook URL (if needed):**
   - URL: `https://stepless-erose-yessenia.ngrok-free.dev/webhooks/whatsapp`
   - Method: POST

---

## Documentation References

- [KIND Quick Start](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [KIND Ingress Setup](https://kind.sigs.k8s.io/docs/user/ingress/)
- [Kubernetes Health Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

---

**Need help?** Check logs first:
```powershell
kubectl logs -f -l component=backend -n crm-digital-fte
kubectl get events -n crm-digital-fte --sort-by='.lastTimestamp'
```
