#!/bin/sh
set -eu

: "${WOPR_API_SERVICE_HOST:?missing WOPR_API_SERVICE_HOST}"
: "${WOPR_API_SERVICE_PORT:?missing WOPR_API_SERVICE_PORT}"

# Render template -> actual nginx conf
envsubst '$WOPR_API_SERVICE_HOST $WOPR_API_SERVICE_PORT' \
  < /etc/nginx/templates/default.conf.template \
  > /etc/nginx/conf.d/default.conf

# Optional: quick visibility
echo "[entrypoint] nginx upstream -> ${WOPR_API_SERVICE_HOST}:${WOPR_API_SERVICE_PORT}"

exec "$@"
