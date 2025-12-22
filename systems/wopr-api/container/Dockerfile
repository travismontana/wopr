FROM python:3.14-slim
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
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 2222 -d /app wopr && \
    mkdir -p /app /var/log/wopr && \
    chown -R wopr:wopr /app /var/log/wopr

WORKDIR /app

COPY --chown=wopr:wopr requirements.txt .
RUN pip install --user -r requirements.txt

COPY --chown=wopr:wopr app/ /app

USER wopr

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]