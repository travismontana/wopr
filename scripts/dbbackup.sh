#!/bin/bash
# CNPG Database Dump Script
# Dumps all databases from wopr-db-cluster to compressed SQL files

set -euo pipefail

# Configuration
NAMESPACE="wopr"
CLUSTER="wopr-db-cluster"
BACKUP_DIR="$HOME/local/wopr/backups"
DATE=$(date +%Y-%m-%d_%H%M%S)

# Databases to dump
DATABASES=(
  "wopr-config-db-database"
  "wopr-db-database"
  "wopr-labelstudio-db-database"
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting PostgreSQL backup for cluster: ${CLUSTER}${NC}"

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Get primary pod
echo "Locating primary pod..."
PRIMARY_POD=$(kubectl get pod -n "$NAMESPACE" \
  -l "cnpg.io/cluster=${CLUSTER},role=primary" \
  -o jsonpath='{.items[0].metadata.name}')

if [ -z "$PRIMARY_POD" ]; then
  echo -e "${RED}Error: Could not find primary pod${NC}"
  exit 1
fi
echo -e "Primary pod: ${YELLOW}${PRIMARY_POD}${NC}"

# Get superuser credentials
echo "Extracting credentials..."
PGUSER=$(kubectl get secret -n "$NAMESPACE" "${CLUSTER}-superuser" \
  -o jsonpath='{.data.username}' | base64 -d)
PGPASSWORD=$(kubectl get secret -n "$NAMESPACE" "${CLUSTER}-superuser" \
  -o jsonpath='{.data.password}' | base64 -d)

# Dump each database
for DB in "${DATABASES[@]}"; do
  OUTPUT_FILE="${BACKUP_DIR}/${DB}-${DATE}.sql.gz"
  echo -e "\n${GREEN}Dumping ${YELLOW}${DB}${GREEN}...${NC}"
  
  kubectl exec -n "$NAMESPACE" "$PRIMARY_POD" -- \
    env PGPASSWORD="$PGPASSWORD" \
    pg_dump -U "$PGUSER" -d "$DB" \
      --clean \
      --if-exists \
      --create \
      --verbose 2>&1 | gzip > "$OUTPUT_FILE"
  
  SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
  echo -e "${GREEN}✓ Saved: ${YELLOW}${OUTPUT_FILE}${GREEN} (${SIZE})${NC}"
done

echo -e "\n${GREEN}Backup complete!${NC}"
echo -e "Files saved in: ${YELLOW}${BACKUP_DIR}${NC}"
ls -lh "$BACKUP_DIR"/*-${DATE}.sql.gz
