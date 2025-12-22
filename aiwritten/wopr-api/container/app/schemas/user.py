#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
Copyright (c) 2025 Bob Bomar <bob@bomar.us>
SPDX-License-Identifier: MIT

User and authentication Pydantic schemas.
"""

from datetime import datetime
from uuid import UUID
from typing import List

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update schema"""
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8)
    role: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    """User response schema"""
    id: UUID
    role: str
    created_at: datetime
    last_login: datetime | None
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class LoginRequest(BaseModel):
    """Login request"""
    username: str
    password: str


class ApiKeyCreate(BaseModel):
    """API key creation"""
    name: str = Field(..., min_length=1, max_length=128)
    scopes: List[str] | None = None
    expires_days: int | None = None


class ApiKeyResponse(BaseModel):
    """API key response"""
    id: UUID
    name: str
    scopes: List[str] | None
    created_at: datetime
    expires_at: datetime | None
    last_used: datetime | None
    is_active: bool
    
    # Only returned on creation
    key: str | None = None
    
    model_config = ConfigDict(from_attributes=True)
