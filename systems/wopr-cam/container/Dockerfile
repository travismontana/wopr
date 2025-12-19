# Build stage
# Use official Python image as base
FROM python:3.13-slim as builder
ARG DOTRACE
RUN apt-get update \
&& apt-get install -y --no-install-recommends netcat-openbsd \
&& rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 wopr
USER 1000:1000
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


RUN if [ -n "${STARTTRACE}" ]; then
      pip install --no-cache-dir --user \
      opentelemetry-distro \
      opentelemetry-exporter-otlp && \
      /home/wopr/.local/bin/opentelemetry-bootstrap -a install && \
      STARTCMD="/home/wopr/.local/bin/opentelemetry-instrument python ./app.py"; \
    else \
      STARTCMD="python ./app.py"; \
    fi

COPY --chown=1000:1000 app.py .
EXPOSE 8080

#ENV STARTTRACE=${DOTRACE:+/home/wopr/.local/bin/opentelemetry-instrument}
CMD [${STARTCMD}]]
