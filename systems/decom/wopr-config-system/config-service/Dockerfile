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

# Build stage
# Use official Python image as base
FROM python:3.13-slim as builder
RUN apt-get update \
&& apt-get install -y --no-install-recommends netcat-openbsd \
&& rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 wopr
USER 1000:1000
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --user \
    opentelemetry-distro \
    opentelemetry-exporter-otlp

# Run bootstrap to auto-install instrumentations
RUN /home/wopr/.local/bin/opentelemetry-bootstrap -a install

COPY --chown=1000:1000 app.py .
EXPOSE 8080

ENV OTEL_SERVICE_NAME=wopr-config-service 
ENV OTEL_TRACES_EXPORTER=otlp 
ENV OTEL_METRICS_EXPORTER=otlp
ENV OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
ENV OTEL_EXPORTER_OTLP_ENDPOINT=https://otel.monitoring.abode.tailandtraillabs.org
ENV OTEL_PYTHON_EXCLUDED_URLS="(/health|/metrics)$"

CMD ["/home/wopr/.local/bin/opentelemetry-instrument", "python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
