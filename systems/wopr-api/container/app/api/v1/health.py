import logging
import sys
import datetime
from app import globals as woprvar
logger = logging.getLogger(woprvar.APP_NAME)
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

from fastapi import APIRouter
router = APIRouter(tags=["status"])

@router.get("/", summary="Health Check", description="Check the health of the WOPR API.")
@router.get("", summary="Health Check", description="Check the health of the WOPR API.")
async def health_check() -> dict:
    logger.debug("Performing health check at %s", datetime.now(datetime.timezone.utc).isoformat())
    return {
        "status": "ok",
        "service": "wopr-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }