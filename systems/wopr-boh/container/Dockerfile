# syntax=docker/dockerfile:1

FROM python:3.14-slim

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
COPY requirements.txt pyproject.toml ./
RUN pip install -r requirements.txt && pip install -e .

# Copy app code to /app (back_of_house/ will be at /app/back_of_house/)
COPY --chown=wopr:wopr app/back_of_house/ ./
COPY --chown=wopr:wopr app/back_of_house/back_of_house/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
# Switch to non-root user
USER wopr

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
# Module path: back_of_house.wsgi (because /app is in PYTHONPATH)
#CMD ["python", "manage.py", "migrate", "--noinput"]
#CMD ["python", "manage.py", "collectstatic", "--noinput"]
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "back_of_house.wsgi:application"]
