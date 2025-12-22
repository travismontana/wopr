# WOPR API

Copyright (c) 2025 Bob Bomar <bob@bomar.us>  
Licensed under the MIT License - see [LICENSE](../LICENSE) file.

---

## Overview

FastAPI-based API layer for WOPR (Wargaming Oversight & Position Recognition).

- **Port:** 8000
- **Database:** PostgreSQL 16 (wopr_main)
- **Task Queue:** Celery + Redis
- **Tracing:** OpenTelemetry → Tempo/Grafana
- **Config:** wopr-config service
- **Migrations:** Alembic

## Project Structure

```
wopr-api/
├── Dockerfile
├── requirements.txt
├── docker-compose.yml      # Local dev
├── alembic.ini
├── alembic/
│   ├── env.py
│   └── versions/           # Migration files
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI app + OTEL
│   ├── config.py          # Config integration
│   ├── database.py        # SQLAlchemy setup
│   ├── dependencies.py    # Auth, DB session
│   ├── models/            # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── camera.py
│   │   ├── game.py
│   │   └── image.py
│   ├── schemas/           # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── camera.py
│   │   └── common.py
│   ├── api/               # Route handlers
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── health.py
│   │       ├── auth.py
│   │       └── cameras.py
│   ├── services/          # Business logic
│   │   └── auth.py
│   └── tasks/             # Celery tasks
│       └── __init__.py
└── tests/
```

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret for JWT signing
- `REDIS_URL` - Redis broker URL (optional, defaults from config)

Optional:
- `WOPR_CONFIG_SERVICE_URL` - Config service URL (default: http://wopr-config_service.svc:8080)
- `OTEL_EXPORTER_OTLP_ENDPOINT` - OTEL endpoint override

## Quick Start

### Local Development

```bash
# Set environment variables
export DATABASE_URL="postgresql://wopr:wopr@localhost:5432/wopr_main"
export JWT_SECRET_KEY="your-secret-key-change-in-production"
export REDIS_URL="redis://localhost:6379/0"

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Compose

```bash
docker-compose up -d
```

### Kubernetes

```bash
kubectl apply -f k8s/
```

## API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Endpoints

### Health
- `GET /health` - Liveness probe
- `GET /ready` - Readiness probe
- `GET /metrics` - Prometheus metrics

### Auth
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Current user

### Cameras
- `GET /api/v1/cameras` - List cameras
- `POST /api/v1/cameras/{id}/capture` - Trigger capture

## Development

```bash
# Run tests
pytest

# Lint
black app/
ruff app/

# Type check
mypy app/
```

## License

MIT License - see LICENSE file
