# CRM Digital FTE Factory - KIND Cluster Deployment
# Optimized for KIND (Kubernetes IN Docker)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "CRM Digital FTE Factory - KIND Deploy" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "[1/9] Checking Docker..." -ForegroundColor Yellow
docker ps > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}
Write-Host "OK: Docker is running" -ForegroundColor Green

# Check if KIND cluster exists
Write-Host "`n[2/9] Checking KIND cluster..." -ForegroundColor Yellow
$kindPath = "$env:USERPROFILE\bin\kind.exe"
if (-not (Test-Path $kindPath)) {
    $kindPath = "kind"  # Try system PATH
}
kubectl cluster-info --context kind-kind > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: KIND cluster not found. Creating one..." -ForegroundColor Yellow
    & $kindPath create cluster --name kind
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to create KIND cluster" -ForegroundColor Red
        exit 1
    }
}
Write-Host "OK: KIND cluster is ready" -ForegroundColor Green

# Build Docker images
Write-Host "`n[3/9] Building Docker images..." -ForegroundColor Yellow

Write-Host "  Building backend API image..." -ForegroundColor Cyan
docker build -t crm-fte-api:latest -f Dockerfile .
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build backend API image" -ForegroundColor Red
    exit 1
}

Write-Host "  Building worker image..." -ForegroundColor Cyan
docker build -t crm-fte-worker:latest -f Dockerfile.worker .
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build worker image" -ForegroundColor Red
    exit 1
}

Write-Host "  Building frontend image..." -ForegroundColor Cyan
docker build -t crm-fte-frontend:latest -f omni-desk-frontend/Dockerfile ./omni-desk-frontend
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build frontend image" -ForegroundColor Red
    exit 1
}
Write-Host "OK: All images built" -ForegroundColor Green

# Load images into KIND
Write-Host "`n[4/9] Loading images into KIND cluster..." -ForegroundColor Yellow
$kindPath = "$env:USERPROFILE\bin\kind.exe"
if (-not (Test-Path $kindPath)) {
    $kindPath = "kind"  # Try system PATH
}
Write-Host "  Loading crm-fte-api:latest..." -ForegroundColor Cyan
& $kindPath load docker-image crm-fte-api:latest --name kind
Write-Host "  Loading crm-fte-worker:latest..." -ForegroundColor Cyan
& $kindPath load docker-image crm-fte-worker:latest --name kind
Write-Host "  Loading crm-fte-frontend:latest..." -ForegroundColor Cyan
& $kindPath load docker-image crm-fte-frontend:latest --name kind
Write-Host "OK: Images loaded into KIND" -ForegroundColor Green

# Deploy namespace and ConfigMaps
Write-Host "`n[5/9] Creating namespace and ConfigMaps..." -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
Write-Host "OK: Namespace and ConfigMaps created" -ForegroundColor Green

# Create secrets
Write-Host "`n[6/9] Creating Secrets..." -ForegroundColor Yellow
if (Test-Path "k8s/create-secrets.ps1") {
    & "k8s/create-secrets.ps1"
} else {
    Write-Host "  Applying secret.yaml..." -ForegroundColor Cyan
    kubectl apply -f k8s/secret.yaml
}
Write-Host "OK: Secrets created" -ForegroundColor Green

