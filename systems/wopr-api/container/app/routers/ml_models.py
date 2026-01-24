from fastapi import APIRouter

from lib import globals as worpvar
from lib.helpers import setup_logging
from lib.directus_client import get_one, get_all, post, update, delete

logger = setup_logging("wopr-api", "INFO", "/tmp/wopr-api.log")

router = APIRouter(
    tags=["ml_models"],
)

@router.get("", response_model=list)
async def get_ml_models():
    """Get ML Models configuration."""
    logger.info("Fetching ML Models configuration")
    return get_all("models")

@router.patch("/{model_id}", response_model=dict)
async def update_ml_model(model_id: str, payload: dict):
    """Update ML Model configuration."""
    logger.info(f"Updating ML Model {model_id}")
    return update("models", model_id, payload)

@router.post("", response_model=dict)
async def create_ml_model(payload: dict):
    """Create new ML Model configuration."""
    logger.info("Creating new ML Model")
    return post("models", payload)

@router.delete("/{model_id}", status_code=204)
async def delete_ml_model(model_id: str):
    """Delete ML Model configuration."""
    logger.info(f"Deleting ML Model {model_id}")
    return delete("models", model_id)

