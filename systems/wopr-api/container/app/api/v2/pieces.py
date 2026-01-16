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
router = APIRouter(tags=["pieces"])
@router.get("/gameid/{game_id}/", response_model=list[dict])
@router.get("/gameid/{game_id}", response_model=list[dict])
def get_pieces(game_id: int):
  """Get all pieces for a specific game"""
  logger.info(f"Fetching pieces for game ID {game_id} from the directus api")
  URL = f"{woprvar.DIRECTUS_URL}/items/pieces?filter[game_catalog_uuid][_eq]={game_id}"
  
  try:
    response = requests.get(URL, headers=woprvar.DIRECTUS_HEADERS)
    response.raise_for_status()
    data = response.json()
    return data.get('data', [])
  except requests.RequestException as e:
    logger.error(f"Error fetching pieces from Directus: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching pieces, error: {e}")

@router.get("")
async def get_pieces():
    logger.info("Fetching all pieces")
    return get_all("pieces")

@router.get("/{piece_id}")
async def get_piece(piece_id: str):
    logger.info(f"Fetching piece with ID: {piece_id}")
    return get_one("pieces", piece_id)

@router.post("")
async def create_piece(payload: dict):
	logger.info(f"Creating a new piece with payload: {payload}")
	return post("pieces", payload)

@router.patch("/{piece_id}")
async def update_piece(piece_id: str, payload: dict):
    logger.info(f"Updating piece {piece_id} with payload: {payload}")
    return update("pieces", piece_id, payload)

@router.delete("/{piece_id}")
async def delete_piece(piece_id: str):
    logger.info(f"Deleting piece with ID: {piece_id}")
    return delete("pieces", piece_id)