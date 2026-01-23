from fastapi import APIRouter, HTTPException, status
import requests
import logging
from app import globals as woprvar
from opentelemetry import trace
from contextlib import nullcontext
from app.directus_client import get_one, get_all, post, update, delete
from app.lib.crud import CRUDRouter
from app.lib.task_helper import (
    queue_task, 
    get_task_status,
    revoke_task,
    wait_for_task,
    get_all_tasks,
	get_all_active_tasks
)

from app.logging import configure_logging

from app.models.models import ModelResponse, ModelCreate, ModelUpdate

from app.lib.helpers import do_api_things

logger = configure_logging(woprvar.LOGFILE)

# Usage
models_router = CRUDRouter(
    table_name="models",
    response_model=ModelResponse,
    create_model=ModelCreate,
    update_model=ModelUpdate,
    prefix="",
    tags=["models"]
).router

# Custom endpoint
@models_router.get("/{model_id}/stats")
async def get_model_stats(model_id: str):
    """Get statistics for a specific model"""
    # Custom logic
    pass

@models_router.get("/health")
async def get_health():
    """Return healthy"""
    return "healthy"


@models_router.post("/status", response_model=ModelResponse)
async def update_model_status(data: ModelUpdate):
    """Update the status of a model"""
    logger.info("Updating model status")
    logger.debug(f"Update data: {data}")
    return data


@models_router.post("/activate")
async def activate_model(model_id: int, request=Request):
    """Activate a model"""
    logger.info("Activating model")
    logger.debug(f"Activation data: {data}")
    models_url = woprvar.WOPR_CONFIG["api"]["models_url"]

    action = "post"
    base_url = models_url
    route = "/api/v2/models"
    path = "activate"
    payload = {"model_id": model_id}
    results = do_api_things(action, base_url, route, path, payload)
    return results
