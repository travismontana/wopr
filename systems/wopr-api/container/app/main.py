#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2023-present Bob <bob@bomar.us>
# See git log for detailed authorship

WOPR API main application.
"""

import logging

from wopr import config as woprconfig
from wopr import storage as woprstorage
from wopr import logging as woprlogging
from wopr import tracing as woprtracing
from app import globals as woprvar

# Initialize config client at startup
woprconfig.init_config(service_url=woprvar.CONFIG_SERVICE_URL)  # Uses WOPR_CONFIG_SERVICE_URL env var

logger = woprlogging.setup_logging(woprvar.APP_NAME)

logger.info("WOPR API application: booting up...")

tracing_enabled = woprconfig.get_bool("tracing.enabled", False)

if tracing_enabled:
    from opentelemetry import trace
    tracing_endpoint = woprconfig.get_str("tracing.endpoint", "http://localhost:4317")
    tracer = woprtracing.create_tracer(
        tracer_name=woprvar.APP_NAME,
        tracer_enabled=tracing_enabled,
        tracer_endpoint=tracing_endpoint
    )
    if tracer:
        logger.info(f"Tracing enabled. Exporting to {tracing_endpoint}")
    else:
        logger.warning("Tracing is enabled but failed to initialize tracer.")
else:
    tracer = None
    logger.info("Tracing is disabled.")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import cameras
from typing import List

async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("WOPR API starting up...")
    with tracer.start_as_current_span("app_startup"):
        #setup_tracing()
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

# CORS
CORS_ORIGINS: List[str] = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["cameras"])

@app.get("/")
async def root():
    """Root endpoint"""
    with tracer.start_as_current_span("root_endpoint") if tracer else nullcontext():
        return {
            "service": woprvar.APP_TITLE,
            "version": woprvar.APP_VERSION,
            "status": "operational",
            "docs": "/docs"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=woprvar.SERVICE_HOST, port=woprvar.SERVICE_PORT)