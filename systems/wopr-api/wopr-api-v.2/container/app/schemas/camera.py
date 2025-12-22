#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
Copyright (c) 2025 Bob Bomar <bob@bomar.us>
SPDX-License-Identifier: MIT

Camera Pydantic schemas.
"""

from datetime import datetime
from uuid import UUID
from typing import Dict, Any

from pydantic import BaseModel, Field, ConfigDict, HttpUrl


class CameraBase(BaseModel):
    """Base camera schema"""
    name: str = Field(..., min_length=1, max_length=128)
    device_id: str = Field(..., min_length=1, max_length=64)
    service_url: str


class CameraCreate(CameraBase):
    """Camera creation schema"""
    capabilities: Dict[str, Any] | None = None
    metadata: Dict[str, Any] | None = None


class CameraUpdate(BaseModel):
    """Camera update schema"""
    name: str | None = None
    service_url: str | None = None
    status: str | None = None
    capabilities: Dict[str, Any] | None = None
    metadata: Dict[str, Any] | None = None


class CameraResponse(CameraBase):
    """Camera response schema"""
    id: UUID
    status: str
    capabilities: Dict[str, Any] | None
    metadata: Dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
    last_heartbeat: datetime | None
    
    model_config = ConfigDict(from_attributes=True)


class CameraHeartbeat(BaseModel):
    """Camera heartbeat request"""
    status: str
    metadata: Dict[str, Any] | None = None


class CaptureRequest(BaseModel):
    """Camera capture request"""
    game_instance_id: UUID | None = None
    subject: str = "capture"
    metadata: Dict[str, Any] | None = None


class CaptureResponse(BaseModel):
    """Camera capture response"""
    image_id: UUID
    filename: str
    file_path: str
    captured_at: datetime
