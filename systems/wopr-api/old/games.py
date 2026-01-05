#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob <bob@example.com>
# See git log for detailed authorship

WOPR API - games CRUD endpoints (Directus schema).
"""

from wopr import logging as woprlogging
from app import globals as woprvar

import logging
import sys
from typing import Optional, List
from datetime import datetime
from contextlib import contextmanager
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import psycopg
from psycopg.rows import dict_row

logger = logging.getLogger(woprvar.APP_NAME)
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
router = APIRouter()

DATABASE_URL = woprvar.DATABASE_URL
logger.debug(f"Using database URL: {DATABASE_URL}")

@contextmanager
def get_db():
    """Database connection context manager"""
    logger.debug("Opening database connection")
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()
        logger.debug("Closed database connection")


class GameCreate(BaseModel):
    """Model for creating a game"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    min_players: Optional[int] = Field(None, ge=1)
    max_players: Optional[int] = Field(None, ge=1)
    url: Optional[str] = None
    status: str = Field(default="draft", pattern="^(draft|published)$")
    user_created: Optional[UUID] = None


class GameUpdate(BaseModel):
    """Model for updating a game"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    min_players: Optional[int] = Field(None, ge=1)
    max_players: Optional[int] = Field(None, ge=1)
    url: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|published)$")
    user_updated: Optional[UUID] = None


class GameResponse(BaseModel):
    """Model for game response"""
    id: int
    uuid: UUID
    name: str
    description: Optional[str]
    min_players: Optional[int]
    max_players: Optional[int]
    url: Optional[str]
    status: str
    user_created: Optional[UUID]
    date_created: datetime
    user_updated: Optional[UUID]
    date_updated: Optional[datetime]


@router.get("", response_model=List[GameResponse])
async def list_games(
    limit: int = 100,
    offset: int = 0,
    status: Optional[str] = None
):
    """
    List all games
    


@router.get("/{game_id}", response_model=GameResponse)
async def get_game(game_id: int):
    """
    Get a specific game by ID.
    
    Args:
        game_id: The game ID
    """
    logger.debug(f"Getting game {game_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT * FROM game_catalog WHERE id = %s",
                (game_id,)
            )
            game = cur.fetchone()
            if not game:
                logger.debug(f"Game {game_id} not found in DB")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game with ID {game_id} not found"
                )

            logger.debug(f"Found game {game_id}: {game.get('name')}")
            return game


@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(game: GameCreate):
    """
    Create a new game.
    
    Args:
        game: Game data
    """
    logger.info(f"Creating game: {game.name}")
    
    # Generate UUID for Directus document tracking
    game_uuid = uuid4()
    now = datetime.utcnow()
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO game_catalog (
                    uuid, name, description, min_players, max_players,
                    url, status, user_created, date_created
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    game_uuid,
                    game.name,
                    game.description,
                    game.min_players,
                    game.max_players,
                    game.url,
                    game.status,
                    game.user_created,
                    now
                )
            )
            conn.commit()
            new_game = cur.fetchone()
            
            logger.info(f"Created game {new_game['id']}: {new_game['name']}")
            return new_game


@router.put("/{game_id}", response_model=GameResponse)
async def update_game(game_id: int, game: GameUpdate):
    """
    Update an existing game.
    
    Args:
        game_id: The game ID
        game: Updated game data
    """
    logger.info(f"Updating game {game_id}")
    
    update_fields = []
    values = []
    
    for field, value in game.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = %s")
            values.append(value)
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    # Always update date_updated
    update_fields.append("date_updated = %s")
    values.append(datetime.utcnow())
    values.append(game_id)
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            query = f"""
                UPDATE game_catalog
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING *
            """
            
            cur.execute(query, values)
            conn.commit()
            updated_game = cur.fetchone()
            
            if not updated_game:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game with ID {game_id} not found"
                )
            
            logger.info(f"Updated game {game_id}")
            return updated_game


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(game_id: int):
    """
    Delete a game.
    
    Args:
        game_id: The game ID
    """
    logger.info(f"Deleting game {game_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "DELETE FROM game_catalog WHERE id = %s RETURNING id",
                (game_id,)
            )
            conn.commit()
            deleted = cur.fetchone()
            
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game with ID {game_id} not found"
                )
            
            logger.info(f"Deleted game {game_id}")


@router.patch("/{game_id}/publish", response_model=GameResponse)
async def publish_game(game_id: int):
    """
    Publish a game (set status to 'published').
    
    Args:
        game_id: The game ID
    """
    logger.info(f"Publishing game {game_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                UPDATE game_catalog
                SET status = 'published', date_updated = %s
                WHERE id = %s
                RETURNING *
                """,
                (datetime.utcnow(), game_id)
            )
            conn.commit()
            updated_game = cur.fetchone()
            
            if not updated_game:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game with ID {game_id} not found"
                )
            
            logger.info(f"Published game {game_id}")
            return updated_game


@router.patch("/{game_id}/unpublish", response_model=GameResponse)
async def unpublish_game(game_id: int):
    """
    Unpublish a game (set status to 'draft').
    
    Args:
        game_id: The game ID
    """
    logger.info(f"Unpublishing game {game_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                UPDATE game_catalog
                SET status = 'draft', date_updated = %s
                WHERE id = %s
                RETURNING *
                """,
                (datetime.utcnow(), game_id)
            )
            conn.commit()
            updated_game = cur.fetchone()
            
            if not updated_game:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game with ID {game_id} not found"
                )
            
            logger.info(f"Unpublished game {game_id}")
            return updated_game