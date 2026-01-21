#!/usr/bin/env python3

import logging
import sys
import json
import os
import asyncpg
import base64
from contextlib import nullcontext
from typing import List

from app import globals as woprvar
from app.logging import configure_logging
from . import logger

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from starlette.requests import Request
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.trace import Status, StatusCode
from opentelemetry.baggage import set_baggage, get_baggage
from opentelemetry.trace import Link
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.instrumentation.logging import LoggingInstrumentor

from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

# Import all API routers
from app.api.v2 import config
from app.api.v2 import games
from app.api.v2 import pieces
from app.api.v2 import mlimages
from app.api.v2 import images
from app.api.v2 import notifications
from app.api.v2 import stream
from app.api.v2 import session
from app.api.v2 import vision
from app.api.v2 import players
from app.api.v2 import plays
from app.api.v2 import tasks
from app.api.v2 import models
from app.api.v2 import model_family

from app.celery_app import celery_app

# -------------------------
# Application Initialization
# -------------------------

# Configure logging first
logger = configure_logging("/var/log/wopr-api.log")
logger.info("WOPR API application: booting up...")
logger.debug(f"WOPR API globals: {woprvar.WOPR_CONFIG}")

# -------------------------
# Tracing Configuration
# -------------------------

# Define header capture lists (used by middleware)
CAPTURE_REQUEST_HEADERS = [
    "accept", "accept-language", "accept-encoding",
    "content-type", "referer", "user-agent"
]

CAPTURE_RESPONSE_HEADERS = [
    "content-type", "content-length", "cache-control"
]

# Determine if tracing is enabled
tracing_enabled = True
logger.info(f"Tracing enabled: {tracing_enabled}")

# Initialize tracer as None (will be set if tracing enabled)
tracer = None

# -------------------------
# FastAPI Application Setup
# -------------------------

async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("WOPR API starting up...")
    yield
    # Shutdown
    logger.info("WOPR API shutting down...")

app = FastAPI(
    title=woprvar.APP_TITLE,
    description=woprvar.APP_DESCRIPTION,
    version=woprvar.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": woprvar.APP_AUTHOR,
        "email": woprvar.APP_AUTHOR_EMAIL,
    },
)
logger.info("FastAPI application created")

# -------------------------
# OpenTelemetry Tracing Setup
# -------------------------

if tracing_enabled:
    logger.info("Initializing OpenTelemetry tracing...")
    
    tracing_endpoint = woprvar.APP_OTEL_URL + "/v1/traces"
    logger.debug(f"Tracing endpoint: {tracing_endpoint}")
    
    tracer = woprvar.create_tracer(
        tracer_name=woprvar.APP_NAME,
        tracer_version=woprvar.APP_VERSION,
        tracer_enabled=tracing_enabled,
        tracer_endpoint=tracing_endpoint,
        service_namespace="wopr",
        deployment_env=os.getenv("DEPLOYMENT_ENV", "production")
    )
    
    if tracer:
        logger.info(f"Tracing enabled. Exporting to {tracing_endpoint}")
        
        # Instrument asyncpg (database calls)
        AsyncPGInstrumentor().instrument()
        logger.info("AsyncPG instrumentation enabled")
        
        # Instrument httpx (HTTP client calls)
        HTTPXClientInstrumentor().instrument()
        logger.info("HTTPX instrumentation enabled")
        
        # Instrument logging (adds trace_id/span_id to logs)
        LoggingInstrumentor().instrument(set_logging_format=True)
        logger.info("Logging instrumentation enabled")
        
        # Define request hook for capturing headers in spans
        def request_hook(span, scope):
            """Capture request headers in trace spans"""
            if span and span.is_recording():
                headers = dict(scope.get("headers", []))
                for key, value in headers.items():
                    key_str = key.decode() if isinstance(key, bytes) else key
                    if key_str.lower() in CAPTURE_REQUEST_HEADERS:
                        val_str = value.decode() if isinstance(value, bytes) else value
                        span.set_attribute(f"http.request.header.{key_str}", val_str)
        
        # Instrument the FastAPI app
        FastAPIInstrumentor.instrument_app(app, server_request_hook=request_hook)
        logger.info("FastAPI instrumentation enabled")
        
    else:
        logger.warning("Tracing is enabled but failed to initialize tracer")
        tracer = None
else:
    logger.info("Tracing is disabled")
    tracer = None

# -------------------------
# Router Registration
# -------------------------

logger.info("Registering API routers...")

