#!/bin/sh
set -eu

if [ -n "${STARTTRACE:-}" ]; then
  echo "[entrypoint] tracing enabled"

  # install at runtime (only if you REALLY want runtime installs)
  pip install --no-cache-dir --user opentelemetry-distro opentelemetry-exporter-otlp || { echo "pip install failed"; exit 1; }
  /home/wopr/.local/bin/opentelemetry-bootstrap -a install || { echo "opentelemetry-bootstrap install failed"; exit 1; }

  exec /home/wopr/.local/bin/opentelemetry-instrument python /app/app.py
else
  echo "[entrypoint] tracing disabled"
  exec python /app/app.py
fi

exit 0
