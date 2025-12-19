#!/bin/sh
set -eu

if [ -n "${STARTTRACE:-}" ]; then
  echo "[entrypoint] tracing enabled"
  exec /home/wopr/.local/bin/opentelemetry-instrument python /app/app.py
else
  echo "[entrypoint] tracing disabled"
  exec python /app/app.py
fi

exit 0
