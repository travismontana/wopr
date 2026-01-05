#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob Bomar <bob@bomar.us>
# See git log for detailed authorship

WOPR API - games CRUD endpoints (Directus schema).
"""

"""
  Endpoint:
  /images/gameid/{game_catalog_uuid}
    {DIRECTUS_API_URL}/items/mlimages?filter[game_catalog_uuid][_eq]={game_catalog_uuid}
  /images/pieceid/{piece_id}
    {DIRECTUS_API_URL}/items/mlimages?filter[piece_id][_eq]={piece_id}
  /images/all
    {DIRECTUS_API_URL}/items/mlimages

  Both return json.
  
"""
from . import router, logger
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app import globals as woprvar
import requests
router = APIRouter(tags=["images"])
logger.info("Images API module loaded")

@router.get("/gameid/{game_catalog_uuid}/", response_model=list[dict])
@router.get("/gameid/{game_catalog_uuid}", response_model=list[dict])
def get_images_by_game_catalog_uuid(game_catalog_uuid: int):
  """Get all images for a specific game catalog UUID"""
  logger.info(f"Fetching images for game catalog UUID {game_catalog_uuid} from the directus api")
  URL = f"{woprvar.DIRECTUS_URL}/items/mlimages?filter[game_catalog_uuid][_eq]={game_catalog_uuid}"
  
  try:
    response = requests.get(URL, headers=woprvar.DIRECTUS_HEADERS)
    response.raise_for_status()
    data = response.json()
    return data.get('data', [])
  except requests.RequestException as e:
    logger.error(f"Error fetching images from Directus: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching images, error: {e}")

@router.get("/pieceid/{piece_id}/", response_model=list[dict])
@router.get("/pieceid/{piece_id}", response_model=list[dict])
def get_images_by_piece_id(piece_id: int):
  """Get all images for a specific piece ID"""
  logger.info(f"Fetching images for piece ID {piece_id} from the directus api")
  URL = f"{woprvar.DIRECTUS_URL}/items/mlimages?filter[piece_id][_eq]={piece_id}"
  
  try:
    response = requests.get(URL, headers=woprvar.DIRECTUS_HEADERS)
    response.raise_for_status()
    data = response.json()
    return data.get('data', [])
  except requests.RequestException as e:
    logger.error(f"Error fetching images from Directus: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching images, error: {e}")

@router.get("/all/", response_model=list[dict])
@router.get("/all", response_model=list[dict])
def get_all_images():
  """Get all images"""
  logger.info("Fetching all images from the directus api")
  URL = f"{woprvar.DIRECTUS_URL}/items/mlimages"
  
  try:
    response = requests.get(URL, headers=woprvar.DIRECTUS_HEADERS)
    response.raise_for_status()
    data = response.json()
    return data.get('data', [])
  except requests.RequestException as e:
    logger.error(f"Error fetching images from Directus: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching images, error: {e}") 
    