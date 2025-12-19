#!/bin/sh
set -eu

if [ -n "${STARTTRACE:-}" ]; then
  echo "[entrypoint] tracing enabled"
  pip install --no-cache-dir --user opencv-python-headless \
    opencv-python-headless \
    opentelemetry-api \
    opentelemetry-sdk \
    opentelemetry-exporter-otlp \
    opentelemetry-instrumentation \
    opentelemetry-instrumentation-wsgi \
    opentelemetry-instrumentation-flask 
  ls -ln /dev/video0
  stat -c "mode=%a uid=%u gid=%g %n" /dev/video0
  exec /home/wopr/.local/bin/opentelemetry-instrument python /app/app.py
else
  echo "[entrypoint] tracing disabled"
  exec python /app/app.py
fi

exit 0
