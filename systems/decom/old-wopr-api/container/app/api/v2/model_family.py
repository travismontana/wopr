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

from app.models.model_family import ModelFamilyResponse, ModelFamilyCreate, ModelFamilyUpdate

logger = configure_logging(woprvar.LOGFILE)

# Usage
model_family_router = CRUDRouter(
    table_name="model_family",
    response_model=ModelFamilyResponse,
    create_model=ModelFamilyCreate,
    update_model=ModelFamilyUpdate,
    prefix="",
    tags=["model_family"]
).router

# Custom endpoint
@model_family_router.get("/{model_family_id}/stats")
async def get_model_stats(model_family_id: str):
    # Custom logic
    pass

@model_family_router.get("/health")
async def get_health():
    return "healthy"
