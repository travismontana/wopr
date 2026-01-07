#!/bin/bash
# Copyright 2026 Bob Bomar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -euo pipefail

# Thumbor Test Script
# Usage: ./test.sh [namespace] [release-name]

NAMESPACE="${1:-wopr}"
RELEASE="${2:-thumbor}"

echo "=== Testing Thumbor Deployment ==="
echo "Namespace: $NAMESPACE"
echo "Release: $RELEASE"
echo

# Get pod name
POD=$(kubectl get pod -n "$NAMESPACE" -l "app.kubernetes.io/name=thumbor" -o jsonpath='{.items[0].metadata.name}')
echo "Testing pod: $POD"
echo

# Test 1: Healthcheck
echo "Test 1: Healthcheck endpoint..."
if kubectl exec -n "$NAMESPACE" "$POD" -- curl -s -f http://localhost:8000/healthcheck > /dev/null; then
    echo "✓ Healthcheck OK"
else
    echo "✗ Healthcheck FAILED"
    exit 1
fi

# Test 2: Unsafe URL processing (if enabled)
echo
echo "Test 2: Image processing (unsafe URL)..."
# Test with a simple gradient that Thumbor can generate
TEST_URL="/unsafe/100x100/gradient"
if kubectl exec -n "$NAMESPACE" "$POD" -- curl -s -f "http://localhost:8000$TEST_URL" -o /dev/null; then
    echo "✓ Image processing OK"
else
    echo "⚠ Image processing may be disabled (this is OK if unsafe URLs are disabled)"
fi

# Test 3: Check storage directories
echo
echo "Test 3: Storage directories..."
if kubectl exec -n "$NAMESPACE" "$POD" -- test -d /data/storage; then
    echo "✓ Storage directory exists"
else
    echo "✗ Storage directory missing"
    exit 1
fi

if kubectl exec -n "$NAMESPACE" "$POD" -- test -d /data/result_storage; then
    echo "✓ Result storage directory exists"
else
    echo "✗ Result storage directory missing"
    exit 1
fi

# Test 4: Check PVC
echo
echo "Test 4: Persistent Volume..."
if kubectl get pvc -n "$NAMESPACE" "$RELEASE-thumbor" &> /dev/null; then
    PVC_STATUS=$(kubectl get pvc -n "$NAMESPACE" "$RELEASE-thumbor" -o jsonpath='{.status.phase}')
    if [ "$PVC_STATUS" = "Bound" ]; then
        echo "✓ PVC is bound"
    else
        echo "⚠ PVC status: $PVC_STATUS"
    fi
else
    echo "⚠ No PVC found (persistence may be disabled)"
fi

# Test 5: Check resource usage
echo
echo "Test 5: Resource usage..."
kubectl top pod -n "$NAMESPACE" "$POD" 2>/dev/null || echo "⚠ Metrics server not available"

# Test 6: Service endpoint
echo
echo "Test 6: Service endpoint..."
SERVICE=$(kubectl get svc -n "$NAMESPACE" -l "app.kubernetes.io/name=thumbor" -o jsonpath='{.items[0].metadata.name}')
if [ -n "$SERVICE" ]; then
    echo "✓ Service exists: $SERVICE"
    CLUSTER_IP=$(kubectl get svc -n "$NAMESPACE" "$SERVICE" -o jsonpath='{.spec.clusterIP}')
    echo "  Cluster IP: $CLUSTER_IP:8000"
else
    echo "✗ Service not found"
    exit 1
fi

# Test 7: Ingress
echo
echo "Test 7: Ingress configuration..."
if kubectl get ingress -n "$NAMESPACE" -l "app.kubernetes.io/name=thumbor" &> /dev/null; then
    INGRESS_HOST=$(kubectl get ingress -n "$NAMESPACE" -l "app.kubernetes.io/name=thumbor" -o jsonpath='{.items[0].spec.rules[0].host}')
    echo "✓ Ingress configured: $INGRESS_HOST"
else
    echo "⚠ No ingress found"
fi

echo
echo "=== All Tests Complete ==="
echo
echo "To test from outside the cluster:"
echo "  kubectl port-forward -n $NAMESPACE svc/$SERVICE 8000:8000"
echo "  curl http://localhost:8000/healthcheck"
echo
echo "Example image URL (if unsafe URLs enabled):"
echo "  http://localhost:8000/unsafe/300x200/https://picsum.photos/800/600"
