#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
Copyright (c) 2025 Bob Bomar <bob@bomar.us>
SPDX-License-Identifier: MIT

Camera and capture session models.
"""

from datetime import datetime
from typing import List
import uuid

from sqlalchemy import DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Camera(Base):
    """Camera device"""
    __tablename__ = "cameras"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    device_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    service_url: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="offline")
    
    capabilities: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    last_heartbeat: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    sessions: Mapped[List["CameraSession"]] = relationship(
        "CameraSession",
        back_populates="camera",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Camera(id={self.id}, name={self.name}, status={self.status})>"


class CameraSession(Base):
    """Camera capture session"""
    __tablename__ = "camera_sessions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    game_instance_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("game_instances.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="active")
    capture_count: Mapped[int] = mapped_column(Integer, default=0)
    metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    # Relationships
    camera: Mapped["Camera"] = relationship("Camera", back_populates="sessions")
    
    def __repr__(self) -> str:
        return f"<CameraSession(id={self.id}, status={self.status}, captures={self.capture_count})>"
