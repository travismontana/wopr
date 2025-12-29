#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob <bob@example.com>
# See git log for detailed authorship

WOPR API - ml_image_metadatas CRUD endpoints.
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

DATABASE_URL = woprvar.DATABASE_URL
logger.debug(f"Using database URL: {DATABASE_URL}")

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


class MLImageCreate(BaseModel):
    """Model for creating ML image metadata"""
    document_id: Optional[str] = None
    filename: str = Field(..., min_length=1, max_length=255)
    uid: Optional[str] = None
    object_rotation: Optional[int] = None
    object_position: Optional[str] = Field(None, max_length=255)
    color_temp: Optional[str] = Field(None, max_length=255)
    light_intensity: Optional[str] = Field(None, max_length=255)
    locale: Optional[str] = Field(None, max_length=255)
    game_id: Optional[int] = None
    piece_id: Optional[int] = None


class MLImageUpdate(BaseModel):
    """Model for updating ML image metadata"""
    document_id: Optional[str] = None
    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    uid: Optional[str] = None
    object_rotation: Optional[int] = None
    object_position: Optional[str] = Field(None, max_length=255)
    color_temp: Optional[str] = Field(None, max_length=255)
    light_intensity: Optional[str] = Field(None, max_length=255)
    locale: Optional[str] = Field(None, max_length=255)
    published_at: Optional[datetime] = None


class MLImageResponse(BaseModel):
    """Model for ML image metadata response"""
    id: int
    document_id: Optional[str]
    filename: Optional[str]
    uid: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]
    object_rotation: Optional[int]
    object_position: Optional[str]
    color_temp: Optional[str]
    light_intensity: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    created_by_id: Optional[int]
    updated_by_id: Optional[int]
    locale: Optional[str]


@router.get("", response_model=List[MLImageResponse])
async def list_mlimages(
    limit: int = 100,
    offset: int = 0,
    locale: Optional[str] = None,
    game_id: Optional[int] = None,
    piece_id: Optional[int] = None
):
    """
    List all ML image metadata with optional pagination and filtering.
    
    Args:
        limit: Maximum number of results (default 100)
        offset: Number of results to skip (default 0)
        locale: Optional locale filter
        game_id: Optional filter by game ID
        piece_id: Optional filter by piece ID
    """
    logger.debug(f"Listing ML images: limit={limit}, offset={offset}, locale={locale}, game_id={game_id}, piece_id={piece_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            if game_id and piece_id:
                # Filter by both game and piece
                query = """
                    SELECT DISTINCT m.* FROM ml_image_metadatas m
                    INNER JOIN ml_image_metadatas_game_lnk mg ON m.id = mg.ml_image_metadata_id
                    INNER JOIN ml_image_metadatas_piece_lnk mp ON m.id = mp.ml_image_metadata_id
                    WHERE mg.game_id = %s AND mp.piece_id = %s
                """
                params = [game_id, piece_id]
                
                if locale:
                    query += " AND m.locale = %s"
                    params.append(locale)
                
                query += " ORDER BY m.created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cur.execute(query, params)
            elif game_id:
                # Filter by game only
                query = """
                    SELECT m.* FROM ml_image_metadatas m
                    INNER JOIN ml_image_metadatas_game_lnk mg ON m.id = mg.ml_image_metadata_id
                    WHERE mg.game_id = %s
                """
                params = [game_id]
                
                if locale:
                    query += " AND m.locale = %s"
                    params.append(locale)
                
                query += " ORDER BY m.created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cur.execute(query, params)
            elif piece_id:
                # Filter by piece only
                query = """
                    SELECT m.* FROM ml_image_metadatas m
                    INNER JOIN ml_image_metadatas_piece_lnk mp ON m.id = mp.ml_image_metadata_id
                    WHERE mp.piece_id = %s
                """
                params = [piece_id]
                
                if locale:
                    query += " AND m.locale = %s"
                    params.append(locale)
                
                query += " ORDER BY m.created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cur.execute(query, params)
            elif locale:
                cur.execute(
                    """
                    SELECT * FROM ml_image_metadatas
                    WHERE locale = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (locale, limit, offset)
                )
            else:
                cur.execute(
                    """
                    SELECT * FROM ml_image_metadatas
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset)
                )
            
            images = cur.fetchall()
            return images


