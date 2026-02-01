from fastapi import APIRouter

from lib import globals as worpvar
from lib.helpers import setup_logging

logger = setup_logging("wopr-api", "INFO", "/tmp/wopr-api.log")

router = APIRouter(
    tags=["config"],
)

@router.get("", response_model=dict)
async def get_config():
    """Get WOPR configuration."""
    logger.info("Fetching WOPR configuration")
    return worpvar.WOPR_CONFIG

@router.get('/refresh', response_model=dict)
async def refresh_config():
    """Refresh WOPR configuration."""
    logger.info("Refreshing WOPR configuration")
    worpvar.WOPR_CONFIG = worpvar.get_directus_config()[0]["data"]
    return worpvar.WOPR_CONFIG