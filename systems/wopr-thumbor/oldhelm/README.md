# Thumbor Helm Chart

Image processing service for the WOPR system using Thumbor.

## Overview

Thumbor is an open-source smart imaging service that enables on-demand image cropping, resizing, and filters. This chart deploys Thumbor with NFS-backed storage for WOPR image processing.

## Installation

```bash
# Install with default values
helm install thumbor . -n wopr --create-namespace

# Install with custom values
helm install thumbor . -n wopr \
  --set nfs.server=your-nfs-server \
  --set nfs.path=/your/nfs/path \
  --set ingress.hosts[0].host=thumbor.yourdomain.com
```

## Configuration

See `values.yaml` for all configuration options.

### Key Settings

```yaml
# NFS configuration
nfs:
  enabled: true
  server: danas.hangar.bpfx.org
  path: /volume2/wopr

# Ingress configuration
ingress:
  enabled: true
  hosts:
    - host: thumbor.studio.abode.tailandtraillabs.org

# Resource limits
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
```

### Environment Variables

Thumbor can be configured via environment variables in `values.yaml`:

- `SECURITY_KEY`: Security key for URL signing (change in production)
- `ALLOW_UNSAFE_URL`: Allow unsigned URLs (set to False in production)
- `FILE_LOADER_ROOT_PATH`: Root path for loading images
- `RESULT_STORAGE_FILE_STORAGE_ROOT_PATH`: Path for result storage
- `STORAGE_FILE_STORAGE_ROOT_PATH`: Path for storage

## Upgrading

```bash
helm upgrade thumbor . -n wopr
```

## Uninstalling

```bash
helm uninstall thumbor -n wopr
```

## Accessing the Service

```bash
# Port-forward for local access
kubectl port-forward svc/thumbor 8888:8888 -n wopr

# Test healthcheck
curl http://localhost:8888/healthcheck
```

## Usage Examples

```bash
# Resize an image to 300x200
http://thumbor.yourdomain.com/unsafe/300x200/images/your-image.jpg

# Smart crop and resize
http://thumbor.yourdomain.com/unsafe/smart/300x200/images/your-image.jpg

# Apply filters
http://thumbor.yourdomain.com/unsafe/filters:brightness(10)/images/your-image.jpg
```

## Troubleshooting

```bash
# Check pods
kubectl get pods -n wopr

# Check logs
kubectl logs -n wopr deployment/thumbor

# Describe pod
kubectl describe pod -n wopr -l app.kubernetes.io/name=thumbor
```

## Architecture

```
Internet → Ingress (TLS) → Service → Deployment (Thumbor)
                                          ↓
                                     NFS Volume (Images)
```

## Security Considerations

1. **Change SECURITY_KEY in production**: Update the `SECURITY_KEY` environment variable
2. **Disable ALLOW_UNSAFE_URL in production**: Set to `False` for URL signing enforcement
3. **Configure resource limits**: Adjust CPU/memory based on workload
4. **Use signed URLs**: Implement URL signing for production deployments

## References

- [Thumbor Documentation](https://thumbor.readthedocs.io/)
- [MinimalCompact Thumbor Image](https://github.com/MinimalCompact/thumbor)
- [Thumbor GitHub](https://github.com/thumbor/thumbor)
