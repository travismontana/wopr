# WOPR Config Service Helm Chart

Centralized configuration service with PostgreSQL backend for the WOPR system.

## Installation

```bash
# Add dependencies (if using external charts)
helm dependency update

# Install with default values
helm install wopr-config . -n wopr --create-namespace

# Install with custom values
helm install wopr-config . -n wopr \
  --set postgresql.password=supersecret \
  --set ingress.hosts[0].host=config.mydomain.com
```

## Configuration

See `values.yaml` for all configuration options.

### Key Settings

```yaml
# Database password (required in production)
postgresql:
  password: "changeme"

# Ingress configuration
ingress:
  enabled: true
  hosts:
    - host: wopr-config.studio.tailandtraillabs.org

# Resource limits
resources:
  limits:
    cpu: 500m
    memory: 512Mi
```

## Upgrading

```bash
helm upgrade wopr-config . -n wopr
```

## Uninstalling

```bash
helm uninstall wopr-config -n wopr
```

**Warning:** This will delete the PVC and all config data. Back up first!

## Accessing the Service

```bash
# Port-forward for local access
kubectl port-forward svc/wopr-config-wopr-config-service 8080:8080 -n wopr

# Check status
curl http://localhost:8080/health
```

## Troubleshooting

```bash
# Check pods
kubectl get pods -n wopr

# Check logs
kubectl logs -n wopr deployment/wopr-config-wopr-config-service
kubectl logs -n wopr statefulset/wopr-config-wopr-config-service-db

# Check database
kubectl exec -it wopr-config-wopr-config-service-db-0 -n wopr -- psql -U wopr -d config_db
```

## Components

- **StatefulSet**: PostgreSQL with 5Gi PVC
- **Deployment**: FastAPI config service
- **Services**: Database (headless) + API
- **Ingress**: HTTPS with cert-manager
- **Secret**: Database credentials
- **ConfigMap**: Schema initialization

## Architecture

```
Internet → Ingress (TLS) → Service → Deployment (FastAPI)
                                          ↓
                           Service → StatefulSet (PostgreSQL + PVC)
```
