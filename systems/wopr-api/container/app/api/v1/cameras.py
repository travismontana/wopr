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
import sys
logger = logging.getLogger(woprvar.APP_NAME)
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import httpx

router = APIRouter(tags=["cameras"])

camera_dict = woprvar.HACK_CAMERA_DICT

class CaptureRequest(BaseModel):
    captureType: str
    filename: str

@router.get("")
async def listall():
    logger.debug("Listing all cameras")
    """Get list of cameras (stub)"""
    return {"cameras": list(camera_dict.values())}

@router.get("/{camera_id}")
async def get_camera(camera_id: str):
    logger.debug(f"Getting camera {camera_id}")
    """Get camera by ID (stub)"""
    camera = list(camera_dict.values())
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with ID {camera_id} not found"
        )
    return {"camera": camera}

@router.post("/capture")
async def capture_image(request: CaptureRequest):
    captureType = request.captureType
    filename = request.filename
    logger.debug(f"Capturing image for filename {filename}")
    """Capture image from camera (stub)"""

    if captureType == "ml_capture":
        camUrl = "http://wopr-cam.hangar.bpfx.org:5000/capture_ml";
    else:
        camUrl = "http://wopr-cam.hangar.bpfx.org:5000/capture";

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{camUrl}",
                json={
                    "filename": str(filename) if filename else None,
                }
            )
            response.raise_for_status()
            cam_response = response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to capture from camera: {str(e)}"
        )
    return {"filepath": cam_response}