#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob <bob@example.com>
# See git log for detailed authorship

WOPR API - pieces CRUD endpoints (Directus schema).
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
logger.debug(f"Using DATABASE_URL: {DATABASE_URL}")

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    try:
        yield conn
    finally:
        conn.close()


class PieceCreate(BaseModel):
    """Model for creating a piece"""
    name: str = Field(..., min_length=1, max_length=255)
    game_uuid: int = Field(..., description="Game ID this piece belongs to")
    status: str = Field(default="draft", pattern="^(draft|published)$")
    user_created: Optional[UUID] = None


class PieceUpdate(BaseModel):
    """Model for updating a piece"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    game_uuid: Optional[int] = None
    status: Optional[str] = Field(None, pattern="^(draft|published)$")
    user_updated: Optional[UUID] = None


class PieceResponse(BaseModel):
    """Model for piece response"""
    id: int
    uuid: UUID
    name: str
    game_uuid: int
    status: str
    user_created: Optional[UUID]
    date_created: datetime
    user_updated: Optional[UUID]
    date_updated: Optional[datetime]


@router.get("", response_model=List[PieceResponse])
async def list_pieces(
    limit: int = 100,
    offset: int = 0,
    game_id: Optional[int] = None,
    status: Optional[str] = None
):
    """
    List all pieces with optional pagination and filtering.
    
    Args:
        limit: Maximum number of results (default 100)
        offset: Number of results to skip (default 0)
        game_id: Optional filter by game ID (direct FK to game_catalog)
        status: Optional filter by status (draft|published)
    """
    logger.debug(f"Listing pieces: limit={limit}, offset={offset}, game_id={game_id}, status={status}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            query = "SELECT * FROM pieces WHERE 1=1"
            params = []
            
            if game_id:
                query += " AND game_uuid = %s"
                params.append(game_id)
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            query += " ORDER BY date_created DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cur.execute(query, params)
            pieces = cur.fetchall()
            return pieces


@router.get("/{piece_id}", response_model=PieceResponse)
async def get_piece(piece_id: int):
    """
    Get a specific piece by ID.
    
    Args:
        piece_id: The piece ID
    """
    logger.debug(f"Getting piece {piece_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "SELECT * FROM pieces WHERE id = %s",
                (piece_id,)
            )
            piece = cur.fetchone()
            
            if not piece:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Piece with ID {piece_id} not found"
                )
            
            return piece


@router.post("", response_model=PieceResponse, status_code=status.HTTP_201_CREATED)
async def create_piece(piece: PieceCreate):
    """
    Create a new piece.
    
    Args:
        piece: Piece data
    """
    logger.info(f"Creating piece: {piece.name}")
    
    # Generate UUID for Directus document tracking
    piece_uuid = uuid4()
    now = datetime.utcnow()
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Verify game exists
            cur.execute("SELECT id FROM game_catalog WHERE id = %s", (piece.game_uuid,))
            if not cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game with ID {piece.game_uuid} not found"
                )
            
            cur.execute(
                """
                INSERT INTO pieces (
                    uuid, name, game_uuid, status, user_created, date_created
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    piece_uuid,
                    piece.name,
                    piece.game_uuid,
                    piece.status,
                    piece.user_created,
                    now
                )
            )
            conn.commit()
            new_piece = cur.fetchone()
            
            logger.info(f"Created piece {new_piece['id']}: {new_piece['name']}")
            return new_piece


@router.put("/{piece_id}", response_model=PieceResponse)
async def update_piece(piece_id: int, piece: PieceUpdate):
    """
    Update an existing piece.
    
    Args:
        piece_id: The piece ID
        piece: Updated piece data
    """
    logger.info(f"Updating piece {piece_id}")
    
    update_fields = []
    values = []
    
    for field, value in piece.dict(exclude_unset=True).items():
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
    values.append(piece_id)
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # If updating game_uuid, verify it exists
            if piece.game_uuid:
                cur.execute("SELECT id FROM game_catalog WHERE id = %s", (piece.game_uuid,))
                if not cur.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Game with ID {piece.game_uuid} not found"
                    )
            
            query = f"""
                UPDATE pieces
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING *
            """
            
            cur.execute(query, values)
            conn.commit()
            updated_piece = cur.fetchone()
            
            if not updated_piece:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Piece with ID {piece_id} not found"
                )
            
            logger.info(f"Updated piece {piece_id}")
            return updated_piece


@router.delete("/{piece_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_piece(piece_id: int):
    """
    Delete a piece.
    
    Args:
        piece_id: The piece ID
    """
    logger.info(f"Deleting piece {piece_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                "DELETE FROM pieces WHERE id = %s RETURNING id",
                (piece_id,)
            )
            conn.commit()
            deleted = cur.fetchone()
            
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Piece with ID {piece_id} not found"
                )
            
            logger.info(f"Deleted piece {piece_id}")


@router.patch("/{piece_id}/publish", response_model=PieceResponse)
async def publish_piece(piece_id: int):
    """
    Publish a piece (set status to 'published').
    
    Args:
        piece_id: The piece ID
    """
    logger.info(f"Publishing piece {piece_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                UPDATE pieces
                SET status = 'published', date_updated = %s
                WHERE id = %s
                RETURNING *
                """,
                (datetime.utcnow(), piece_id)
            )
            conn.commit()
            updated_piece = cur.fetchone()
            
            if not updated_piece:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Piece with ID {piece_id} not found"
                )
            
            logger.info(f"Published piece {piece_id}")
            return updated_piece


@router.patch("/{piece_id}/unpublish", response_model=PieceResponse)
async def unpublish_piece(piece_id: int):
    """
    Unpublish a piece (set status to 'draft').
    
    Args:
        piece_id: The piece ID
    """
    logger.info(f"Unpublishing piece {piece_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                UPDATE pieces
                SET status = 'draft', date_updated = %s
                WHERE id = %s
                RETURNING *
                """,
                (datetime.utcnow(), piece_id)
            )
            conn.commit()
            updated_piece = cur.fetchone()
            
            if not updated_piece:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Piece with ID {piece_id} not found"
                )
            
            logger.info(f"Unpublished piece {piece_id}")
            return updated_piece