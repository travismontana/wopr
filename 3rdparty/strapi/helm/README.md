# Strapi 5 Helm Chart

Helm chart for deploying Strapi 5 CMS on Kubernetes with external PostgreSQL (CNPG).

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PostgreSQL database (e.g., CNPG cluster)

## Installation

### 1. Generate Secrets

Generate secure secrets for Strapi:

```bash
# Generate random secrets
openssl rand -base64 32  # For each secret
```

### 2. Update values.yaml

Create a custom values file (e.g., `values-prod.yaml`):

```yaml
strapi:
  nodeEnv: production
  adminJwtSecret: "your-generated-secret-1"
  apiTokenSalt: "your-generated-secret-2"
  appKeys: "key1,key2,key3,key4"
  jwtSecret: "your-generated-secret-3"
  transferTokenSalt: "your-generated-secret-4"

postgresql:
  external:
    host: "postgresql-cluster-rw.database.svc.cluster.local"
    database: "strapi"
    username: "strapi"
    password: "your-db-password"

ingress:
  enabled: true
  className: "traefik"
  hosts:
    - host: strapi.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
```

### 3. Install the Chart

```bash
helm install strapi ./strapi-helm -f values-prod.yaml
```

Or with ArgoCD:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: strapi
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/yourusername/yourrepo
    targetRevision: main
    path: charts/strapi
    helm:
      valueFiles:
        - values-prod.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: strapi
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## Configuration

### Key Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Strapi image repository | `naskio/strapi` |
| `image.tag` | Strapi image tag | `5.30.1` |
| `replicaCount` | Number of replicas | `1` |
| `postgresql.external.host` | PostgreSQL host | `postgresql-cluster-rw.database.svc.cluster.local` |
| `postgresql.external.database` | Database name | `strapi` |
| `persistence.enabled` | Enable persistent storage | `true` |
| `persistence.size` | PVC size | `10Gi` |
| `ingress.enabled` | Enable ingress | `false` |

### Using External Secrets

Instead of storing secrets in values.yaml:

```yaml
postgresql:
  existingSecret: "strapi-db-secret"
  existingSecretKey: "password"
```

Create the secret separately:

```bash
kubectl create secret generic strapi-db-secret \
  --from-literal=password=your-db-password
```

## Connecting to CNPG

If using CloudNativePG:

1. Create the database and user in CNPG:

```sql
CREATE DATABASE strapi;
CREATE USER strapi WITH PASSWORD 'secure-password';
GRANT ALL PRIVILEGES ON DATABASE strapi TO strapi;
```

2. Use the CNPG read-write service:

```yaml
postgresql:
  external:
    host: "postgresql-cluster-rw.database.svc.cluster.local"
```

## Health Checks

Strapi 5 provides `/_health` endpoint for liveness/readiness probes.

## Upgrading

```bash
helm upgrade strapi ./strapi-helm -f values-prod.yaml
```

## Uninstalling

```bash
helm uninstall strapi
```

Note: This will not delete PVCs. Delete manually if needed:

```bash
kubectl delete pvc strapi-uploads
```

## Troubleshooting

Check pod logs:
```bash
kubectl logs -f deployment/strapi
```

Check database connectivity:
```bash
kubectl exec -it deployment/strapi -- sh
nc -zv postgresql-cluster-rw.database.svc.cluster.local 5432
```
