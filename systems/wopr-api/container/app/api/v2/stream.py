#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob Bomar <bob@bomar.us>
# See git log for detailed authorship

WOPR API - games CRUD endpoints (Directus schema).
"""

"""
  Endpoint:
  GET /gameid/{game_id}
    - get all pieces for a specific game (all info)
      {DIRECTUS_API_URL}/items/pieces?filter[game_id][_eq]={game
  
  Both return json.
  
"""
from . import router, logger
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app import globals as woprvar
import requests
router = APIRouter(tags=["stream"])

@router.get("/grab/{camera_id}/", response_model=dict)
def grab_stream(camera_id: str):
    """
    Grab a stream from a specific camera.
    """
    logger.info(f"Grabbing stream from camera ID {camera_id}")
    CAMURL = woprvar.WOPR_CONFIG['camera']['camDict'][camera_id]['host']
    CAMPORT = woprvar.WOPR_CONFIG['camera']['camDict'][camera_id]['port']
    CAMLCLID = woprvar.WOPR_CONFIG['camera']['camDict'][camera_id]['id']
    URL = f"{CAMURL}:{CAMPORT}/camera/stream/{CAMLCLID}"
    
    try:
        response = requests.get(URL)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        logger.error(f"Error grabbing stream from WOPR API: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error grabbing stream, error: {e}")
