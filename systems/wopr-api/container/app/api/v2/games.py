#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob Bomar <bob@bomar.us>
# See git log for detailed authorship

WOPR API - games CRUD endpoints (Directus schema).
"""

"""
  Endpoint:
  GET /
    - get all games (all info)
      {DIRECTUS_API_URL}/items/games
  GET /{game_id}
    - get specific game (all info)
      {DIRECTUS_API_URL}/items/games/{game_id}
  
  Both return json.
  
"""
from . import router, logger
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app import globals as woprvar
import requests

@router.get("/api/v2/games/", response_model=list[dict])
@router.get("/api/v2/games", response_model=list[dict])
def get_games():
  """Get all games"""
  logger.info("Fetching all games from the directus api")
  URL = f"{woprvar.DIRECTUS_URL}/items/game_catalog"
  
  try:
    response = requests.get(URL, headers=woprvar.DIRECTUS_HEADERS)
    response.raise_for_status()
    data = response.json()
    return data.get('data', [])
  except requests.RequestException as e:
    logger.error(f"Error fetching games from Directus: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching games, error: {e}")

@router.get("/api/v2/games/{game_id}", response_model=dict)
def get_game(game_id: int):
  """Get a specific game by ID"""
  logger.info(f"Fetching game with ID {game_id} from the directus api")
  URL = f"{woprvar.DIRECTUS_URL}/items/game_catalog/{game_id}"
  
  try:
    response = requests.get(URL, headers=DIRECTUS_HEADERS)
    response.raise_for_status()
    data = response.json()
    return data.get('data', {})
  except requests.RequestException as e:
    logger.error(f"Error fetching game {game_id} from Directus: {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching game {game_id}, error: {e}")
  
  