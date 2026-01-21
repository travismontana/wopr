import logging
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from lib.helpers import (
    get_config, get_all,
    setup_logger
)

from api import models


logger = setup_logger()
WOPR_API_URL = "https://api.wopr.tailandtraillabs.org/api/v2"

config = get_config()
if len(config) == 0:
    logger.info("Configuration is empty or could not be loaded")

APP_NAME = "wopr-model"
APP_API_VERSION = "v1"

logger.info(f"Starting {APP_NAME} application")

logger.info(f"Setup variables")

# Allons Ye!
app = FastAPI(
    title=APP_NAME,
    )

# Load api's
app.include_router(models.api_models, prefix=f"/api/v2/models", tags=["models"])

# Build defaults

base_path = config['storage']['base_path']
models_path = f"{base_path}/{config['storage']['models_subdir']}"
models_backup_path = f"{config['storage']['models_backup_subdir']}"
models_download_path = f"downloads"
models_distfiles_path = f"distfiles"

paths = {
    "base_path": base_path,
    "models_path": models_path,
    "models_backup_path": models_backup_path,
    "models_download_path": models_download_path,
    "models_distfiles_path": models_distfiles_path
}

app.state.paths = paths
app.state.config = config

app.state.models = get_all("models")

# health page
@app.get("/health")
def get_health():
    return "healthy"

@app.get("/nelson")
def nelson():
    return "haha"

@app.get("/status")
def get_status():
    status = []
    global_vars = {
        "paths": app.state.paths,
        "config": app.state.config
    }
    status.append({"variables": global_vars})

    return status

