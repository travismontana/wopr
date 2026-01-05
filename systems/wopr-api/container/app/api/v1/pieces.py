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