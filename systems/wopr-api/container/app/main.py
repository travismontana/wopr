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
from app import globals as woprvar

# Initialize config client at startup
woprconfig.init_config(service_url=woprvar.CONFIG_SERVICE_URL)  # Uses WOPR_CONFIG_SERVICE_URL env var

logger = woprlogging.setup_logging(woprvar.APP_NAME)

logger.info("WOPR API application: booting up...")

from fastapi import FastAPI
from app.api.v1 import cameras

async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    logger.info("WOPR API starting up...")
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

app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["cameras"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": woprvar.APP_TITLE,
        "version": woprvar.APP_VERSION,
        "status": "operational",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=woprvar.SERVICE_HOST, port=woprvar.SERVICE_PORT)