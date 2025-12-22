#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2023-present Bob <bob@bomar.us>
# See git log for detailed authorship

WOPR API main application.
"""

import logging

from fastapi import FastAPI

from wopr.config import init_config, get_str, get_int
from wopr.storage import imagefilename
from wopr.logging import setup_logging

# Initialize config client at startup
init_config()  # Uses WOPR_CONFIG_SERVICE_URL env var

logger = setup_logging(__wopr-name__)

logger.info("Starting WOPR API application")
app = FastAPI(
    title=__wopr-title__,
    description=__wopr-description__,
    version=__wopr-version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": __wopr-author__,
        "email": __wopr-author_email__,
    },
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": __wopr-title__,
        "version": __wopr-version__,
        "status": "operational",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)