# Deploy PostgreSQL
Write-Host "`n[7/9] Deploying PostgreSQL..." -ForegroundColor Yellow
kubectl apply -f k8s/postgres.yaml
Write-Host "  Waiting for PostgreSQL pod to start (max 60s)..." -ForegroundColor Cyan
$timeout = 60
$elapsed = 0
while ($elapsed -lt $timeout) {
    $postgresStatus = kubectl get pod postgres-0 -n crm-digital-fte -o jsonpath="{.status.phase}" 2>$null
    if ($postgresStatus -eq "Running") {
        Write-Host "OK: PostgreSQL is running" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 5
    $elapsed += 5
    Write-Host "  Waiting... ($elapsed`s)" -ForegroundColor Gray
}

# Deploy Kafka
Write-Host "`n[8/9] Deploying Kafka..." -ForegroundColor Yellow
kubectl apply -f k8s/kafka.yaml
Write-Host "  Waiting for Kafka pod to start (max 60s)..." -ForegroundColor Cyan
$timeout = 60
$elapsed = 0
while ($elapsed -lt $timeout) {
    $kafkaStatus = kubectl get pod kafka-0 -n crm-digital-fte -o jsonpath="{.status.phase}" 2>$null
    if ($kafkaStatus -eq "Running") {
        Write-Host "OK: Kafka is running" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 5
    $elapsed += 5
    Write-Host "  Waiting... ($elapsed`s)" -ForegroundColor Gray
}

# Deploy application services
Write-Host "`n[9/9] Deploying application services..." -ForegroundColor Yellow
Write-Host "  Deploying Backend API..." -ForegroundColor Cyan
kubectl apply -f k8s/api.yaml
Write-Host "  Deploying Worker..." -ForegroundColor Cyan
kubectl apply -f k8s/worker.yaml
Write-Host "  Deploying Frontend and Ingress..." -ForegroundColor Cyan
kubectl apply -f k8s/web-form.yaml

Write-Host "`n  Waiting for pods to be ready (max 60s)..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

$timeout = 60
$elapsed = 0
while ($elapsed -lt $timeout) {
    $backendReady = kubectl get pods -n crm-digital-fte -l component=backend -o jsonpath="{.items[0].status.containerStatuses[0].ready}" 2>$null
    $frontendReady = kubectl get pods -n crm-digital-fte -l component=frontend -o jsonpath="{.items[0].status.containerStatuses[0].ready}" 2>$null

    if ($backendReady -eq "true" -and $frontendReady -eq "true") {
        Write-Host "OK: Application services are ready" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 5
    $elapsed += 5
    Write-Host "  Waiting... ($elapsed`s)" -ForegroundColor Gray
}

# Display status
Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "Deployment Status" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

Write-Host "`nPods:" -ForegroundColor Yellow
kubectl get pods -n crm-digital-fte -o wide

Write-Host "`nServices:" -ForegroundColor Yellow
kubectl get svc -n crm-digital-fte

Write-Host "`nIngress:" -ForegroundColor Yellow
kubectl get ingress -n crm-digital-fte

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "Access Instructions" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Use port forwarding to access services:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  # Frontend (Web Form)" -ForegroundColor Cyan
Write-Host "  kubectl port-forward svc/frontend 3000:3000 -n crm-digital-fte" -ForegroundColor White
Write-Host "  Then open: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "  # Backend API" -ForegroundColor Cyan
Write-Host "  kubectl port-forward svc/backend 8000:8000 -n crm-digital-fte" -ForegroundColor White
Write-Host "  Then open: http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "  # PostgreSQL (for debugging)" -ForegroundColor Cyan
Write-Host "  kubectl port-forward svc/postgres 5432:5432 -n crm-digital-fte" -ForegroundColor White
Write-Host ""

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Health Check Verification" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Test backend health
$backendPod = kubectl get pods -n crm-digital-fte -l component=backend -o jsonpath="{.items[0].metadata.name}" 2>$null
if ($backendPod) {
    Write-Host "Testing backend health endpoint..." -ForegroundColor Yellow
    $health = kubectl exec -n crm-digital-fte $backendPod -- curl -s http://localhost:8000/health 2>$null
    if ($health) {
        Write-Host "OK: Backend health - $health" -ForegroundColor Green
    } else {
        Write-Host "WARN: Backend not responding yet (may still be starting)" -ForegroundColor Yellow
    }
}

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "Useful Commands" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  kubectl logs -f -l component=backend -n crm-digital-fte" -ForegroundColor White
Write-Host "  kubectl logs -f -l component=frontend -n crm-digital-fte" -ForegroundColor White
Write-Host "  kubectl logs -f -l component=worker -n crm-digital-fte" -ForegroundColor White
Write-Host ""
Write-Host "Check status:" -ForegroundColor Yellow
Write-Host "  kubectl get all -n crm-digital-fte" -ForegroundColor White
Write-Host "  kubectl describe pods -n crm-digital-fte" -ForegroundColor White
Write-Host ""
Write-Host "Restart deployment:" -ForegroundColor Yellow
Write-Host "  kubectl rollout restart deployment/backend -n crm-digital-fte" -ForegroundColor White
Write-Host "  kubectl rollout restart deployment/frontend -n crm-digital-fte" -ForegroundColor White
Write-Host ""
Write-Host "Clean up:" -ForegroundColor Yellow
Write-Host "  kubectl delete namespace crm-digital-fte" -ForegroundColor White
Write-Host ""

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
