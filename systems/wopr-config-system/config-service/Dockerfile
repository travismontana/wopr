# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim
RUN useradd -m -u 1000 wopr
USER 1000:1000
WORKDIR /app

# Ensure pip-installed scripts are in PATH

COPY --from=builder /install /usr/local
COPY --chown=1000:1000 app.py .
EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]