@router.get("/{mlimage_id}", response_model=MLImageResponse)
async def get_mlimage(mlimage_id: int):
    """
    Get specific ML image metadata by ID.
    
    Args:
        mlimage_id: The ML image metadata ID
    """
    logger.debug(f"Getting ML image {mlimage_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT * FROM ml_image_metadatas WHERE id = %s",
                (mlimage_id,)
            )
            image = cur.fetchone()
            
            if not image:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ML image metadata with ID {mlimage_id} not found"
                )
            
            return image


@router.post("", response_model=MLImageResponse, status_code=status.HTTP_201_CREATED)
async def create_mlimage(image: MLImageCreate):
    """
    Create new ML image metadata.
    
    Args:
        image: ML image metadata
    """
    logger.info(f"Creating ML image metadata: {image.filename}")
    
    now = datetime.utcnow()
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO ml_image_metadatas (
                    document_id, filename, uid,
                    object_rotation, object_position,
                    color_temp, light_intensity, locale, game_id, piece_id,
                    create_time, update_time, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    image.document_id,
                    image.filename,
                    image.uid,
                    image.object_rotation,
                    image.object_position,
                    image.color_temp,
                    image.light_intensity,
                    image.locale,
                    image.game_id,
                    image.piece_id,
                    now,
                    now,
                    now,
                    now
                )
            )
            conn.commit()
            new_image = cur.fetchone()
            
            logger.info(f"Created ML image metadata {new_image['id']}: {new_image['filename']}")
            return new_image


@router.put("/{mlimage_id}", response_model=MLImageResponse)
async def update_mlimage(mlimage_id: int, image: MLImageUpdate):
    """
    Update existing ML image metadata.
    
    Args:
        mlimage_id: The ML image metadata ID
        image: Updated ML image metadata
    """
    logger.info(f"Updating ML image metadata {mlimage_id}")
    
    update_fields = []
    values = []
    
    for field, value in image.dict(exclude_unset=True).items():
        if value is not None:
            update_fields.append(f"{field} = %s")
            values.append(value)
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    update_fields.append("update_time = %s")
    update_fields.append("updated_at = %s")
    now = datetime.utcnow()
    values.extend([now, now])
    values.append(mlimage_id)
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            query = f"""
                UPDATE ml_image_metadatas
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING *
            """
            
            cur.execute(query, values)
            conn.commit()
            updated_image = cur.fetchone()
            
            if not updated_image:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ML image metadata with ID {mlimage_id} not found"
                )
            
            logger.info(f"Updated ML image metadata {mlimage_id}")
            return updated_image


@router.delete("/{mlimage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mlimage(mlimage_id: int):
    """
    Delete ML image metadata.
    
    Args:
        mlimage_id: The ML image metadata ID
    """
    logger.info(f"Deleting ML image metadata {mlimage_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "DELETE FROM ml_image_metadatas WHERE id = %s RETURNING id",
                (mlimage_id,)
            )
            conn.commit()
            deleted = cur.fetchone()
            
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ML image metadata with ID {mlimage_id} not found"
                )
            
            logger.info(f"Deleted ML image metadata {mlimage_id}")


