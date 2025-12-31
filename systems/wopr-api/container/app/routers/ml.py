# wopr-api/app/routers/ml.py (or create if it doesn't exist)
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import httpx
import asyncio
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/ml", tags=["ml"])


class CaptureRequest(BaseModel):
    game_id: int
    piece_id: int
    position_id: int
    lighting_level: int = Field(ge=0, le=100, description="0-100")
    lighting_temp: str = Field(description="e.g., 'neutral', 'warm', 'cool'")
    notes: Optional[str] = None


class CaptureResponse(BaseModel):
    success: bool
    image_metadata_id: Optional[int] = None
    message: str
    lighting_set: bool
    image_captured: bool
    
@router.post("/captureandsetlights", response_model=CaptureResponse)
async def capture_and_set_lights(request: CaptureRequest):
    """
    Orchestrates ML training image capture:
    1. Sets lighting via homeauto API
    2. Waits 10 seconds for stabilization
    3. Captures image via mlimages endpoint
    4. Returns metadata record
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

    try:
        # Step 1: Set lights
        logger.info(f"Setting lights: level={request.lighting_level}, temp={request.lighting_temp} ({kelvin}K)")
        async with httpx.AsyncClient(timeout=30.0) as client:
            homeauto_response = await client.post(
                "http://wopr-api:8000/api/v1/homeauto/lights/preset",  # ← Fixed URL
                json={
                    "brightness": request.lighting_level,  # ← Fixed field name
                    "kelvin": kelvin  # ← Mapped integer value
                }
            )
            homeauto_response.raise_for_status()
            lighting_set = True
            logger.info(f"Lights set successfully to {kelvin}K @ {request.lighting_level}%")

        # Step 2: Wait for stabilization
        logger.info("Waiting 10 seconds for lighting stabilization...")
        await asyncio.sleep(10)

        # Step 3: Capture image
        logger.info(f"Capturing image: game={request.game_id}, piece={request.piece_id}, pos={request.position_id}")
        async with httpx.AsyncClient(timeout=60.0) as client:
            capture_response = await client.post(
                "http://wopr-api:8000/api/v1/mlimages",
                json={
                    "game_id": request.game_id,
                    "piece_id": request.piece_id,
                    "position_id": request.position_id,
                    "lighting_condition": request.lighting_temp,  # Store original string
                    "lighting_level": request.lighting_level,
                    "notes": request.notes
                }
            )
            capture_response.raise_for_status()
            capture_data = capture_response.json()
            image_captured = True
            image_metadata_id = capture_data.get("id")
            logger.info(f"Image captured: metadata_id={image_metadata_id}")

        return CaptureResponse(
            success=True,
            image_metadata_id=image_metadata_id,
            message=f"Image captured successfully for piece {request.piece_id} at position {request.position_id}",
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
