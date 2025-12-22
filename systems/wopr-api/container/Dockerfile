# WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025 Bob Bomar <bob@bomar.us>
# SPDX-License-Identifier: MIT

FROM python:3.11-slim

# Metadata
LABEL org.opencontainers.image.title="WOPR API"
LABEL org.opencontainers.image.description="FastAPI service for WOPR game tracking"
LABEL org.opencontainers.image.authors="Bob Bomar <bob@bomar.us>"
LABEL org.opencontainers.image.licenses="MIT"

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    git \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 wopr && \
    mkdir -p /app /var/log/wopr && \
    chown -R wopr:wopr /app /var/log/wopr

WORKDIR /app

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel git+github.com
COPY --chown=wopr:wopr requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY --chown=wopr:wopr app/ ./app/
COPY --chown=wopr:wopr alembic/ ./alembic/
COPY --chown=wopr:wopr alembic.ini .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Switch to app user
USER wopr

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
