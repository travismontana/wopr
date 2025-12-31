"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob <bob@example.com>
# See git log for detailed authorship

WOPR API - Home Automation integration.
Proxies requests to Home Assistant REST API for controlling lights and other automation.
"""

from app import globals as woprvar
import logging
import sys

logger = logging.getLogger(woprvar.APP_NAME)
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import httpx
from typing import Optional

router = APIRouter(tags=["homeauto"])


class LightPresetRequest(BaseModel):
    """Request model for setting light preset"""
    brightness: int = Field(..., ge=10, le=100, description="Brightness percentage (10-100)")
    kelvin: int = Field(..., description="Color temperature in Kelvin (3000/4000/5500)")

    class Config:
        json_schema_extra = {
            "example": {
                "brightness": 50,
                "kelvin": 4000
            }
        }


class HomeAssistantResponse(BaseModel):
    """Response from Home Assistant service call"""
    changed_states: list = Field(default_factory=list)
    service_response: Optional[dict] = None


@router.post("/lights/preset", response_model=HomeAssistantResponse)
async def set_light_preset(request: LightPresetRequest):
    """
    Set office lights to specified brightness and color temperature.
    
    Calls Home Assistant script.office_lights_preset with provided parameters.
    
    Args:
        request: LightPresetRequest containing brightness (10-100%) and kelvin (3000/4000/5500K)
        
    Returns:
        HomeAssistantResponse with changed states and any service response data
        
    Raises:
        HTTPException: 503 if Home Assistant is unreachable
        HTTPException: 400 if parameters are invalid
    """
    logger.debug(
        f"Setting light preset: brightness={request.brightness}%, kelvin={request.kelvin}K"
    )
    
    # Validate kelvin is one of the supported values
    valid_kelvin = [3000, 4000, 5500]
    if request.kelvin not in valid_kelvin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid kelvin value. Must be one of: {valid_kelvin}"
        )
    
    # Validate brightness is in 10% increments
    if request.brightness % 10 != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brightness must be in 10% increments (10, 20, 30, ...100)"
        )
    
    # Build Home Assistant API URL
    ha_url = f"{woprvar.HOMEASSISTANT_URL}/api/services/script/office_lights_preset"
    
    # Prepare headers with authentication
    headers = {
        "Authorization": f"Bearer {woprvar.HOMEASSISTANT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Prepare service data
    service_data = {
        "brightness": request.brightness,
        "kelvin": request.kelvin
    }
    
    logger.debug(f"Calling Home Assistant API: {ha_url}")
    logger.debug(f"Service data: {service_data}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                ha_url,
                headers=headers,
                json=service_data
            )
            response.raise_for_status()
            ha_response = response.json()
            
        logger.info(
            f"Light preset set successfully: brightness={request.brightness}%, "
            f"kelvin={request.kelvin}K"
        )
        
        return HomeAssistantResponse(
            changed_states=ha_response.get("changed_states", []),
            service_response=ha_response.get("service_response")
        )
        
    except httpx.HTTPStatusError as e:
        logger.error(f"Home Assistant returned error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Home Assistant error: {e.response.text}"
        )
    except httpx.HTTPError as e:
        logger.error(f"Failed to reach Home Assistant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to communicate with Home Assistant: {str(e)}"
        )


@router.get("/lights/preset/options")
async def get_preset_options():
    """
    Get available brightness and kelvin options for light presets.
    
    Returns:
        Dictionary with valid brightness percentages and kelvin temperatures
    """
    return {
        "brightness_options": list(range(10, 101, 10)),
        "kelvin_options": [3000, 4000, 5500],
        "kelvin_descriptions": {
            3000: "warm",
            4000: "neutral", 
            5500: "cool"
        }
    }