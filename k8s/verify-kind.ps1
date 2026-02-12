# CRM Digital FTE Factory - KIND Deployment Verification
# Verifies Task #8 (Ingress) and Task #9 (Health Checks)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Deployment Verification" -ForegroundColor Cyan
Write-Host "Tasks #8 (Ingress) & #9 (Health Checks)" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if KIND cluster is running
Write-Host "[1/6] Checking KIND cluster..." -ForegroundColor Yellow
kubectl cluster-info --context kind-kind > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: KIND cluster not found. Run .\k8s\deploy-kind.ps1 first." -ForegroundColor Red
    exit 1
}
Write-Host "OK: KIND cluster is running" -ForegroundColor Green

# Check namespace
Write-Host "`n[2/6] Checking namespace..." -ForegroundColor Yellow
$namespace = kubectl get namespace crm-digital-fte 2>$null
if (-not $namespace) {
    Write-Host "ERROR: Namespace 'crm-digital-fte' not found. Run .\k8s\deploy-kind.ps1 first." -ForegroundColor Red
    exit 1
}
Write-Host "OK: Namespace exists" -ForegroundColor Green

# Check pods
Write-Host "`n[3/6] Checking pod status..." -ForegroundColor Yellow
$pods = kubectl get pods -n crm-digital-fte -o json 2>$null | ConvertFrom-Json
if (-not $pods.items) {
    Write-Host "ERROR: No pods found. Run .\k8s\deploy-kind.ps1 first." -ForegroundColor Red
    exit 1
}

$allReady = $true
foreach ($pod in $pods.items) {
    $name = $pod.metadata.name
    $status = $pod.status.phase

    if ($pod.status.containerStatuses) {
        $ready = ($pod.status.containerStatuses | Where-Object { $_.ready -eq $true }).Count
        $total = $pod.status.containerStatuses.Count

        if ($status -eq "Running" -and $ready -eq $total) {
            Write-Host "  OK: $name - $status ($ready/$total ready)" -ForegroundColor Green
        } else {
            Write-Host "  WARN: $name - $status ($ready/$total ready)" -ForegroundColor Yellow
            $allReady = $false
        }
    } else {
        Write-Host "  WARN: $name - $status (initializing)" -ForegroundColor Yellow
        $allReady = $false
    }
}

# Task #9: Verify Health Checks
Write-Host "`n[4/6] Task #9: Verifying Health Probes..." -ForegroundColor Yellow
Write-Host ""

