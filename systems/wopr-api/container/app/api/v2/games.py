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
import requests

from . import router, logger
from fastapi import APIRouter, HTTPException, status

from pydantic import BaseModel, Field
from app import globals as woprvar

from app.directus_client import get_one, get_all, post, update, delete

router = APIRouter(tags=["games"])


@router.get("/{game_id}", response_model=dict)
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
  
@router.get("")
async def get_games():
    logger.info("Fetching all games")
    return get_all("game_catalog")

@router.get("/{game_id}")
async def get_game(game_id: str):
    logger.info(f"Fetching game with ID: {game_id}")
    return get_one("game_catalog", game_id)

@router.post("")
async def create_game(payload: dict):
	logger.info(f"Creating a new game with payload: {payload}")
	return post("game_catalog", payload)

@router.patch("/{game_id}")
async def update_game(game_id: str, payload: dict):
    logger.info(f"Updating game {game_id} with payload: {payload}")
    return update("game_catalog", game_id, payload)

@router.delete("/{game_id}")
async def delete_game(game_id: str):
    logger.info(f"Deleting game with ID: {game_id}")
    return delete("game_catalog", game_id)