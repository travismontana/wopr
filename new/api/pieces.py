#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob <bob@example.com>
# See git log for detailed authorship

WOPR API - pieces CRUD endpoints.
"""

from wopr import logging as woprlogging
from app import globals as woprvar

import logging
from typing import Optional, List
from datetime import datetime
from contextlib import contextmanager

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import psycopg
from psycopg.rows import dict_row

logger = woprlogging.setup_logging(woprvar.APP_NAME)

router = APIRouter()

DATABASE_URL = woprvar.DATABASE_URL


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
    document_id: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=255)
    uid: Optional[str] = None
    description: Optional[str] = None
    locale: Optional[str] = Field(None, max_length=255)


class PieceUpdate(BaseModel):
    """Model for updating a piece"""
    document_id: Optional[str] = None
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    uid: Optional[str] = None
    description: Optional[str] = None
    locale: Optional[str] = Field(None, max_length=255)
    published_at: Optional[datetime] = None


class PieceResponse(BaseModel):
    """Model for piece response"""
    id: int
    document_id: Optional[str]
    name: Optional[str]
    uid: Optional[str]
    create_time: Optional[datetime]
    update_time: Optional[datetime]
    description: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    created_by_id: Optional[int]
    updated_by_id: Optional[int]
    locale: Optional[str]


@router.get("", response_model=List[PieceResponse])
async def list_pieces(
    limit: int = 100,
    offset: int = 0,
    locale: Optional[str] = None,
    game_id: Optional[int] = None
):
    """
    List all pieces with optional pagination, locale, and game filtering.
    
    Args:
        limit: Maximum number of results (default 100)
        offset: Number of results to skip (default 0)
        locale: Optional locale filter
        game_id: Optional filter by game ID (via pieces_game_lnk)
    """
    logger.debug(f"Listing pieces: limit={limit}, offset={offset}, locale={locale}, game_id={game_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            if game_id:
                # Filter by game via junction table
                query = """
                    SELECT p.* FROM pieces p
                    INNER JOIN pieces_game_lnk pgl ON p.id = pgl.piece_id
                    WHERE pgl.game_id = %s
                """
                params = [game_id]
                
                if locale:
                    query += " AND p.locale = %s"
                    params.append(locale)
                
                query += " ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cur.execute(query, params)
            elif locale:
                cur.execute(
                    """
                    SELECT * FROM pieces
                    WHERE locale = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (locale, limit, offset)
                )
            else:
                cur.execute(
                    """
                    SELECT * FROM pieces
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset)
                )
            
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
    
    now = datetime.utcnow()
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO pieces (
                    document_id, name, uid, description, locale,
                    create_time, update_time, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    piece.document_id,
                    piece.name,
                    piece.uid,
                    piece.description,
                    piece.locale,
                    now,
                    now,
                    now,
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
    
    update_fields.append("update_time = %s")
    update_fields.append("updated_at = %s")
    now = datetime.utcnow()
    values.extend([now, now])
    values.append(piece_id)
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
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


@router.post("/{piece_id}/games/{game_id}", status_code=status.HTTP_201_CREATED)
async def link_piece_to_game(piece_id: int, game_id: int):
    """
    Link a piece to a game via pieces_game_lnk junction table.
    
    Args:
        piece_id: The piece ID
        game_id: The game ID
    """
    logger.info(f"Linking piece {piece_id} to game {game_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Verify piece exists
            cur.execute("SELECT id FROM pieces WHERE id = %s", (piece_id,))
            if not cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Piece with ID {piece_id} not found"
                )
            
            # Verify game exists
            cur.execute("SELECT id FROM games WHERE id = %s", (game_id,))
            if not cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Game with ID {game_id} not found"
                )
            
            # Create link (assuming pieces_game_lnk has piece_id, game_id columns)
            try:
                cur.execute(
                    """
                    INSERT INTO pieces_game_lnk (piece_id, game_id)
                    VALUES (%s, %s)
                    """,
                    (piece_id, game_id)
                )
                conn.commit()
                logger.info(f"Linked piece {piece_id} to game {game_id}")
                return {"piece_id": piece_id, "game_id": game_id, "status": "linked"}
            except psycopg.errors.UniqueViolation:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Piece {piece_id} is already linked to game {game_id}"
                )


@router.delete("/{piece_id}/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_piece_from_game(piece_id: int, game_id: int):
    """
    Unlink a piece from a game.
    
    Args:
        piece_id: The piece ID
        game_id: The game ID
    """
    logger.info(f"Unlinking piece {piece_id} from game {game_id}")
    
    with get_db() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                DELETE FROM pieces_game_lnk
                WHERE piece_id = %s AND game_id = %s
                RETURNING piece_id
                """,
                (piece_id, game_id)
            )
            conn.commit()
            deleted = cur.fetchone()
            
            if not deleted:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Link between piece {piece_id} and game {game_id} not found"
                )
            
            logger.info(f"Unlinked piece {piece_id} from game {game_id}")
