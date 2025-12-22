# WOPR-API Helm Chart

Copyright (c) 2025 Bob Bomar <bob@bomar.us>  
Licensed under the MIT License

---

## Overview

Helm chart for deploying WOPR API and Celery Workers.

**Components:**
- **API Deployment** - FastAPI application (uvicorn)
- **Worker Deployment** - Celery workers for async tasks
- **Service** - ClusterIP service for API
- **Ingress** - Optional ingress with TLS
- **HPA** - Horizontal Pod Autoscaler for API and Workers
- **PDB** - Pod Disruption Budget for high availability

---

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PostgreSQL database (external or in-cluster)
- Redis (external or in-cluster)

---

## Quick Start

```bash
# Add the repo (if published)
# helm repo add wopr https://charts.example.com/wopr
# helm repo update

# Install with default values
helm install wopr-api ./wopr-api

# Install with custom values
helm install wopr-api ./wopr-api -f my-values.yaml

# Install in specific namespace
helm install wopr-api ./wopr-api -n wopr --create-namespace
```

---

## Configuration

### Image Configuration

```yaml
image:
  repository: your-registry/wopr-api
  tag: "0.1.0"
  pullPolicy: IfNotPresent
```

### API Configuration

```yaml
api:
  enabled: true
  replicaCount: 2
  
  service:
    type: ClusterIP
    port: 8000
  
  resources:
    limits:
      cpu: 1000m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 256Mi
  
  autoscaling:
    enabled: false
    minReplicas: 2
    maxReplicas: 10
```

### Worker Configuration

```yaml
worker:
  enabled: true
  replicaCount: 3
  
  resources:
    limits:
      cpu: 2000m
      memory: 2Gi
    requests:
      cpu: 500m
      memory: 1Gi
  
  concurrency: 4  # Celery worker concurrency
  logLevel: info
```

### Ingress Configuration

```yaml
ingress:
  enabled: true
  className: "traefik"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: wopr.studio.local
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: wopr-api-tls
      hosts:
        - wopr.studio.local
```

### Database & Redis

```yaml
# Use existing external services
secrets:
  DATABASE_URL: "postgresql://user:pass@host:5432/db"

env:
  REDIS_URL: "redis://redis-host:6379/0"

# OR deploy with chart (not recommended for production)
postgresql:
  enabled: true
  host: "wopr-db.svc"
  port: 5432
  database: "wopr_main"
  username: "wopr"

redis:
  enabled: true
  host: "wopr-redis.svc"
  port: 6379
```

---

## Installation Examples

### Basic Installation

```bash
helm install wopr-api ./wopr-api \
  --set image.repository=your-registry/wopr-api \
  --set image.tag=0.1.0 \
  --set secrets.DATABASE_URL="postgresql://..." \
  --set secrets.JWT_SECRET_KEY="your-secret-key"
```

### Production Installation

```bash
# Create values file
cat > prod-values.yaml <<EOF
image:
  repository: your-registry/wopr-api
  tag: 0.1.0
  pullPolicy: Always

api:
  replicaCount: 3
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 20

worker:
  replicaCount: 5
  autoscaling:
    enabled: true
    minReplicas: 5
    maxReplicas: 50
  concurrency: 8

ingress:
  enabled: true
  className: traefik
  hosts:
    - host: wopr.production.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: wopr-prod-tls
      hosts:
        - wopr.production.com

secrets:
  DATABASE_URL: "postgresql://wopr:CHANGEME@postgres.svc:5432/wopr"
  JWT_SECRET_KEY: "GENERATE-SECURE-KEY"

env:
  REDIS_URL: "redis://redis.svc:6379/0"
  OTEL_ENABLED: "true"
  OTEL_ENDPOINT: "http://tempo.observability:4317"
EOF

# Install
helm install wopr-api ./wopr-api -f prod-values.yaml -n production
```

### Development Installation

