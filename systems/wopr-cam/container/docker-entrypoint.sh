#!/bin/sh
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

set -eu

# FastAPI app path: "app:app" means /app/app.py contains `app = FastAPI(...)`
APP_MODULE="${APP_MODULE:-app:app}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-5000}"

if [ -n "${STARTTRACE:-}" ]; then
  echo "[entrypoint] tracing enabled"

  # Install runtime deps (as you were doing). You can/should bake these into the image later.
  pip install --no-cache-dir --user \
    opencv-python-headless \
    opentelemetry-distro \
    opentelemetry-exporter-otlp \
    opentelemetry-instrumentation \
    opentelemetry-instrumentation-asgi \
    opentelemetry-instrumentation-fastapi \
    opentelemetry-instrumentation-logging \
    fastapi \
    "uvicorn[standard]" \
    pydantic

  # Optional camera device sanity checks (keep if you're on a host with /dev/video0)
  if [ -e /dev/video0 ]; then
    ls -ln /dev/video0
    stat -c "mode=%a uid=%u gid=%g %n" /dev/video0
  else
    echo "[entrypoint] NOTE: /dev/video0 not found (ok if running without camera device)"
  fi

  # (Optional but handy) ensure distro is bootstrapped.
  # If you already have this done elsewhere, you can remove it.
  #/home/wopr/.local/bin/opentelemetry-bootstrap -a install || true

  # Launch uvicorn under OpenTelemetry auto-instrumentation
  exec /home/wopr/.local/bin/opentelemetry-instrument \
    uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT"

else
  echo "[entrypoint] tracing disabled"
  exec uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT"
fi
