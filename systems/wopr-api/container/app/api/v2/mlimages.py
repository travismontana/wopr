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

@router.post("/capture", response_model=dict)
def capture_piece_image(payload: dict):
  """Capture an image for a specific piece"""
  """ Receiving application/json payload with:
    "game_id": selectedGame['id'],
    "piece_id": selectedPiece['id'],
    "light_intensity": lightIntensity,
    "color_temp": lightTemp,
    "object_rotation": objectRotation,
    "object_position": objectPosition
  
  then need to send, that to 
  {woprvar.DIRECTUS_URL}/items/mlimages
  """
  logger.info("Capturing piece image with payload: %s", payload)
  URL = f"{woprvar.DIRECTUS_URL}/items/mlimages"

  try:
      response = requests.post(URL, json=payload, headers=woprvar.DIRECTUS_HEADERS)
      response.raise_for_status()
      logger.info("Successfully captured piece image, response: %s", response.json())
  except requests.RequestException as e:
      logger.error(f"Error capturing piece image: {e}")
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error capturing piece image, error: {e}")

  """ now we get the uuid, then build the filename, then call teh camera API to take the picture """ 
  URL = f"{woprvar.DIRECTUS_URL}/items/mlimages/{response.json().get('data', {}).get('id')}"
  
  try:
    response = requests.get(URL, headers=woprvar.DIRECTUS_HEADERS)
    response.raise_for_status()
    data = response.json()
  except requests.RequestException as e:
    logger.error(f"Error fetching games from Directus: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching games, error: {e}")

  logger.info("Fetched mlimage data: %s", data)
  """ now we have the data, build the filename """
  image_uuid = data.get('data', {}).get('uuid')
  piece_id = data.get('data', {}).get('piece_id')
  game_id = data.get('data', {}).get('game_id')
  if not image_uuid:
      logger.error("No UUID found in mlimage data")
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No UUID found in mlimage data")
  
  FILENAME = f"{piece_id}-{game_id}-{image_uuid}.jpg"
  payload = {
      "filename": FILENAME
  }
  try:
      response = requests.post(URL, json=payload, headers=woprvar.DIRECTUS_HEADERS)
      response.raise_for_status()
      logger.info("Successfully updated piece filename, response: %s", response.json())
  except requests.RequestException as e:
      logger.error(f"Error capturing piece image: {e}")
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error setting filename for piece image, error: {e}")