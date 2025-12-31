#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob <bob@example.com>
# See git log for detailed authorship

WOPR API - games_catalog CRUD endpoints.
"""

from wopr import logging as woprlogging
from app import globals as woprvar

import logging
import sys
from typing import Optional, List
from datetime import datetime
from contextlib import contextmanager

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import psycopg
from psycopg.rows import dict_row

logger = logging.getLogger(woprvar.APP_NAME)
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
router = APIRouter()

# Database connection - adjust to match your actual connection string
DATABASE_URL = woprvar.DATABASE_URL  # Assumes you have this in globals
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
    document_id: Optional[str] = None
    uid: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    min_players: Optional[int] = Field(None, ge=1)
    max_players: Optional[int] = Field(None, ge=1)
    locale: Optional[str] = Field(None, max_length=255)


class GameUpdate(BaseModel):
    """Model for updating a game"""
    document_id: Optional[str] = None
    uid: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    min_players: Optional[int] = Field(None, ge=1)
    max_players: Optional[int] = Field(None, ge=1)
    locale: Optional[str] = Field(None, max_length=255)
    published_at: Optional[datetime] = None


class GameResponse(BaseModel):
    """Model for game response"""
    id: int
    document_id: Optional[str]
    uid: Optional[str]
    name: Optional[str]
    description: Optional[str]
    min_players: Optional[int]
    max_players: Optional[int]
    create_time: Optional[datetime]
    update_time: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    created_by_id: Optional[int]
    updated_by_id: Optional[int]
    locale: Optional[str]


@router.get("", response_model=List[GameResponse])
async def list_games_catalog(
    limit: int = 100,
    offset: int = 0,
    locale: Optional[str] = None
):
    """
    List all games_catalog with optional pagination and locale filtering.
    
    Args:
        limit: Maximum number of results (default 100)
        offset: Number of results to skip (default 0)
        locale: Optional locale filter
    """
    logger.debug(f"Listing games_catalog: limit={limit}, offset={offset}, locale={locale}")
    
    with get_db() as conn:
        logger.debug("opened DB connection for listing games_catalog")
        with conn.cursor(row_factory=dict_row) as cur:
            logger.debug("created DB cursor for listing games_catalog")
            if locale:
                logger.debug(f"Filtering games_catalog by locale: {locale}")
                cur.execute(
                    """
                    SELECT * FROM games_catalog
                    WHERE locale = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (locale, limit, offset)
                )
            else:
                logger.debug("No locale filter applied")
                cur.execute(
                    """
                    SELECT * FROM games_catalog_catalog
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset)
                )
            
            games_catalog = cur.fetchall()
            logger.debug(f"Fetched {len(games_catalog)} games_catalog from DB")
            return games_catalog


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
                "SELECT * FROM games_catalog WHERE id = %s",
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
    logger.debug(f"Create payload: {game.dict(exclude_none=True)}")
    
    now = datetime.utcnow()
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO games_catalog (
                    document_id, uid, name, description,
                    min_players, max_players, locale,
                    create_time, update_time, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    game.document_id,
                    game.uid,
                    game.name,
                    game.description,
                    game.min_players,
                    game.max_players,
                    game.locale,
                    now,
                    now,
                    now,
                    now
                )
            )
            conn.commit()
            new_game = cur.fetchone()
            logger.debug(f"Inserted game row: {new_game}")
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
    
    # Build dynamic update query based on provided fields
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
    
    # Always update update_time and updated_at
    update_fields.append("update_time = %s")
    update_fields.append("updated_at = %s")
    now = datetime.utcnow()
    values.extend([now, now])
    values.append(game_id)
    
    logger.debug(f"Update fields: {update_fields} | values (pre-query): {values}")
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            query = f"""
                UPDATE games_catalog
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING *
            """
            logger.debug(f"Executing update query: {query}")
            cur.execute(query, values)
            conn.commit()
            updated_game = cur.fetchone()
            
            if not updated_game:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game with ID {game_id} not found"
                )
            logger.debug(f"Updated game row: {updated_game}")
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
                "DELETE FROM games_catalog WHERE id = %s RETURNING id",
                (game_id,)
            )
            conn.commit()
            deleted = cur.fetchone()
            logger.debug(f"Delete result for {game_id}: {deleted}")
            if not deleted:
                logger.debug(f"Game {game_id} not found when attempting delete")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game with ID {game_id} not found"
                )

            logger.info(f"Deleted game {game_id}")
