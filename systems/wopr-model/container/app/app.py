import logging
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from lib.helpers import get_all, setup_logger

from api import models

logger = setup_logger()

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

base_path = "/remote/wopr"
models_path = f"{base_path}/models"
models_backup_path = f"{base_path}/backups"
models_download_path = f"{base_path}/downloads"
models_distfiles_path = f"{base_path}/distfiles"

paths = {
    "base_path": base_path,
    "models_path": models_path,
    "models_backup_path": models_backup_path,
    "models_download_path": models_download_path,
    "models_distfiles_path": models_distfiles_path
}

app.state.paths = paths
app.state.config = {"app_name": APP_NAME, "app_api_version": APP_API_VERSION}
# Here
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
