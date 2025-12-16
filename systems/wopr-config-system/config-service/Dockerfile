# Build stage
# Use official Python image as base
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
RUN useradd -m -u 1000 wopr
USER 1000:1000
COPY --chown=1000:1000 app.py .
EXPOSE 8080

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
