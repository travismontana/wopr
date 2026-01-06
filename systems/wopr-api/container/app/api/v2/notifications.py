#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob Bomar <bob@bomar.us>
# See git log for detailed authorship

WOPR API - notifications
"""

"""
  Endpoint:
  POST /
  Needs:
  {
  "username": "WOPR",
  "embeds": [
    {
      "title": "Game Over",
      "description": "Game ID 1234 has ended.",
      "color": 16711680
    }]}
  
"""
from . import router, logger
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app import globals as woprvar
import requests

router = APIRouter(tags=["notifications"])

@router.post("/")
@router.post("")
async def create_notification(notification: dict):
    """Create a notification"""
    logger.info("Sending notification to Discord webhook")
    URL = woprvar.WOPR_CONF['notifications']['discord']['webhook_url']
    logger.debug(f"Discord Webhook URL: {URL}")
    try:
      logger.debug(f"Notification payload: {notification}")
      response = requests.post(URL, json=notification)
      response.raise_for_status()
      return {"detail": "Notification sent successfully"}
    except requests.RequestException as e:
      logger.error(f"Error sending notification: {e}")
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error sending notification, error: {e}")



