# WOPR API Application Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            WOPR API Application                          │
│                         (FastAPI - Port 8000)                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
            ┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────────┐
            │   Root API   │ │  Cameras   │ │    Config      │
            │      /       │ │  /api/v1/  │ │   /api/v1/     │
            │              │ │  cameras   │ │   config       │
            └──────────────┘ └────┬───────┘ └────┬───────────┘
                                  │              │
                                  │              │
     ┌────────────────────────────┴──────┐       │
     │  Camera Endpoints:                 │       │
     │  • GET /    (list all cameras)    │       │
     │  • GET /{id} (get camera)         │       │
     │  • POST /capture (capture image)  │       │
     └───────────────┬───────────────────┘       │
                     │                            │
                     │                    ┌───────▼──────────────┐
                     │                    │  Config Endpoints:    │
                     │                    │  • Database-backed    │
                     │                    │    config service     │
                     │                    │  • PostgreSQL DB      │
                     │                    └───────┬───────────────┘
                     │                            │
                     │                            │
     ┌───────────────▼────────────────┐  ┌───────▼────────────┐
     │  External Camera Service       │  │  PostgreSQL DB      │
     │  wopr-cam.hangar.bpfx.org:5000│  │  config-db:5432     │
     │  • /capture                    │  │  Database:  config_db│
     │  • /capture_ml                 │  │  User: wopr         │
     └────────────────────────────────┘  └─────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         Cross-Cutting Concerns                           │
├─────────────────────────────────────────────────────────────────────────┤
│  • CORS Middleware (allow all origins)                                  │
│  • OpenTelemetry Tracing (optional, configurable)                       │
│    - OTLP HTTP Exporter                                                 │
│    - Captures request/response headers & payloads                       │
│  • Logging (wopr. logging module)                                        │
│  • Configuration Service (wopr-config via CONFIG_SERVICE_URL)           │
│  • Storage Layer (wopr.storage module)                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. FastAPI Application (`main.py`)
- Entry point for the API
- Configures middleware, CORS, and tracing
- Manages application lifecycle events (startup/shutdown)
- Exposes OpenAPI documentation at `/docs` and `/redoc`
- Implements conditional distributed tracing

### 2. API Routes (`app/api/v1/`)

#### Cameras API (`cameras.py`)
- **Purpose**: Manages camera operations and image capture
- **Endpoints**:
  - `GET /api/v1/cameras` - List all cameras
  - `GET /api/v1/cameras/{camera_id}` - Get specific camera
  - `POST /api/v1/cameras/capture` - Trigger image capture
- **External Integration**:  Communicates with physical camera service via HTTP

#### Config API (`config.py`)
- **Purpose**: Database-backed configuration management service
- **Features**:
  - Dynamic configuration storage
  - Type-safe value parsing (string, int, float, boolean, list, dict)
  - Environment-based configuration isolation
  - PostgreSQL persistent storage

### 3. Global Configuration (`globals.py`)
- Application metadata (name, version, author)
- Service configuration (host, port)
- External service URLs
- Environment variable handling

## External Dependencies

| Service | Endpoint | Purpose |
|---------|----------|---------|
| **Camera Service** | `wopr-cam.hangar.bpfx.org:5000` | Physical camera control and image capture |
| **PostgreSQL** | `config-db:5432` | Persistent configuration storage |
| **Config Service** | `wopr-config.studio.abode...` | Central configuration server |
| **Tracing Backend** | Configurable OTLP endpoint | Distributed tracing collection |

## Key Dependencies

- **FastAPI** - Modern web framework for building APIs
- **Uvicorn** - ASGI server for running the application
- **OpenTelemetry** - Distributed tracing and observability
- **httpx** - Async HTTP client for camera communication
- **psycopg3** - PostgreSQL database adapter
- **Pydantic** - Data validation and settings management
- **WOPR Modules** - Shared libraries (config, storage, logging, tracing)

## Configuration Sources

### Environment Variables
```bash
SERVICE_NAME=wopr-api
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8000
CONFIG_SERVICE_URL=http://wopr-config.studio.abode. tailandtraillabs.org
DATABASE_URL=postgresql://wopr:wopr@config-db:5432/config_db
WOPR_ENVIRONMENT=default
```

### Dynamic Configuration
Retrieved from the config service at runtime: 
- `tracing.enabled` (boolean) - Enable/disable distributed tracing
- `tracing.host` (string) - OTLP tracing endpoint

## Cross-Cutting Concerns

### CORS Middleware
- Allows all origins (`*`)
- Supports all methods and headers
- Credentials enabled

### OpenTelemetry Tracing
- **Conditional**:  Only active when `tracing.enabled=true`
- **Captures**:
  - Request headers (accept, content-type, user-agent, etc.)
  - Response headers (content-type, content-length, cache-control)
  - Request/response payloads
- **Exporter**: OTLP HTTP format
- **Instrumentation**: FastAPI auto-instrumentation + custom middleware

### Logging
- Structured logging via `wopr.logging` module
- Application-wide logger with service name
- Logs lifecycle events, API calls, and errors

### Storage Layer
- Abstracted via `wopr.storage` module
- Used for persistent data operations

## Architecture Pattern

This is a **microservices-oriented architecture** where: 

- **WOPR API** acts as an API gateway
- **Camera Service** handles hardware interaction
- **Config Service** provides centralized configuration
- **PostgreSQL** provides persistent storage for configuration
- **Tracing Backend** provides observability

The application follows **clean architecture principles** with:
- Separation of concerns (API routes, business logic, configuration)
- Dependency injection (config, logging, storage modules)
- External service abstraction (httpx client for cameras)
- Environment-based configuration

## API Documentation

The API automatically generates interactive documentation: 
- **Swagger UI**:  `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

## Application Metadata

- **Name**: WOPR API
- **Version**: 0.1.3-beta
- **Description**: Wargaming Oversight & Position Recognition
- **Author**: Bob Bomar
- **Domain**: studio.abode.tailandtraillabs.org