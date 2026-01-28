# syntax=docker/dockerfile:1

FROM python:3.14-slim

# Avoid .pyc, keep logs unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \


WORKDIR /app

# System deps (keep minimal). Add build tools ONLY if you hit wheels/build issues.
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
      git \
      netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install python deps first for better layer caching
COPY requirements.txt .
COPY pyproject.toml .
RUN python -m pip install --upgrade pip \
 && pip install -e . && pip install -r requirements.txt

# Copy the rest of the app
COPY app/ ./app/

EXPOSE 8000

# Optional: basic container healthcheck (assumes Streamlit is responding)
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8000/ || exit 1
# Run Streamlit

CMD ["gunicorn", "app:boh", "--host", "0.0.0.0", "--port", "8000"]