# syntax=docker/dockerfile:1

FROM python:3.14-slim

# Avoid .pyc, keep logs unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

WORKDIR /app

# System deps (keep minimal). Add build tools ONLY if you hit wheels/build issues.
RUN apt-get update && apt-get install -y --no-install-recommends \
      curl \
    && rm -rf /var/lib/apt/lists/*

# Install python deps first for better layer caching
COPY requirements.txt .
COPY pyproject.toml .
RUN python -m pip install --upgrade pip \
 && pip install -e . && pip install -r requirements.txt

# Copy the rest of the app
COPY app/ ./app/

EXPOSE 8501

# Optional: basic container healthcheck (assumes Streamlit is responding)
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD curl -fsS http://127.0.0.1:8501/_stcore/health || exit 1

# Run Streamlit

CMD ["streamlit", "run", "back_of_house.py", "--server.port=8501", "--server.address=0.0.0.0"]