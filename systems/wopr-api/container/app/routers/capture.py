from fastapi import APIRouter

from lib import globals as woprvar
from lib.helpers import setup_logging, do_api_things
from lib.directus_client import get_one, get_all, post, update, delete

logger = setup_logging("wopr-api", "INFO", "/tmp/wopr-api.log")

router = APIRouter(
    tags=["capture"],
)


@router.post("", response_model=dict)
async def create_capture(payload: dict):
    """Create new Capture."""
    logger.info("Creating new Capture")
    host = woprvar.WOPR_CONFIG["camera"]["camDict"]["0"]["host"]
    port = woprvar.WOPR_CONFIG["camera"]["camDict"]["0"]["port"]
    action = "post"
    base_url = f"http://{host}:{port}"
    path = "/api/v1"
    route = "capture"
    return do_api_things(action, base_url, route, path, payload)
