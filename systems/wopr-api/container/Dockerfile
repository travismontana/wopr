# buildplease6
FROM python:3.12-slim
LABEL maintainer="Bob Bomar"
LABEL description="WOPR API - Wargaming Oversight & Position Recognition API Service"

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    libpq-dev \
    git \
    && pip install --upgrade pip setuptools wheel \
    && apt clean \
    && apt autoclean \
    && rm -rf /var/lib/apt/lists/* 

RUN useradd -m wopr && \
    mkdir -p /app /var/log/wopr && \
    chown -R wopr:wopr /app /var/log/wopr

RUN touch /var/log/wopr-api.log
RUN chown wopr:wopr /var/log/wopr-api.log

USER wopr

WORKDIR /app

COPY --chown=wopr:wopr requirements.txt .
RUN pip install --user -r requirements.txt

COPY --chown=wopr:wopr app/ ./app/


ENV OTEL_SERVICE_NAME=wopr-api

EXPOSE 8000

CMD ["/home/wopr/.local/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]