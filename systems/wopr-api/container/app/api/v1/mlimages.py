#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob <bob@example.com>
# See git log for detailed authorship

WOPR API - ML image metadata CRUD endpoints (Directus schema).
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
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


class MLImageCreate(BaseModel):
    """Model for creating ML image metadata"""
    filename: str = Field(..., min_length=1, max_length=255)
    object_rotation: int = Field(default=0)
    object_position: int = Field(None, max_length=255)
    color_temp: Optional[str] = Field(None, max_length=255)
    light_intensity: Optional[int] = None
    game_uuid: Optional[int] = None
    piece_id: Optional[int] = None
    status: str = Field(default="draft", pattern="^(draft|published)$")
    user_created: Optional[UUID] = None


class MLImageUpdate(BaseModel):
    """Model for updating ML image metadata"""
    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    object_rotation: Optional[int] = None
    object_position: Optional[int] = None
    color_temp: Optional[str] = Field(None, max_length=255)
    light_intensity: Optional[int] = None
    game_uuid: Optional[int] = None
    piece_id: Optional[int] = None
    status: Optional[str] = Field(None, pattern="^(draft|published)$")
    user_updated: Optional[UUID] = None


class MLImageResponse(BaseModel):
    """Model for ML image metadata response"""
    id: int
    uuid: UUID
    filename: Optional[str]
    object_rotation: Optional[int]
    object_position: Optional[int]
    color_temp: Optional[str]
    light_intensity: Optional[int]
    game_uuid: Optional[int]
    piece_id: Optional[int]
    status: str
    user_created: Optional[UUID]
    date_created: datetime
    user_updated: Optional[UUID]
    date_updated: Optional[datetime]


@router.get("", response_model=List[MLImageResponse])
async def list_mlimages(
    limit: int = 100,
    offset: int = 0,
    game_id: Optional[int] = None,
    piece_id: Optional[int] = None,
    status: Optional[str] = None
):
    """
    List all ML image metadata with optional pagination and filtering.
    
    Args:
        limit: Maximum number of results (default 100)
        offset: Number of results to skip (default 0)
        game_id: Optional filter by game ID (direct FK to game_catalog)
        piece_id: Optional filter by piece ID (direct FK to pieces)
        status: Optional filter by status (draft|published)
    """
    logger.debug(f"Listing ML images: limit={limit}, offset={offset}, game_id={game_id}, piece_id={piece_id}, status={status}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            query = "SELECT * FROM ml_image_metadata WHERE 1=1"
            params = []
            
            if game_id:
                query += " AND game_uuid = %s"
                params.append(game_id)
            
            if piece_id:
                query += " AND piece_id = %s"
                params.append(piece_id)
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            query += " ORDER BY date_created DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            logger.debug(f"Executing query: {query} with params: {params}")
            cur.execute(query, params)
            mlimages = cur.fetchall()
            logger.debug(f"Found {len(mlimages)} ML images")
            return mlimages


@router.get("/{mlimage_id}", response_model=MLImageResponse)
async def get_mlimage(mlimage_id: int):
    """
    Get a specific ML image metadata by ID.
    
    Args:
        mlimage_id: The ML image metadata ID
    """
    logger.debug(f"Getting ML image {mlimage_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT * FROM ml_image_metadata WHERE id = %s",
                (mlimage_id,)
            )
            mlimage = cur.fetchone()
            
            if not mlimage:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ML image metadata with ID {mlimage_id} not found"
                )
            
            return mlimage


