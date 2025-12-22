#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
Copyright (c) 2025 Bob Bomar <bob@bomar.us>
SPDX-License-Identifier: MIT

Image and ML training models.
"""

from datetime import datetime
from typing import List
import uuid

from sqlalchemy import Boolean, BigInteger, DateTime, Integer, String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Image(Base):
    """Captured image"""
    __tablename__ = "images"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Context
    game_instance_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("game_instances.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    camera_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cameras.id", ondelete="SET NULL"),
        nullable=True
    )
    camera_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("camera_sessions.id", ondelete="SET NULL"),
        nullable=True
    )
    captured_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    
    # Image metadata
    subject: Mapped[str | None] = mapped_column(String(64), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    format: Mapped[str | None] = mapped_column(String(16), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    
    # Processing
    analysis_status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    analysis_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    analysis_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    analysis_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # ML training
    is_training_data: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    training_labels: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    augmented_from: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("images.id"),
        nullable=True
    )
    
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        return f"<Image(id={self.id}, filename={self.filename}, status={self.analysis_status})>"


class PieceImage(Base):
    """Junction table: piece <-> training images"""
    __tablename__ = "piece_images"
    __table_args__ = (
        UniqueConstraint('piece_id', 'image_id', name='uq_piece_image'),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    piece_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pieces.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    image_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("images.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Training metadata
    rotation_angle: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_context: Mapped[str | None] = mapped_column(String(64), nullable=True)
    lighting_condition: Mapped[str | None] = mapped_column(String(64), nullable=True)
    occlusion_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    
    # Bounding box
    bbox_x: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bbox_y: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bbox_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bbox_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    annotations: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<PieceImage(piece_id={self.piece_id}, image_id={self.image_id})>"
