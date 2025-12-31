#!/usr/bin/env python3
# main.py
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2023-present Bob <bob@bomar.us>
# See git log for detailed authorship

WOPR API main application.
"""

import logging
import sys
import json
import os
import asyncpg
import base64
from contextlib import nullcontext
from typing import List

from wopr import config as woprconfig
from wopr import storage as woprstorage
from wopr import logging as woprlogging
from wopr import tracing as woprtracing
from app import globals as woprvar

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
from app.api.v1 import cameras
from app.api.v1 import config
from app.api.v1 import status
from app.api.v1 import health
from app.api.v1 import games
from app.api.v1 import pieces
from app.api.v1 import mlimages

woprconfig.init_config(service_url=os.getenv("APP_API_URL") or woprvar.APP_API_URL)

# Set normal logging not using woprlogg.
logger = logging.getLogger(woprvar.APP_NAME)
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logger.info("WOPR API application: booting up...")

# Determine if tracing is enabled
tracing_enabled = woprconfig.get_bool("tracing.enable", True)
if os.getenv("TRACING_ENABLE") is not None or tracing_enabled:
    logger.debug(f"Tracing is enabled tracing_enabled: ({tracing_enabled}).")
else:
    logger.debug(f"Tracing is disabled; tracing_enabled: ({tracing_enabled}).")

# Initialize tracer early so it's available in lifespan
tracer = None

async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("WOPR API starting up...")
    with tracer.start_as_current_span("app_startup") if tracer else nullcontext():
        logger.info("Yielding into application...")
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

if tracing_enabled:
    CAPTURE_REQUEST_HEADERS = [
        "accept", "accept-language", "accept-encoding",
        "content-type", "referer", "user-agent"
    ]

    CAPTURE_RESPONSE_HEADERS = [
        "content-type", "content-length", "cache-control"
    ]
    
    tracing_endpoint = woprvar.APP_OTEL_URL + "/v1/traces"
    tracer = woprtracing.create_tracer(
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
        
    else:
        logger.warning("Tracing is enabled but failed to initialize tracer.")

    def request_hook(span, scope):
        if span and span.is_recording():
            headers = dict(scope.get("headers", []))
            for key, value in headers.items():
                key_str = key.decode() if isinstance(key, bytes) else key
                if key_str.lower() in CAPTURE_REQUEST_HEADERS:
                    val_str = value.decode() if isinstance(value, bytes) else value
                    span.set_attribute(f"http.request.header.{key_str}", val_str)
    
    FastAPIInstrumentor.instrument_app(app, server_request_hook=request_hook)
    app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["cameras"])
    app.include_router(config.router, prefix="/api/v1/config", tags=["config"])
    app.include_router(status.router, prefix="/api/v1/status", tags=["status"])
    app.include_router(health.router, prefix="/api/v1/health", tags=["health"])
    app.include_router(games.router, prefix="/api/v1/games", tags=["games"])
    app.include_router(pieces.router, prefix="/api/v1/pieces", tags=["pieces"])
    app.include_router(mlimages.router, prefix="/api/v1/mlimages", tags=["mlimages"])
    @app.middleware("http")
    async def capture_headers_and_payloads(request, call_next):
        span = trace.get_current_span()
        
        # Read request body
        body = await request.body()
        
        # Capture request body in span
        if span and span.is_recording() and body:
            try:
                body_dict = json.loads(body)
                span.set_attribute("http.request.body", json.dumps(body_dict))
            except:
                # Not JSON or parse failed - store as string (truncate if huge)
                body_str = body.decode()[:1000]
                span.set_attribute("http.request.body", body_str)
        
        # Reconstruct request so FastAPI can still read the body
        async def receive():
            return {"type": "http.request", "body": body}
        
        request = Request(request.scope, receive)
        
        # Process request
        response = await call_next(request)
        
        # Capture response headers
        if span and span.is_recording():
            for key in CAPTURE_RESPONSE_HEADERS:
                if key in response.headers:
                    span.set_attribute(f"http.response.header.{key}", response.headers[key])
        
        return response  # <-- CRITICAL: Was missing!

else:
    tracer = None
    logger.info("Tracing is disabled.")

# CORS
CORS_ORIGINS: List[str] = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    with tracer.start_as_current_span("root_endpoint") if tracer else nullcontext():
        logger.info("Root endpoint accessed")
        return {
            "service": woprvar.APP_TITLE,
            "version": woprvar.APP_VERSION,
            "status": "operational",
            "docs": "/docs"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=woprvar.SERVICE_HOST, port=woprvar.SERVICE_PORT)