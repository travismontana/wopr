#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
Copyright (c) 2025 Bob Bomar <bob@bomar.us>
SPDX-License-Identifier: MIT

Main FastAPI application with OpenTelemetry instrumentation.
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

from app.config import settings
from app.database import engine
from app.api.v1 import health, auth, cameras

logger = logging.getLogger(__name__)


def setup_tracing() -> None:
    """Configure OpenTelemetry tracing"""
    if not settings.OTEL_ENABLED:
        logger.info("OpenTelemetry tracing disabled")
        return
    
    # Create resource with service info
    resource = Resource.create({
        "service.name": settings.OTEL_SERVICE_NAME,
        "service.version": "0.1.0",
    })
    
    # Set up tracer provider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    
    # OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=settings.OTEL_ENDPOINT,
        insecure=True
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Auto-instrument SQLAlchemy
    SQLAlchemyInstrumentor().instrument(
        engine=engine,
        enable_commenter=True,
    )
    
    # Auto-instrument Redis
    RedisInstrumentor().instrument()
    
    logger.info(f"OpenTelemetry tracing enabled: {settings.OTEL_ENDPOINT}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("WOPR API starting up...")
    setup_tracing()
    yield
    # Shutdown
    logger.info("WOPR API shutting down...")


# Create FastAPI app
app = FastAPI(
    title="WOPR API",
    description="Wargaming Oversight & Position Recognition - API Layer",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Auto-instrument FastAPI (must be after app creation)
if settings.OTEL_ENABLED:
    FastAPIInstrumentor.instrument_app(app)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["cameras"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "WOPR API",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
