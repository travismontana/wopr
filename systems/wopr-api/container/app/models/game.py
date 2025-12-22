#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
Copyright (c) 2025 Bob Bomar <bob@bomar.us>
SPDX-License-Identifier: MIT

Game, piece, and game instance models.
"""

from datetime import datetime
from typing import List
import uuid

from sqlalchemy import DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Game(Base):
    """Game definition/type"""
    __tablename__ = "games"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    game_type: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    ruleset_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    
    piece_definitions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    pieces: Mapped[List["Piece"]] = relationship(
        "Piece",
        back_populates="game",
        cascade="all, delete-orphan"
    )
    instances: Mapped[List["GameInstance"]] = relationship(
        "GameInstance",
        back_populates="game",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Game(id={self.id}, type={self.game_type})>"


class Piece(Base):
    """Game piece definition"""
    __tablename__ = "pieces"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    game_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    piece_type: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    properties: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    expected_image_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="pieces")
    
    def __repr__(self) -> str:
        return f"<Piece(id={self.id}, name={self.name}, type={self.piece_type})>"


class GameInstance(Base):
    """Active game instance"""
    __tablename__ = "game_instances"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    game_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("games.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    
    status: Mapped[str] = mapped_column(String(32), default="setup")
    player_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    player_names: Mapped[List[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    game: Mapped["Game"] = relationship("Game", back_populates="instances")
    states: Mapped[List["GameState"]] = relationship(
        "GameState",
        back_populates="game_instance",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<GameInstance(id={self.id}, status={self.status})>"


class GameState(Base):
    """Game state at a point in time"""
    __tablename__ = "game_states"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    game_instance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("game_instances.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    image_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("images.id", ondelete="SET NULL"),
        nullable=True
    )
    
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    state_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # Human-in-the-loop
    ai_detected_state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    user_confirmed_state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    confirmation_status: Mapped[str] = mapped_column(String(32), default="pending")
    confirmed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    changes_from_previous: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    rule_violations: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    game_instance: Mapped["GameInstance"] = relationship("GameInstance", back_populates="states")
    
    def __repr__(self) -> str:
        return f"<GameState(id={self.id}, round={self.round_number}, status={self.confirmation_status})>"
