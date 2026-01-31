import logging
import httpx
import torch

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from ultralytics.utils.torch_utils import select_device

from lib.helpers import setup_logger

from api import model_ctl

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
app.include_router(model_ctl.model_ctl, prefix="/api/v2/model_ctl", tags=["models"])

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
    device = select_device(
        device="", verbose=False
    )  # "" = auto-select, same as default

    gpu_status = {
        "device_selected": str(device),  # e.g. "cuda:0" or "cpu"
        "cuda_available": torch.cuda.is_available(),
        "device_count": torch.cuda.device_count(),
        "device_name": (
            torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        ),  # e.g. "NVIDIA GeForce RTX 3060"
    }
    status.append({"variables": global_vars})
    status.append({"gpu_status": gpu_status})

    return status
