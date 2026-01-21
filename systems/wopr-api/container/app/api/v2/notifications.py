from . import router, logger
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app import globals as woprvar
import requests
from app.logging import configure_logging
logger = configure_logging(woprvar.LOGFILE)
router = APIRouter(tags=["notifications"])

@router.post("/")
@router.post("")
async def create_notification(notification: dict):
    """Create a notification"""
    logger.info("Sending notification to Discord webhook: notification: %s", notification)
    URL = woprvar.WOPR_CONFIG['notifications']['discord']['webhook_url']
    logger.debug(f"Discord Webhook URL: {URL}")
    try:
      logger.debug(f"Notification payload: {notification}")
      response = requests.post(URL, json=notification)
      response.raise_for_status()
      return {"detail": "Notification sent successfully"}
    except requests.RequestException as e:
      logger.error(f"Error sending notification: {e}")
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error sending notification, error: {e}")



