#!/usr/bin/env python3
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
from typing import Optional, Dict, List
from functools import lru_cache

router = APIRouter(tags=["homeauto"])

# Config service URL - adjust as needed
CONFIG_SERVICE_URL = "http://wopr-api:8000/api/v1/config"  # ← CHANGE THIS TO YOUR CONFIG SERVICE URL


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


async def fetch_light_settings() -> Dict:
    """
    Fetch light settings from config service.
    
    Returns dict with structure:
    {
        "intensity": ["10", "20", ...],
        "temps": {"cool": "5500", "warm": "3000", "neutral": "4000"}
    }
    """
    settings = dict()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{CONFIG_SERVICE_URL}/get/lightSettings.intensity"
            )
            response.raise_for_status()
            settings["intensity"] = response.json()["value"]
            
            logger.debug(f"Fetched light settings from config: {settings}")
            
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch light settings from config service: {str(e)}")
        # Fallback to defaults if config service unavailable
        logger.warning("Using fallback default light settings")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{CONFIG_SERVICE_URL}/get/lightSettings.tempNames"
            )
            response.raise_for_status()
            settings["tempNames"] = response.json()["value"]
            
            logger.debug(f"Fetched light settings from config: {settings}")
            
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch light settings from config service: {str(e)}")
        # Fallback to defaults if config service unavailable
        logger.warning("Using fallback default light settings")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{CONFIG_SERVICE_URL}/get/lightSettings.tempNums"
            )
            response.raise_for_status()
            settings["tempNums"] = response.json()["value"]
            
            logger.debug(f"Fetched light settings from config: {settings}")
            
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch light settings from config service: {str(e)}")
        # Fallback to defaults if config service unavailable
        logger.warning("Using fallback default light settings")

    return settings
    
def parse_intensity_list(intensity_list: List[str]) -> List[int]:
    """Convert string intensity values to integers"""
    return [int(i) for i in intensity_list]


def parse_temps_dict(temps: Dict[str, str]) -> Dict[str, int]:
    """Convert string kelvin values to integers"""
    return {k: int(v) for k, v in temps.items()}


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
    
    # Fetch current light settings from config
    light_settings = await fetch_light_settings()
    
    # Parse and validate kelvin against config
    temps = parse_temps_dict(light_settings["tempNums"]).values()
    valid_kelvin = temps
    
    if request.kelvin not in valid_kelvin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid kelvin value. Must be one of: {valid_kelvin}"
        )
    
    # Parse and validate brightness against config
    valid_brightness = parse_intensity_list(light_settings["intensity"])
    
    if request.brightness not in valid_brightness:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid brightness value. Must be one of: {valid_brightness}"
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

        if isinstance(ha_response, dict):
            changed_states = ha_response.get("changed_states", [])
            service_response = ha_response.get("service_response")
        elif isinstance(ha_response, list):
            changed_states = ha_response
            service_response = None
        else:
            changed_states = []
            service_response = ha_response

        return HomeAssistantResponse(
            changed_states=changed_states,
            service_response=service_response
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
    Fetches values from config service.
    
    Returns:
        Dictionary with valid brightness percentages and kelvin temperatures
    """
    light_settings = await fetch_light_settings()
    
    # Parse config values
    brightness_options = parse_intensity_list(light_settings["intensity"])
    temps = light_settings["tempNums"]
    kelvin_descriptions = light_settings["tempNames"]
    kelvin_options = temps
    
    # Build reverse lookup for descriptions
    #kelvin_descriptions = {v: k for k, v in temps.items()}
    
    return {
        "brightness_options": brightness_options,
        "kelvin_options": kelvin_options,
        "kelvin_descriptions": kelvin_descriptions
    }