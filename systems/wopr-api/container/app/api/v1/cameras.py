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
from pydantic import BaseModel
import httpx

router = APIRouter()

camera_dict = woprvar.HACK_CAMERA_DICT

class CaptureRequest(BaseModel):
    captureType: str
    game_id: str
    subject: str
    subject_name: str
    sequence: int

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
    game_id = request.game_id
    subject = request.subject
    subject_name = request.subject_name
    sequence = request.sequence
    logger.debug(f"Capturing image for game {game_id}, subject {subject}, subject_name {subject_name}, sequence {sequence}")
    """Capture image from camera (stub)"""

    if captureType == "ml_capture":
        camUrl = "http://wopr-cam.hangar.bpfx.org:5000/api/v1/capture_ml";
    else:
        camUrl = "http://wopr-cam.hangar.bpfx.org/api/v1/capture";

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{camUrl}",
                json={
                    "game_id": str(game_id) if game_id else None,
                    "subject": str(subject) if subject else None,
                    "subject_name": str(subject_name) if subject_name else None,
                    "sequence": int(sequence) if sequence else None
                }
            )
            response.raise_for_status()
            cam_response = response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to capture from camera: {str(e)}"
        )
    return {"game_id": game_id, "subject": subject, "subject_name": subject_name, "sequence": sequence}