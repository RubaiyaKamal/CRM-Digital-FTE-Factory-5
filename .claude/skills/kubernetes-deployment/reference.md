# Kubernetes Deployment Reference

## Overview
Deploy the Customer Success FTE to Kubernetes with horizontal pod autoscaling, health checks, ConfigMaps, Secrets, and zero-downtime updates.

## Key Capabilities
- Multi-pod deployment (API + Workers)
- Horizontal Pod Autoscaling (HPA)
- ConfigMap for configuration
- Secrets for credentials
- Service and Ingress setup
- Health probes

## Prerequisites
- Kubernetes cluster (minikube for local, cloud for production)
- kubectl CLI configured
- Docker images built and pushed
- Helm (optional)

## Constitutional Alignment
- **Principle 8: Kubernetes-Native Deployment** - Required deployment method
- **Principle 3: Zero Message Loss** - No downtime deployments
- **Principle 6: Observability** - Health checks and metrics