app.include_router(config.router, prefix="/api/v2/config", tags=["config"])
app.include_router(games.router, prefix="/api/v2/games", tags=["games"])
app.include_router(pieces.router, prefix="/api/v2/pieces", tags=["pieces"])
app.include_router(mlimages.router, prefix="/api/v2/mlimages", tags=["mlimages"])
app.include_router(images.router, prefix="/api/v2/images", tags=["images"])
app.include_router(notifications.router, prefix="/api/v2/notifications", tags=["notifications"])
app.include_router(stream.router, prefix="/api/v2/stream", tags=["stream"])
app.include_router(session.router, prefix="/api/v2/session", tags=["session"])
app.include_router(session.router, prefix="/api/v2/sessions", tags=["session"])
app.include_router(vision.router, prefix="/api/v2/vision", tags=["vision"])
app.include_router(players.router, prefix="/api/v2/players", tags=["players"])
app.include_router(plays.router, prefix="/api/v2/plays", tags=["plays"])
app.include_router(tasks.router, prefix="/api/v2/tasks", tags=["tasks"])
app.include_router(models.models_router, prefix="/api/v2/models", tags=["models"])
app.include_router(model_family.model_family_router, prefix="/api/v2/model_family", tags=["model_family"])

logger.info("All API routers registered successfully")

# -------------------------
# Middleware
# -------------------------

@app.middleware("http")
async def capture_headers_and_payloads(request, call_next):
    """
    Middleware to capture request/response headers and bodies in trace spans.
    Only active when tracing is enabled.
    """
    # Skip tracing capture if tracer not initialized
    if not tracer:
        return await call_next(request)
    
    span = trace.get_current_span()
    logger.debug(f"[MIDDLEWARE] Processing {request.method} {request.url.path}")
    logger.debug(f"[MIDDLEWARE] Span recording: {span.is_recording() if span else False}")
    
    # Read request body
    body = await request.body()
    logger.debug(f"[MIDDLEWARE] Request body length: {len(body)}")
    
    # Capture request body in span
    if span and span.is_recording() and body:
        try:
            body_dict = json.loads(body)
            span.set_attribute("http.request.body", json.dumps(body_dict))
            logger.debug("[MIDDLEWARE] Captured request body as JSON")
        except Exception as e:
            logger.debug(f"[MIDDLEWARE] Request body not JSON: {e}")
            body_str = body.decode()[:1000]
            span.set_attribute("http.request.body", body_str)
    
    # Reconstruct request so FastAPI can still read the body
    async def receive():
        return {"type": "http.request", "body": body}
    
    request = Request(request.scope, receive)
    
    # Process request
    response = await call_next(request)
    logger.debug(f"[MIDDLEWARE] Response status: {response.status_code}")
    
    # Capture response headers and body in span
    if span and span.is_recording():
        logger.debug("[MIDDLEWARE] Capturing response data")
        span.set_attribute("middleware.request.method", request.method)
        span.set_attribute("middleware.request.path", request.url.path)
        
        # Capture response headers
        for key in CAPTURE_RESPONSE_HEADERS:
            if key in response.headers:
                span.set_attribute(f"http.response.header.{key}", response.headers[key])
        
        # Capture response body
        response_body = b""
        try:
            async for chunk in response.body_iterator:
                response_body += chunk
            logger.debug(f"[MIDDLEWARE] Captured response body length: {len(response_body)}")
        except Exception as e:
            logger.error(f"[MIDDLEWARE] Failed to read response body: {e}")
            return response
        
        # Store response body in span (truncate if large)
        if response_body:
            try:
                body_json = json.loads(response_body)
                span.set_attribute("http.response.body", json.dumps(body_json))
                logger.debug("[MIDDLEWARE] Captured response body as JSON")
            except Exception as e:
                logger.debug(f"[MIDDLEWARE] Response not JSON: {e}")
                try:
                    span.set_attribute("http.response.body", response_body.decode()[:1000])
                except UnicodeDecodeError:
                    # Binary response (image, etc.)
                    span.set_attribute("http.response.body", f"<binary data, {len(response_body)} bytes>")
                    logger.debug("[MIDDLEWARE] Response is binary data")
        
        # Reconstruct response with captured body
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )
    
    logger.debug("[MIDDLEWARE] No span recording, returning original response")
    return response

logger.info("Middleware registered")

# -------------------------
# CORS Configuration
# -------------------------

CORS_ORIGINS: List[str] = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured")

# -------------------------
# Root Endpoint
# -------------------------

@app.get("/")
async def root():
    """Root endpoint - returns service information"""
    logger.info("Root endpoint accessed")
    return {
        "service": woprvar.APP_TITLE,
        "version": woprvar.APP_VERSION,
        "status": "operational",
        "docs": "/docs"
    }

# -------------------------
# Application Entry Point
# -------------------------

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting uvicorn server on {woprvar.SERVICE_HOST}:{woprvar.SERVICE_PORT}")
    uvicorn.run(app, host=woprvar.SERVICE_HOST, port=woprvar.SERVICE_PORT)