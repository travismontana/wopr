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
import os

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
        "data"      : data.model,
        "note"      : note,
        "extradata" : extradata,
        "status"    : status
    }
    data.last_operation = last_operation
    return data

@api_models.post("/status", response_model=ModelStatus)
async def get_model_status(data: ModelStatus, request: Request):
    logger.info(f"Received model status request: {data}")

    model_name = data.model

    config = request.app.state.config
    paths = request.app.state.paths
    logger.info(f"Paths: {paths}")
    filename = f"{model_name}.pt"
    models_path = paths["models_path"]
    protected_path = SafeFS(Path(models_path))
    
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
        logger.info(f"Downloaded files: {downloaded_files}")
    except Exception as e:
        logger.error(f"Error listing downloaded files: {e}")
        downloaded_files = []
    for file in downloaded_files:
        if file == filename:
            data.downloaded = True
    try:
        models_distfiles_path = paths["models_distfiles_path"]
        distfile_files = protected_path.listdir(models_distfiles_path)
    except:
        distfile_files = []
    if filename in distfile_files:
        data.distfile = True
        data.checksum = hashlib.sha256(f"{filename}")
    logger.info(f"STATUS: {data}")
    return data


@api_models.post("/download", response_model=ModelStatus)
async def download_model(data: ModelStatus, request: Request):
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
    
    model_info = next(
        (f for f in models if f.get("shortname") == model_name or f.get("name") == model_name),
        None
    )
    logdata.append({"model_info": model_info})
    
    if not model_info:
        return handle_error(data, "Model not found", "failed", {"model_name": model_name})
    
    model_families = get_all("model_family")
    
    familyid_to_get = model_info.get("familyid")
    logdata.append({"familyid_to_get": familyid_to_get})
    
    if not familyid_to_get:
        return handle_error(data, "Model has no family ID", "failed", {"model_info": model_info})
    
    familyname_to_get = next(
        (f for f in model_families if f["id"] == familyid_to_get),
        None
    )
    current_model_family = familyname_to_get
    logdata.append({"current_model_family": current_model_family})
    logger.info(f"Logdata: {logdata}")
    
    if not current_model_family:
        return handle_error(data, "Model family not found", "failed", {"familyid": familyid_to_get})
    
    filename = f"{current_model_family['name']}.pt"
    data.filename = filename
    url = current_model_family['url']
    logdata.append({"filename": filename, "url": url})
    logger.info(f"Logdata: {logdata}")

    # ← CHANGED: Download and check result
    data = await download_file(url, data, request)
    
    # ← CHANGED: Only wrap success if actually downloaded
    if data.downloaded:
        return handle_error(data, "Download completed", "success", {"logdata": logdata})
    else:
        # download_file already set last_operation with error details
        return data

async def download_file(url, data, request: Request):
    """Download a file with proper error handling and directory creation."""
    logdata = []
    timeout = httpx.Timeout(
        connect=10.0,
        read=None,      # ← CHANGED: No read timeout for large files
        write=10.0,
        pool=10.0
    )
    logdata.append({"timeout": timeout})
    
    paths = request.app.state.paths
    models_path = paths["models_path"]
    path = paths["models_download_path"]
    filename = data.filename
    
    # ← ADDED: Ensure directory exists
    download_dir = Path(models_path) / path
    download_dir.mkdir(parents=True, exist_ok=True)
    
    fullpath = download_dir / filename
    logger.info(f"Downloading {url} to {fullpath}")
    
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            async with client.stream('GET', url) as response:
                # ← ADDED: Check response status
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(fullpath, "wb") as file:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        file.write(chunk)
                        downloaded += len(chunk)
                
                logger.info(f"Downloaded {downloaded} bytes to {fullpath}")
                data.downloaded = True
                
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error downloading {url}: {e}")
        data.downloaded = False
        data.last_operation = {
            "task": "download_file",
            "status": "failed",
            "error": f"HTTP {e.response.status_code}",
            "url": url
        }
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        data.downloaded = False
        data.last_operation = {
            "task": "download_file",
            "status": "failed",
            "error": str(e),
            "url": url
        }
    
    return data  # ← ADDED: Actually return the data object

@api_models.post("/download", response_model=ModelStatus)
async def download_model(data: ModelStatus, request: Request):
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
    
    model_info = next(
        (f for f in models if f.get("shortname") == model_name or f.get("name") == model_name),
        None
    )
    logdata.append({"model_info": model_info})
    
    if not model_info:
        return handle_error(data, "Model not found", "failed", {"model_name": model_name})
    
    model_families = get_all("model_family")
    
    familyid_to_get = model_info.get("familyid")
    logdata.append({"familyid_to_get": familyid_to_get})
    
    if not familyid_to_get:
        return handle_error(data, "Model has no family ID", "failed", {"model_info": model_info})
    
    familyname_to_get = next(
        (f for f in model_families if f["id"] == familyid_to_get),
        None
    )
    current_model_family = familyname_to_get
    logdata.append({"current_model_family": current_model_family})
    logger.info(f"Logdata: {logdata}")
    
    if not current_model_family:
        return handle_error(data, "Model family not found", "failed", {"familyid": familyid_to_get})
    
    filename = f"{current_model_family['name']}.pt"
    data.filename = filename
    url = current_model_family['url']
    logdata.append({"filename": filename, "url": url})
    logger.info(f"Logdata: {logdata}")

    # ← CHANGED: Download and check result
    data = await download_file(url, data, request)
    protected_path = SafeFS(Path(models_path))
    # ← CHANGED: Only wrap success if actually downloaded
    if data.downloaded:
        # File download, now copy it to distfiles
        # files are in {models_download_path}
        source = f"{paths['models_download_path']}/{filename}"
        if not data.distfile:
            dest = f"{paths['models_distfiles_path']}/{filename}"
            results = copy_file(source,dest)
            handle_error(data, "Copied file to distfiles", "success", {"results": results})
        else:
            results = None
        if not data.backedup:
            dest = f"{paths['models_distfiles_path']}/{filename}"
            results = copy_file(source,dest)
            handle_error(data, "Copied file to distfiles", "success", {"results": results})
        return handle_error(data, "Download completed", "success", {"logdata": logdata})
    else:
        # download_file already set last_operation with error details
        return data