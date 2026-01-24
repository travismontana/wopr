from fastapi import APIRouter

from lib import globals as worpvar
from lib.helpers import setup_logging
from lib.directus_client import get_one, get_all, post, update, delete

logger = setup_logging("wopr-api", "INFO", "/tmp/wopr-api.log")

router = APIRouter(
    tags=["ml_model_families"],
)


@router.get("", response_model=list)
async def get_ml_model_families():
    """Get ML Models configuration."""
    logger.info("Fetching ML Models configuration")
    return get_all("model_families")


@router.patch("/{model_family_id}", response_model=dict)
async def update_ml_model_family(model_family_id: str, payload: dict):
    """Update ML Model configuration."""
    logger.info(f"Updating ML Model {model_family_id}")
    return update("model_familys", model_family_id, payload)

@router.post("", response_model=dict)
async def create_ml_model_family(payload: dict):
    """Create new ML Model configuration."""
    logger.info("Creating new ML Model")
    return post("model_family_familys", payload)

@router.delete("/{model_family_id}", status_code=204)
async def delete_ml_model_family(model_family_id: str):
    """Delete ML Model configuration."""
    logger.info(f"Deleting ML Model {model_family_id}")
    return delete("model_familys", model_family_id)
