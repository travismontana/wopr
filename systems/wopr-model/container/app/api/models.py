import logging
import httpx
from fastapi import FastAPI, HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path
import hashlib
import inspect

from lib.helpers import (
    get_config, get_all, get_one,
    setup_logger
)

from lib.safe_file import (
    SafeFS
)
logger = setup_logger()
WOPR_API_URL = "https://api.wopr.tailandtraillabs.org/api/v2"

api_models = APIRouter(tags=["models"])

class ModelStatus(BaseModel):
    model: str
    backedup: Optional[bool] = False
    checksum: Optional[str] = None
    downloaded: Optional[bool] = False
    distfile: Optional[bool] = False
    filename: Optional[str] = None
    last_operation: Optional[dict] = None

def handle_error(data,note,status,extradata):
    logger.info("Handling error")
    caller = inspect.stack()[1].function
    last_operation = {
        "task"      : caller,
        "data"      : data.dict(),
        "note"      : note,
        "extradata" : extradata,
        "status"    : status
    }
    data.last_operation = last_operation
    return data

@api_models.post("/status", response_model=ModelStatus)
def get_model_status(data: ModelStatus, request: Request):
    logger.info(f"Received model status request: {data}")

    model_name = data.model

    config = request.app.state.config
    paths = request.app.state.paths
    logger.info(f"Paths: {paths}")
    filename = f"{model_name}.pt"

    protected_path = SafeFS(Path(paths["base_path"]))
    models_path = paths["models_path"]
    
    try:
        models_backup_path = paths["models_backup_path"]
        backup_files = protected_path.listdir(models_backup_path)
    except:
        backup_files = []
    if f"{filename}.gz" in backup_files:
        data.backedup = True
    
    try:
        models_download_path = paths["models_download_path"]
        downloaded_files = protected_path.listdir(models_download_path)
    except:
        downloaded_files = []
    if filename in downloaded_files:
        data.downloaded = True
    
    try:
        models_distfiles_path = paths["models_distfiles_path"]
        distfile_files = protected_path.listdir(models_distfiles_path)
    except:
        distfile_files = []
    if filename in distfile_files:
        data.distfile = True
        data.checksum = hashlib.sha256(f"{filename}")

    return data


@api_models.post("/download", response_model=ModelStatus)
def download_model(data: ModelStatus, request: Request):
    logger.info(f"Received model download request: {data}")
    logdata = []
    model_name = data.model
    logdata.append({"model_name": model_name})
    
    try:
        models = request.app.state.models or get_all("models")
    except Exception as e:
        logger.error(f"Failed to retrieve models: {e}")
        return handle_error(data, "Error getting models", "failed", {"error": str(e)})
    
    if not models:
        return handle_error(data, "Error getting models", "failed", {})
    
    logdata.append({"models": models})
    
    config = request.app.state.config
    paths = request.app.state.paths
    
    # ← CHANGED: Search by shortname OR name
    model_info = next(
        (f for f in models if f.get("shortname") == model_name or f.get("name") == model_name),
        None  # ← CHANGED: Use None instead of ""
    )
    logdata.append({"model_info": model_info})

    
    # ← CHANGED: Validate model_info exists
    if not model_info:
        return handle_error(data, "Model not found", "failed", {"model_name": model_name})
    
    model_families = get_all("model_family")
    
    familyid_to_get = model_info.get("familyid")  # ← CHANGED: Use .get() for safety
    logdata.append({"familyid_to_get": familyid_to_get})
    
    # ← CHANGED: Validate familyid exists
    if not familyid_to_get:
        return handle_error(data, "Model has no family ID", "failed", {"model_info": model_info})
    
    familyname_to_get = next(
        (f for f in model_families if f["id"] == familyid_to_get),
        None  # ← CHANGED: Use None instead of ""
    )
    current_model_family = familyname_to_get
    logdata.append({"current_model_family": current_model_family})
    logger.info(f"Logdata: {logdata}")
    if not current_model_family:
        return handle_error(data, "Model family not found", "failed", {"familyid": familyid_to_get})
    
    filename = f"{current_model_family['name']}.pt"
    url = current_model_family['url']
    logger.info(f"Logdata: {logdata}")
    
    return data