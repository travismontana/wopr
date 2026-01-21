

# WOPR Component Diagram - wopr-api Service

This diagram shows the internal components of the wopr-api service.

```mermaid
C4Component
    title Component Diagram - wopr-api Service

    Container_Boundary(api, "wopr-api Container") {
        Component(main, "main. py", "FastAPI App", "Application entry point with lifespan management")
        Component(globals, "globals.py", "Config Module", "Global configuration and environment variables")
        Component(routes_cameras, "api/v1/cameras. py", "Router", "Camera endpoints")
        Component(routes_config, "api/v1/config.py", "Router", "Config management endpoints")
        Component(routes_mlimages, "api/v1/mlimages.py", "Router", "ML image metadata CRUD")
        Component(routes_games, "api/v1/games.py", "Router", "Game session management")
        Component(routes_pieces, "api/v1/pieces.py", "Router", "Game piece management")
        Component(logging_mod, "logging.py", "Logging Module", "Structured logging setup")
        Component(wopr_core, "wopr-core", "Shared Library", "Config, storage, tracing utilities")
    }
    
    ContainerDb(db, "PostgreSQL", "Database")
    ContainerDb(configdb, "Config DB", "PostgreSQL")
    Container_Ext(cam_svc, "wopr-cam", "Camera Service")
    Container_Ext(otel, "OpenTelemetry", "Tracing")
    
    Rel(main, routes_cameras, "Includes router", "FastAPI")
    Rel(main, routes_config, "Includes router", "FastAPI")
    Rel(main, routes_mlimages, "Includes router", "FastAPI")
    Rel(main, routes_games, "Includes router", "FastAPI")
    Rel(main, routes_pieces, "Includes router", "FastAPI")
    Rel(main, logging_mod, "Uses", "Python import")
    Rel(main, globals, "Uses", "Python import")
    Rel(globals, wopr_core, "Fetches config", "HTTP")
    Rel(routes_cameras, cam_svc, "Triggers capture", "httpx")
    Rel(routes_mlimages, db, "CRUD operations", "psycopg3")
    Rel(routes_games, db, "CRUD operations", "psycopg3")
    Rel(routes_pieces, db, "CRUD operations", "psycopg3")
    Rel(routes_config, configdb, "Reads config", "psycopg3")
    Rel(main, otel, "Exports traces", "OTLP HTTP")
    
    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

# Key Components
main.py: FastAPI app with OpenTelemetry instrumentation, CORS middleware, lifespan events
API Routers: RESTful endpoints for cameras, games, pieces, ML images, config
wopr-core Library: Shared Python module for config (wopr. config), storage (wopr.storage), logging (wopr.logging), tracing (wopr.tracing)
Database Connections: psycopg3 connections with context managers for PostgreSQL access