"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob <bob@example.com>
# See git log for detailed authorship

WOPR API - cameras api.

"""

from wopr import config as woprconfig
from wopr import storage as woprstorage
from wopr import logging as woprlogging
from app import globals as woprvar

import logging
logger = woprlogging.setup_logging(woprvar.APP_NAME)

from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()

camera_dict = woprvar.HACK_CAMERA_DICT

@router.get("")
async def listall():
    logger.debug("Listing all cameras")
    """Get list of cameras (stub)"""
    return {"cameras": list(camera_dict.values())}

@router.get("/{camera_id}")
async def get_camera(camera_id: str):
    logger.debug(f"Getting camera {camera_id}")
    """Get camera by ID (stub)"""
    camera = camera_dict.get(camera_id)
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with ID {camera_id} not found"
        )
    return camera