```bash
# Minimal setup for testing
helm install wopr-api ./wopr-api \
  --set api.replicaCount=1 \
  --set worker.replicaCount=1 \
  --set ingress.enabled=false \
  --set secrets.DATABASE_URL="postgresql://..." \
  --set secrets.JWT_SECRET_KEY="dev-secret"
```

---

## Upgrading

```bash
# Upgrade with new values
helm upgrade wopr-api ./wopr-api -f new-values.yaml

# Upgrade with new image tag
helm upgrade wopr-api ./wopr-api --set image.tag=0.2.0

# Rollback
helm rollback wopr-api 1
```

---

## Scaling

### Manual Scaling

```bash
# Scale API
kubectl scale deployment wopr-api-api --replicas=5

# Scale Workers
kubectl scale deployment wopr-api-worker --replicas=10
```

### Autoscaling

Enable in values.yaml:

```yaml
api:
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 80

worker:
  autoscaling:
    enabled: true
    minReplicas: 5
    maxReplicas: 50
    targetCPUUtilizationPercentage: 80
```

---

## Monitoring

### Prometheus Metrics

API exposes metrics at `/metrics`:

```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true  # Requires prometheus-operator
    interval: 30s
```

### Health Checks

- **Liveness:** `GET /health`
- **Readiness:** `GET /ready`

---

## Secrets Management

### External Secrets Operator

```yaml
# Don't use .Values.secrets, create ExternalSecret instead
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: wopr-api-secrets
spec:
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: wopr-api
  data:
    - secretKey: database-url
      remoteRef:
        key: wopr/database-url
    - secretKey: jwt-secret-key
      remoteRef:
        key: wopr/jwt-secret
```

### Sealed Secrets

```bash
# Create sealed secret
kubectl create secret generic wopr-api \
  --from-literal=database-url="postgresql://..." \
  --from-literal=jwt-secret-key="..." \
  --dry-run=client -o yaml | \
  kubeseal -o yaml > sealed-secret.yaml

kubectl apply -f sealed-secret.yaml
```

---

## Troubleshooting

### Check Pod Status

```bash
# API pods
kubectl get pods -l app.kubernetes.io/component=api

# Worker pods
kubectl get pods -l app.kubernetes.io/component=worker

# Logs
kubectl logs -l app.kubernetes.io/component=api -f
kubectl logs -l app.kubernetes.io/component=worker -f
```

### Database Connection Issues

```bash
# Check secret
kubectl get secret wopr-api -o yaml

# Test connection from pod
kubectl exec -it deployment/wopr-api-api -- psql $DATABASE_URL -c "SELECT 1"
```

### Worker Not Processing Tasks

```bash
# Check Redis connection
kubectl exec -it deployment/wopr-api-worker -- redis-cli -u $REDIS_URL ping

# Check Celery status
kubectl exec -it deployment/wopr-api-worker -- celery -A app.tasks inspect active
```

---

## Uninstalling

```bash
# Uninstall release
helm uninstall wopr-api

# Clean up PVCs (if any)
kubectl delete pvc -l app.kubernetes.io/instance=wopr-api
```

---

## Parameters Reference

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Image repository | `your-registry/wopr-api` |
| `image.tag` | Image tag | `0.1.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `api.replicaCount` | Number of API replicas | `2` |
| `api.service.port` | API service port | `8000` |
| `api.resources.limits.cpu` | API CPU limit | `1000m` |
| `api.resources.limits.memory` | API memory limit | `512Mi` |
| `worker.replicaCount` | Number of worker replicas | `3` |
| `worker.concurrency` | Celery concurrency | `4` |
| `worker.resources.limits.cpu` | Worker CPU limit | `2000m` |
| `worker.resources.limits.memory` | Worker memory limit | `2Gi` |
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class | `traefik` |
| `secrets.DATABASE_URL` | Database connection string | Required |
| `secrets.JWT_SECRET_KEY` | JWT secret key | Required |
| `env.REDIS_URL` | Redis connection string | `redis://wopr-redis.svc:6379/0` |

See `values.yaml` for complete reference.

---

## License

MIT License - see LICENSE file
