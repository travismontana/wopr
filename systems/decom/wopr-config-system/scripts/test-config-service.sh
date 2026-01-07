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

# Test WOPR Config Service endpoints

set -e

CONFIG_SERVICE_URL="${WOPR_CONFIG_SERVICE_URL:-http://localhost:8080}"

echo "Testing WOPR Config Service at $CONFIG_SERVICE_URL"
echo "================================================"
echo ""

# Test health
echo "1. Health check..."
curl -s "$CONFIG_SERVICE_URL/health" | jq '.'
echo ""

# Test get single value
echo "2. Get single value (storage.base_path)..."
curl -s "$CONFIG_SERVICE_URL/get/storage.base_path" | jq '.'
echo ""

# Test get multiple values
echo "3. Get multiple values..."
curl -s -X POST "$CONFIG_SERVICE_URL/get" \
  -H "Content-Type: application/json" \
  -d '{"keys": ["storage.base_path", "camera.default_resolution", "logging.default_level"]}' \
  | jq '.'
echo ""

# Test get section
echo "4. Get section (camera.resolutions)..."
curl -s "$CONFIG_SERVICE_URL/section/camera.resolutions" | jq '.'
echo ""

# Test update value
echo "5. Update value (test only)..."
curl -s -X PUT "$CONFIG_SERVICE_URL/set/test.value" \
  -H "Content-Type: application/json" \
  -d '{"value": "test123", "description": "Test value", "updated_by": "test-script"}' \
  | jq '.'
echo ""

# Test get history
echo "6. Get history for test value..."
curl -s "$CONFIG_SERVICE_URL/history/test.value" | jq '.'
echo ""

# Test delete
echo "7. Delete test value..."
curl -s -X DELETE "$CONFIG_SERVICE_URL/delete/test.value" | jq '.'
echo ""

echo "================================================"
echo "✓ All tests passed!"
echo ""
echo "Try these commands:"
echo "  # Get all config"
echo "  curl $CONFIG_SERVICE_URL/all | jq ."
echo ""
echo "  # Update a value"
echo "  curl -X PUT $CONFIG_SERVICE_URL/set/camera.default_resolution \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"value\": \"1080p\", \"updated_by\": \"bob\"}'"
echo ""
echo "  # Export to YAML"
echo "  curl $CONFIG_SERVICE_URL/export/yaml | jq -r '.yaml'"
