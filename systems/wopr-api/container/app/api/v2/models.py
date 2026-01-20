"""
WOPR Models service
"""
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

logger = configure_logging(woprvar.LOGFILE)

# Usage
models_router = CRUDRouter(
    table_name="models",
    response_model=ModelResponse,
    create_model=ModelCreate,
    update_model=ModelUpdate,
    prefix="/models",
    tags=["models"]
).router

# Custom endpoint
@models_router.get("/{model_id}/stats")
async def get_model_stats(model_id: str):
    # Custom logic
    pass

@models_router.get("/health")
async def get_health():
    return "healthy"
