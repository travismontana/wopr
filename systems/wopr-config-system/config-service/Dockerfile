# Build stage
# Use official Python image as base
FROM python:3.13-slim as builder
RUN useradd -m -u 1000 wopr
USER 1000:1000
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=1000:1000 app.py .
EXPOSE 8080

ENV OTEL_SERVICE_NAME=wopr-config_service 
ENV OTEL_TRACES_EXPORTER=console,otlp 
ENV OTEL_METRICS_EXPORTER=console,otlp
ENV OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=http://tempo.monitoring.abode.tailandtraillabs.org/v1/traces
ENV OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
ENV OTEL_EXPORTER_OTLP_METRICS_ENDPOINT=http://prometheus.monitoring.abode.tailandtraillabs.org/api/v1/otlp/v1/metrics

CMD ["opentelemetry-bootstrap", "-a", "install"]
CMD ["opentelemetry-instrument", "python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
