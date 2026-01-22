import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from wopr_api_client import Client
from wopr_api_client.api.models import get_all_items_api_v2_models_get
from wopr_api_client.api.config import get_all_api_v2_config_all_get

from lib.helpers import setup_logger

from api import models

logger = setup_logger()

API_BASE = "https://api.wopr.tailandtraillabs.org"
woprclient = Client(base_url=API_BASE)


def _to_dict(obj):
    """Convert response object to dict for backwards compatibility."""
    if obj is None:
        return obj
    if isinstance(obj, list):
        return [_to_dict(item) for item in obj]
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return obj


def get_config():
    """Fetch configuration using wopr_api_client."""
    try:
        result = get_all_api_v2_config_all_get.sync(client=woprclient)
        logger.info(f"Config item {result}")
        return result
    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        return {}


def get_all_models() -> list:
    """Fetch all models using wopr_api_client."""
    try:
        result = get_all_items_api_v2_models_get.sync(client=woprclient)
        return _to_dict(result) or []
    except Exception as e:
        logger.error(f"Failed to fetch models: {e}")
        return []


# Get config
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

# Get models using wopr_api_client
app.state.models = get_all_models()


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