@router.post("/{mlimage_id}/games/{game_id}", status_code=status.HTTP_201_CREATED)
async def link_mlimage_to_game(mlimage_id: int, game_id: int):
    """
    Link ML image metadata to a game.
    
    Args:
        mlimage_id: The ML image metadata ID
        game_id: The game ID
    """
    logger.info(f"Linking ML image {mlimage_id} to game {game_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Verify ML image exists
            cur.execute("SELECT id FROM ml_image_metadatas WHERE id = %s", (mlimage_id,))
            if not cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ML image metadata with ID {mlimage_id} not found"
                )
            
            # Verify game exists
            cur.execute("SELECT id FROM games WHERE id = %s", (game_id,))
            if not cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game with ID {game_id} not found"
                )
            
            # Create link
            try:
                cur.execute(
                    """
                    INSERT INTO ml_image_metadatas_game_lnk (ml_image_metadata_id, game_id)
                    VALUES (%s, %s)
                    """,
                    (mlimage_id, game_id)
                )
                conn.commit()
                logger.info(f"Linked ML image {mlimage_id} to game {game_id}")
                return {"mlimage_id": mlimage_id, "game_id": game_id, "status": "linked"}
            except psycopg.errors.UniqueViolation:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"ML image {mlimage_id} is already linked to game {game_id}"
                )


@router.delete("/{mlimage_id}/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_mlimage_from_game(mlimage_id: int, game_id: int):
    """
    Unlink ML image metadata from a game.
    
    Args:
        mlimage_id: The ML image metadata ID
        game_id: The game ID
    """
    logger.info(f"Unlinking ML image {mlimage_id} from game {game_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                DELETE FROM ml_image_metadatas_game_lnk
                WHERE ml_image_metadata_id = %s AND game_id = %s
                RETURNING ml_image_metadata_id
                """,
                (mlimage_id, game_id)
            )
            conn.commit()
            deleted = cur.fetchone()
            
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Link between ML image {mlimage_id} and game {game_id} not found"
                )
            
            logger.info(f"Unlinked ML image {mlimage_id} from game {game_id}")


@router.post("/{mlimage_id}/pieces/{piece_id}", status_code=status.HTTP_201_CREATED)
async def link_mlimage_to_piece(mlimage_id: int, piece_id: int):
    """
    Link ML image metadata to a piece.
    
    Args:
        mlimage_id: The ML image metadata ID
        piece_id: The piece ID
    """
    logger.info(f"Linking ML image {mlimage_id} to piece {piece_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Verify ML image exists
            cur.execute("SELECT id FROM ml_image_metadatas WHERE id = %s", (mlimage_id,))
            if not cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ML image metadata with ID {mlimage_id} not found"
                )
            
            # Verify piece exists
            cur.execute("SELECT id FROM pieces WHERE id = %s", (piece_id,))
            if not cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Piece with ID {piece_id} not found"
                )
            
            # Create link
            try:
                cur.execute(
                    """
                    INSERT INTO ml_image_metadatas_piece_lnk (ml_image_metadata_id, piece_id)
                    VALUES (%s, %s)
                    """,
                    (mlimage_id, piece_id)
                )
                conn.commit()
                logger.info(f"Linked ML image {mlimage_id} to piece {piece_id}")
                return {"mlimage_id": mlimage_id, "piece_id": piece_id, "status": "linked"}
            except psycopg.errors.UniqueViolation:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"ML image {mlimage_id} is already linked to piece {piece_id}"
                )


@router.delete("/{mlimage_id}/pieces/{piece_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_mlimage_from_piece(mlimage_id: int, piece_id: int):
    """
    Unlink ML image metadata from a piece.
    
    Args:
        mlimage_id: The ML image metadata ID
        piece_id: The piece ID
    """
    logger.info(f"Unlinking ML image {mlimage_id} from piece {piece_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                DELETE FROM ml_image_metadatas_piece_lnk
                WHERE ml_image_metadata_id = %s AND piece_id = %s
                RETURNING ml_image_metadata_id
                """,
                (mlimage_id, piece_id)
            )
            conn.commit()
            deleted = cur.fetchone()
            
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Link between ML image {mlimage_id} and piece {piece_id} not found"
                )
            
            logger.info(f"Unlinked ML image {mlimage_id} from piece {piece_id}")