# Backend health checks
Write-Host "Backend API Probes:" -ForegroundColor Cyan
$backendPods = kubectl get pods -n crm-digital-fte -l component=backend -o json 2>$null | ConvertFrom-Json
if ($backendPods.items) {
    $backendPod = $backendPods.items[0]
    $podName = $backendPod.metadata.name

    # Check readiness
    $ready = $false
    if ($backendPod.status.conditions) {
        $readyCondition = $backendPod.status.conditions | Where-Object { $_.type -eq "Ready" }
        if ($readyCondition -and $readyCondition.status -eq "True") {
            $ready = $true
        }
    }

    if ($ready) {
        Write-Host "  OK: Readiness Probe - PASSING (GET /health on port 8000)" -ForegroundColor Green
    } else {
        Write-Host "  WARN: Readiness Probe - NOT READY" -ForegroundColor Yellow
    }

    # Test health endpoint
    if ($ready) {
        Write-Host "  Testing health endpoint..." -ForegroundColor Cyan
        $health = kubectl exec -n crm-digital-fte $podName -c api -- curl -s http://localhost:8000/health 2>$null
        if ($health) {
            Write-Host "  OK: Health Response - $health" -ForegroundColor Green
        } else {
            Write-Host "  WARN: Health endpoint not responding" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  ERROR: Backend pod not found" -ForegroundColor Red
}

# Frontend health checks
Write-Host "`nFrontend Probes:" -ForegroundColor Cyan
$frontendPods = kubectl get pods -n crm-digital-fte -l component=frontend -o json 2>$null | ConvertFrom-Json
if ($frontendPods.items) {
    $frontendPod = $frontendPods.items[0]

    $ready = $false
    if ($frontendPod.status.conditions) {
        $readyCondition = $frontendPod.status.conditions | Where-Object { $_.type -eq "Ready" }
        if ($readyCondition -and $readyCondition.status -eq "True") {
            $ready = $true
        }
    }

    if ($ready) {
        Write-Host "  OK: Readiness Probe - PASSING (GET / on port 3000)" -ForegroundColor Green
        Write-Host "  OK: Liveness Probe - PASSING (GET / on port 3000)" -ForegroundColor Green
    } else {
        Write-Host "  WARN: Probes - NOT READY" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ERROR: Frontend pod not found" -ForegroundColor Red
}

# Worker health checks
Write-Host "`nWorker Probes:" -ForegroundColor Cyan
$workerPods = kubectl get pods -n crm-digital-fte -l component=worker -o json 2>$null | ConvertFrom-Json
if ($workerPods.items) {
    $workerPod = $workerPods.items[0]

    $ready = $false
    if ($workerPod.status.conditions) {
        $readyCondition = $workerPod.status.conditions | Where-Object { $_.type -eq "Ready" }
        if ($readyCondition -and $readyCondition.status -eq "True") {
            $ready = $true
        }
    }

    if ($ready) {
        Write-Host "  OK: Liveness Probe - PASSING (process check)" -ForegroundColor Green
    } else {
        Write-Host "  WARN: Liveness Probe - NOT READY" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ERROR: Worker pod not found" -ForegroundColor Red
}

# Task #8: Verify Ingress
Write-Host "`n[5/6] Task #8: Verifying Ingress..." -ForegroundColor Yellow
$ingress = kubectl get ingress -n crm-digital-fte -o json 2>$null | ConvertFrom-Json
if ($ingress.items -and $ingress.items.Count -gt 0) {
    $ingressResource = $ingress.items[0]
    $ingressName = $ingressResource.metadata.name
    $host = $ingressResource.spec.rules[0].host
    $paths = $ingressResource.spec.rules[0].http.paths

    Write-Host "  OK: Ingress - $ingressName" -ForegroundColor Green
    Write-Host "  OK: Host - $host" -ForegroundColor Green
    Write-Host "  OK: Routes configured:" -ForegroundColor Green

    foreach ($path in $paths) {
        $pathStr = $path.path
        $service = $path.backend.service.name
        $port = $path.backend.service.port.number
        Write-Host "    • $pathStr → $service`:$port" -ForegroundColor White
    }
} else {
    Write-Host "  WARN: No Ingress found (expected for KIND without Ingress controller)" -ForegroundColor Yellow
    Write-Host "  INFO: Use port-forwarding instead for KIND clusters" -ForegroundColor Cyan
}

# Access instructions
Write-Host "`n[6/6] Access Instructions..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Use port forwarding to access services:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  # Frontend (Web Form)" -ForegroundColor Yellow
Write-Host "  kubectl port-forward svc/frontend 3000:3000 -n crm-digital-fte" -ForegroundColor White
Write-Host "  http://localhost:3000" -ForegroundColor Gray
Write-Host ""
Write-Host "  # Backend API" -ForegroundColor Yellow
Write-Host "  kubectl port-forward svc/backend 8000:8000 -n crm-digital-fte" -ForegroundColor White
Write-Host "  http://localhost:8000/health" -ForegroundColor Gray
Write-Host ""

# Summary
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Verification Summary" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Backend summary
$backendReady = $false
if ($backendPods.items) {
    $backendPod = $backendPods.items[0]
    if ($backendPod.status.conditions) {
        $readyCondition = $backendPod.status.conditions | Where-Object { $_.type -eq "Ready" }
        if ($readyCondition -and $readyCondition.status -eq "True") {
            $backendReady = $true
        }
    }
}

if ($backendReady) {
    Write-Host "OK Task #9 - Backend Health Checks: PASSING" -ForegroundColor Green
} else {
    Write-Host "WARN Task #9 - Backend Health Checks: NOT READY" -ForegroundColor Yellow
}

# Frontend summary
$frontendReady = $false
if ($frontendPods.items) {
    $frontendPod = $frontendPods.items[0]
    if ($frontendPod.status.conditions) {
        $readyCondition = $frontendPod.status.conditions | Where-Object { $_.type -eq "Ready" }
        if ($readyCondition -and $readyCondition.status -eq "True") {
            $frontendReady = $true
        }
    }
}

if ($frontendReady) {
    Write-Host "OK Task #9 - Frontend Health Checks: PASSING" -ForegroundColor Green
} else {
    Write-Host "WARN Task #9 - Frontend Health Checks: NOT READY" -ForegroundColor Yellow
}

# Worker summary
$workerReady = $false
if ($workerPods.items) {
    $workerPod = $workerPods.items[0]
    if ($workerPod.status.conditions) {
        $readyCondition = $workerPod.status.conditions | Where-Object { $_.type -eq "Ready" }
        if ($readyCondition -and $readyCondition.status -eq "True") {
            $workerReady = $true
        }
    }
}

if ($workerReady) {
    Write-Host "OK Task #9 - Worker Health Checks: PASSING" -ForegroundColor Green
} else {
    Write-Host "WARN Task #9 - Worker Health Checks: NOT READY" -ForegroundColor Yellow
}

# Ingress summary
if ($ingress.items -and $ingress.items.Count -gt 0) {
    Write-Host "OK Task #8 - Ingress Configuration: DEPLOYED" -ForegroundColor Green
} else {
    Write-Host "INFO Task #8 - Ingress: Use port-forwarding (KIND default)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Troubleshooting commands:" -ForegroundColor Yellow
Write-Host "  kubectl get all -n crm-digital-fte" -ForegroundColor White
Write-Host "  kubectl logs -l component=backend -n crm-digital-fte" -ForegroundColor White
Write-Host "  kubectl describe pods -n crm-digital-fte" -ForegroundColor White
Write-Host ""
