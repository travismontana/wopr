#!/bin/bash
# Quick install script for Strapi 5 Helm Chart

set -e

NAMESPACE=${1:-strapi}
RELEASE_NAME=${2:-strapi}

echo "Installing Strapi 5 to namespace: $NAMESPACE"
echo "Release name: $RELEASE_NAME"

# Create namespace if it doesn't exist
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Check if values-prod.yaml exists
if [ ! -f "values-prod.yaml" ]; then
    echo "ERROR: values-prod.yaml not found!"
    echo "Copy values-prod.example.yaml to values-prod.yaml and customize it."
    echo "  cp values-prod.example.yaml values-prod.yaml"
    echo ""
    echo "Generate secrets with:"
    echo "  openssl rand -base64 32"
    exit 1
fi

# Check for CHANGE-ME values
if grep -q "CHANGE-ME\|REPLACE-WITH" values-prod.yaml; then
    echo "WARNING: Default/placeholder secrets found in values-prod.yaml"
    echo "Generate secure secrets with: openssl rand -base64 32"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install/upgrade the chart
echo "Installing/upgrading Strapi..."
helm upgrade --install $RELEASE_NAME . \
    --namespace $NAMESPACE \
    --values values-prod.yaml \
    --wait \
    --timeout 5m

echo ""
echo "Strapi installation complete!"
echo ""
echo "Check status:"
echo "  kubectl get pods -n $NAMESPACE"
echo ""
echo "View logs:"
echo "  kubectl logs -f -n $NAMESPACE deployment/$RELEASE_NAME"
echo ""
echo "Access admin (if ingress enabled):"
echo "  Check values-prod.yaml for your configured hostname"
echo "  Navigate to: https://your-hostname/admin"
