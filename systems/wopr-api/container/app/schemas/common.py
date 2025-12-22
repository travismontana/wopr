#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
Copyright (c) 2025 Bob Bomar <bob@bomar.us>
SPDX-License-Identifier: MIT

Common Pydantic schemas.
"""

from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common config"""
    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str = "0.1.0"


class ReadyResponse(BaseModel):
    """Readiness check response"""
    ready: bool
    database: str
    config_service: str
    redis: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: str | None = None
    timestamp: datetime


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str
    timestamp: datetime = datetime.utcnow()
