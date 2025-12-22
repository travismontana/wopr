#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
Copyright (c) 2025 Bob Bomar <bob@bomar.us>
SPDX-License-Identifier: MIT

Camera endpoints.
"""

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.database import get_db
from app.models.camera import Camera
from app.models.image import Image
from app.schemas.camera import (
    CameraCreate,
    CameraUpdate,
    CameraResponse,
    CameraHeartbeat,
    CaptureRequest,
    CaptureResponse
)
from app.dependencies import get_current_user
from app.models.user import User
from app.config import settings

# Import wopr-core for storage
try:
    import wopr
    WOPR_CORE_AVAILABLE = True
except ImportError:
    WOPR_CORE_AVAILABLE = False

router = APIRouter()


@router.get("", response_model=list[CameraResponse])
async def list_cameras(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """List all cameras"""
    result = await db.execute(select(Camera))
    cameras = result.scalars().all()
    return [CameraResponse.model_validate(cam) for cam in cameras]


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera_data: CameraCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Register new camera"""
    # Check if device_id exists
    result = await db.execute(
        select(Camera).where(Camera.device_id == camera_data.device_id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera with this device_id already exists"
        )
    
    camera = Camera(
        name=camera_data.name,
        device_id=camera_data.device_id,
        service_url=camera_data.service_url,
        capabilities=camera_data.capabilities,
        mdata=camera_data.mdata,
        status="offline"
    )
    
    db.add(camera)
    await db.commit()
    await db.refresh(camera)
    
    return CameraResponse.model_validate(camera)


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Get camera details"""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    return CameraResponse.model_validate(camera)


@router.post("/{camera_id}/heartbeat")
async def camera_heartbeat(
    camera_id: UUID,
    heartbeat_data: CameraHeartbeat,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Camera heartbeat - updates status and last_heartbeat.
    
    Can be called without authentication (for edge devices).
    """
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    camera.status = heartbeat_data.status
    camera.last_heartbeat = datetime.utcnow()
    if heartbeat_data.mdata:
        camera.mdata = heartbeat_data.mdata
    
    await db.commit()
    
    return {"status": "ok", "timestamp": datetime.utcnow()}


@router.post("/{camera_id}/capture", response_model=CaptureResponse)
async def trigger_capture(
    camera_id: UUID,
    capture_data: CaptureRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Trigger camera capture.
    
    Calls wopr-cam service, saves image mdata to database.
    """
    # Get camera
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found"
        )
    
    # Call wopr-cam service
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{camera.service_url}/capture",
                json={
                    "game_id": str(capture_data.game_instance_id) if capture_data.game_instance_id else None,
                    "subject": capture_data.subject
                }
            )
            response.raise_for_status()
            cam_response = response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to capture from camera: {str(e)}"
        )
    
    # Create image record
    image = Image(
        filename=cam_response.get("filename"),
        file_path=cam_response.get("filepath"),
        subject=capture_data.subject,
        camera_id=camera_id,
        game_instance_id=capture_data.game_instance_id,
        captured_by=current_user.id,
        mdata=capture_data.mdata,
        analysis_status="pending"
    )
    
    db.add(image)
    await db.commit()
    await db.refresh(image)
    
    return CaptureResponse(
        image_id=image.id,
        filename=image.filename,
        file_path=image.file_path,
        captured_at=image.created_at
    )