@router.post("", response_model=MLImageResponse, status_code=status.HTTP_201_CREATED)
async def create_mlimage(mlimage: MLImageCreate):
    """
    Create new ML image metadata.
    
    Args:
        mlimage: ML image metadata
    """
    logger.info(f"Creating ML image metadata: {mlimage.filename}")
    
    # Generate UUID for Directus document tracking
    mlimage_uuid = uuid4()
    now = datetime.utcnow()
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Verify game exists if provided
            if mlimage.game_uuid:
                cur.execute("SELECT id FROM game_catalog WHERE id = %s", (mlimage.game_uuid,))
                if not cur.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Game with ID {mlimage.game_uuid} not found"
                    )
            
            # Verify piece exists if provided
            if mlimage.piece_id:
                cur.execute("SELECT id FROM pieces WHERE id = %s", (mlimage.piece_id,))
                if not cur.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Piece with ID {mlimage.piece_id} not found"
                    )
            
            cur.execute(
                """
                INSERT INTO ml_image_metadata (
                    uuid, filename, object_rotation, object_position,
                    color_temp, light_intensity, game_uuid, piece_id,
                    status, user_created, date_created
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    mlimage_uuid,
                    mlimage.filename,
                    mlimage.object_rotation,
                    mlimage.object_position,
                    mlimage.color_temp,
                    mlimage.light_intensity,
                    mlimage.game_uuid,
                    mlimage.piece_id,
                    mlimage.status,
                    mlimage.user_created,
                    now
                )
            )
            conn.commit()
            new_mlimage = cur.fetchone()
            
            logger.info(f"Created ML image metadata {new_mlimage['id']}: {new_mlimage['filename']}")
            return new_mlimage


@router.put("/{mlimage_id}", response_model=MLImageResponse)
async def update_mlimage(mlimage_id: int, mlimage: MLImageUpdate):
    """
    Update existing ML image metadata.
    
    Args:
        mlimage_id: The ML image metadata ID
        mlimage: Updated ML image metadata
    """
    logger.info(f"Updating ML image metadata {mlimage_id}")
    
    update_fields = []
    values = []
    
    for field, value in mlimage.dict(exclude_unset=True).items():
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
    values.append(mlimage_id)
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Verify game exists if updating game_uuid
            if mlimage.game_uuid:
                cur.execute("SELECT id FROM game_catalog WHERE id = %s", (mlimage.game_uuid,))
                if not cur.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Game with ID {mlimage.game_uuid} not found"
                    )
            
            # Verify piece exists if updating piece_id
            if mlimage.piece_id:
                cur.execute("SELECT id FROM pieces WHERE id = %s", (mlimage.piece_id,))
                if not cur.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Piece with ID {mlimage.piece_id} not found"
                    )
            
            query = f"""
                UPDATE ml_image_metadata
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING *
            """
            
            cur.execute(query, values)
            conn.commit()
            updated_mlimage = cur.fetchone()
            
            if not updated_mlimage:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ML image metadata with ID {mlimage_id} not found"
                )
            
            logger.info(f"Updated ML image metadata {mlimage_id}")
            return updated_mlimage


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
                "DELETE FROM ml_image_metadata WHERE id = %s RETURNING id",
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


@router.patch("/{mlimage_id}/publish", response_model=MLImageResponse)
async def publish_mlimage(mlimage_id: int):
    """
    Publish ML image metadata (set status to 'published').
    
    Args:
        mlimage_id: The ML image metadata ID
    """
    logger.info(f"Publishing ML image metadata {mlimage_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                UPDATE ml_image_metadata
                SET status = 'published', date_updated = %s
                WHERE id = %s
                RETURNING *
                """,
                (datetime.utcnow(), mlimage_id)
            )
            conn.commit()
            updated_mlimage = cur.fetchone()
            
            if not updated_mlimage:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ML image metadata with ID {mlimage_id} not found"
                )
            
            logger.info(f"Published ML image metadata {mlimage_id}")
            return updated_mlimage


@router.patch("/{mlimage_id}/unpublish", response_model=MLImageResponse)
async def unpublish_mlimage(mlimage_id: int):
    """
    Unpublish ML image metadata (set status to 'draft').
    
    Args:
        mlimage_id: The ML image metadata ID
    """
    logger.info(f"Unpublishing ML image metadata {mlimage_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                UPDATE ml_image_metadata
                SET status = 'draft', date_updated = %s
                WHERE id = %s
                RETURNING *
                """,
                (datetime.utcnow(), mlimage_id)
            )
            conn.commit()
            updated_mlimage = cur.fetchone()
            
            if not updated_mlimage:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ML image metadata with ID {mlimage_id} not found"
                )
            
            logger.info(f"Unpublished ML image metadata {mlimage_id}")
            return updated_mlimage