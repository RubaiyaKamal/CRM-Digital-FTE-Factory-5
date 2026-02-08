# Kubernetes Deployment Skill

## Skill Definition

**Name:** kubernetes-deployment
**Version:** 1.0.0
**Type:** Infrastructure
**Complexity:** Advanced

## Description

Deploy Customer Success FTE to Kubernetes with production-grade configuration including autoscaling, secrets management, and zero-downtime updates.

## Manifest Structure

```
k8s/
├── namespace.yaml
├── configmap.yaml
├── secrets.yaml
├── deployment-api.yaml
├── deployment-worker.yaml
├── service.yaml
├── ingress.yaml
└── hpa.yaml
```

## Implementation

### Step 1: Create Namespace
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: customer-success-fte
  labels:
    app: customer-success-fte
```

### Step 2: ConfigMap for Configuration
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fte-config
  namespace: customer-success-fte
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  KAFKA_BOOTSTRAP_SERVERS: "kafka.kafka.svc.cluster.local:9092"
  POSTGRES_HOST: "postgres.customer-success-fte.svc.cluster.local"
  POSTGRES_DB: "fte_db"
  GMAIL_ENABLED: "true"
  WHATSAPP_ENABLED: "true"
  WEBFORM_ENABLED: "true"
  MAX_EMAIL_LENGTH: "2000"
  MAX_WHATSAPP_LENGTH: "1600"
```

### Step 3: API Deployment
```yaml
# k8s/deployment-api.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fte-api
  namespace: customer-success-fte
spec:
  replicas: 3
  selector:
    matchLabels:
      app: customer-success-fte
      component: api
  template:
    metadata:
      labels:
        app: customer-success-fte
        component: api
    spec:
      containers:
      - name: fte-api
        image: your-registry/customer-success-fte:latest
        command: ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: fte-config
        - secretRef:
            name: fte-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

### Step 4: Worker Deployment
```yaml
# k8s/deployment-worker.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fte-message-processor
  namespace: customer-success-fte
spec:
  replicas: 3
  selector:
    matchLabels:
      app: customer-success-fte
      component: message-processor
  template:
    metadata:
      labels:
        app: customer-success-fte
        component: message-processor
    spec:
      containers:
      - name: message-processor
        image: your-registry/customer-success-fte:latest
        command: ["python", "workers/message_processor.py"]
        envFrom:
        - configMapRef:
            name: fte-config
        - secretRef:
            name: fte-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

### Step 5: Horizontal Pod Autoscaler
```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fte-api-hpa
  namespace: customer-success-fte
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fte-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fte-worker-hpa
  namespace: customer-success-fte
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fte-message-processor
  minReplicas: 3
  maxReplicas: 30
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Step 6: Service and Ingress
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: customer-success-fte
  namespace: customer-success-fte
spec:
  selector:
    app: customer-success-fte
    component: api
  ports:
  - port: 80
    targetPort: 8000
```

## Deployment Commands

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create ConfigMap and Secrets
kubectl apply -f k8s/configmap.yaml
kubectl create secret generic fte-secrets \
  --from-literal=OPENAI_API_KEY=$OPENAI_API_KEY \
  --from-literal=POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
  --from-literal=TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN \
  -n customer-success-fte

# Deploy applications
kubectl apply -f k8s/deployment-api.yaml
kubectl apply -f k8s/deployment-worker.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml

# Verify deployments
kubectl get pods -n customer-success-fte
kubectl get svc -n customer-success-fte
```

## Related Skills

- **agent-specialization** - Application code
- **kafka-streaming** - Worker consumes from Kafka
- **metrics-observability** - Health endpoints
