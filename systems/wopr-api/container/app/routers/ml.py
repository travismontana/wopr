"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob <bob@bomar.us>
# See git log for detailed authorship

Brief description of what this file does.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx
import asyncio
from typing import Optional
from datetime import datetime

from app import globals as woprvar
import logging
import sys

logger = logging.getLogger(woprvar.APP_NAME)
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

# ← CREATE ROUTER BEFORE USING IT
router = APIRouter(prefix="/api/v1/ml", tags=["ml"])


class CaptureRequest(BaseModel):
    game_id: int
    piece_id: int
    position_id: int
    rotation: int = Field(ge=0, le=360, description="Rotation in degrees 0-360, in 45 degree increments")
    lighting_level: int = Field(ge=10, le=100, description="Brightness 10-100")
    lighting_temp: str = Field(description="neutral/warm/cool")
    notes: Optional[str] = None


class CaptureResponse(BaseModel):
    success: bool
    image_metadata_id: Optional[int] = None
    message: str
    lighting_set: bool
    image_captured: bool



@router.post("/captureandsetlights", response_model=CaptureResponse)
async def capture_and_set_lights(request: CaptureRequest):
    logger.info(f"Received ML capture and set lights request 2222: {request}")
    """
    Orchestrates ML training image capture:
    1. Generates filename
    2. Sets lighting via homeauto API
    3. Waits 10 seconds for stabilization
    4. Captures image via camera
    5. Creates metadata record
    6. Returns metadata
    """
    # Map lighting_temp string to kelvin values
    temp_to_kelvin = {
        "neutral": 4000,
        "warm": 3000,
        "cool": 5500
    }
    
    kelvin = temp_to_kelvin.get(request.lighting_temp.lower())
    if kelvin is None:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid lighting_temp: {request.lighting_temp}. Must be 'neutral', 'warm', or 'cool'"
        )
    
    lighting_set = False
    image_captured = False
    image_metadata_id = None
    filename = None
    logger.info(f"Starting ML capture process for request: {request}")
    try:
        # Step 1: Generate filename
        filename = await generate_ml_filename(
            request.game_id,
            request.piece_id,
            request.rotation,
            request.position_id,
            request.lighting_temp,
            request.lighting_level
        )
        logger.info(f"Generated filename: {filename}")

        # Step 2: Set lights
        async with httpx.AsyncClient(timeout=30.0) as client:
            homeauto_response = await client.post(
                "http://wopr-api:8000/api/v1/homeauto/lights/preset",
                json={
                    "brightness": request.lighting_level,
                    "kelvin": kelvin
                }
            )
            homeauto_response.raise_for_status()
            lighting_set = True
            logger.info(f"Lights set successfully to {kelvin}K @ {request.lighting_level}%")

        # Step 3: Wait for stabilization
        logger.info("Waiting 3 seconds for lighting stabilization...")
        await asyncio.sleep(3)

        # Step 4: Capture image via camera
        logger.info(f"Calling camera capture with filename: {filename}")
        async with httpx.AsyncClient(timeout=60.0) as client:
            camera_response = await client.post(
                "http://wopr-api:8000/api/v1/cameras/capture",
                json={
                    "captureType": "ml_capture",
                    "filename": filename
                }
            )
            camera_response.raise_for_status()
            logger.info(f"Camera capture complete: {filename}")

        # Step 5: Create metadata record
        logger.info(f"Creating metadata: game={request.game_id}, piece={request.piece_id}, pos={request.position_id}")
        async with httpx.AsyncClient(timeout=60.0) as client:
            metadata_response = await client.post(
                "http://wopr-api:8000/api/v1/mlimages",
                json={
                    "filename": filename,
                    "object_rotation": request.rotation,
                    "object_position": request.position_id,
                    "color_temp": request.lighting_temp,
                    "light_intensity": request.lighting_level,
                    "game_uuid": request.game_id,
                    "piece_id": request.piece_id,
                    "status": "draft",
                    "notes": request.notes
                }
            )
            metadata_response.raise_for_status()
            metadata_data = metadata_response.json()
            image_captured = True
            image_metadata_id = metadata_data.get("id")
            logger.info(f"Metadata created: id={image_metadata_id}")

        return CaptureResponse(
            success=True,
            image_metadata_id=image_metadata_id,
            message=f"Image captured successfully: {filename}",
            lighting_set=lighting_set,
            image_captured=image_captured
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during capture: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Upstream service error: {e.response.text}"
        )
    except httpx.RequestError as e:
        logger.error(f"Request error during capture: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during capture: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Capture failed: {str(e)}"
        )


async def generate_ml_filename(
    game_id: int,
    piece_id: int,
    position_id: int,
    rotation: int,
    color_temp: str,
    light_intensity: int
) -> str:
    """
    Generate ML training image filename matching frontend pattern:
    {piece}-{game}-{position}-rot{rotation}-pct{intensity}-temp{colortemp}-{timestamp}.jpg
    """
    # Fetch game and piece names
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            game_res = await client.get(f"http://wopr-api:8000/api/v1/games/{game_id}")
            game_res.raise_for_status()
            game_name = game_res.json().get("name", "unknown")
        except:
            game_name = "unknown"
        
        try:
            piece_res = await client.get(f"http://wopr-api:8000/api/v1/pieces/{piece_id}")
            piece_res.raise_for_status()
            piece_name = piece_res.json().get("name", "unknown")
        except:
            piece_name = "unknown"
    
    # Sanitize names
    def sanitize(s: str) -> str:
        return ''.join(c if c.isalnum() or c == '_' else '_' for c in s.lower())

    
    # Generate timestamp
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d-%H%M%S")
    
    # Build filename
    parts = [
        sanitize(piece_name),
        sanitize(game_name),
        f"pos{position_id}",
        f"rot{rotation}",
        f"pct{light_intensity}",
        f"temp{sanitize(color_temp)}",
        timestamp
    ]
    logger.info(f"*****Generated filename parts: {parts}")
    return f"{'-'.join(parts)}.jpg"