# syntax=docker/dockerfile:1

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 

RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    libpq-dev \
    git \
    && pip install --upgrade pip setuptools wheel \
    && apt clean \
    && apt autoclean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 2222 wopr

WORKDIR /app

# Install dependencies as root
COPY pyproject.toml ./
RUN pip install -e .

# Copy app code to /app (wopr_web/ will be at /app/wopr_web/)
COPY --chown=wopr:wopr wopr_web ./
COPY --chown=wopr:wopr wopr_web/scripts/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
RUN mkdir -p /app/staticfiles && chown -R wopr:wopr /app/staticfiles
# Switch to non-root user
USER wopr

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]

