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
ENV OTEL_TRACES_EXPORTER=console,otlp 
ENV OTEL_METRICS_EXPORTER=console,otlp
ENV OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
ENV OTEL_EXPORTER_OTLP_ENDPOINT=https://otel.monitoring.abode.tailandtraillabs.org
ENV OTEL_PYTHON_EXCLUDED_URLS="(/health|/metrics)$"

CMD ["/home/wopr/.local/bin/opentelemetry-instrument", "python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
