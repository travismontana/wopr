#!/usr/bin/env python3
# Copyright 2026 Bob Bomar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
WOPR Vision Service - Label Studio API Integration
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import httpx
import os
import logging
import sys
from opentelemetry import trace
from contextlib import nullcontext
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

router = APIRouter(tags=["vision"])

# Get tracer (if tracing enabled)
try:
    from app import globals as woprvar
    tracer = trace.get_tracer(woprvar.APP_NAME, woprvar.APP_VERSION)
except Exception:
    tracer = None

# Label Studio configuration
LABEL_STUDIO_URL = woprvar.WOPR_CONFIG["vision"]["label_studio_url"]
LABEL_STUDIO_TOKEN = os.getenv('LABEL_STUDIO_TOKEN', '')

if not LABEL_STUDIO_TOKEN:
    logger.warning("LABEL_STUDIO_TOKEN not set - vision endpoints will fail")

# JWT token state management
class TokenManager:
    """Manages Label Studio JWT token lifecycle"""
    
    def __init__(self):
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = LABEL_STUDIO_TOKEN  # Initial token
        self.token_expiry: Optional[datetime] = None
        self._lock = asyncio.Lock()
    
    async def get_access_token(self) -> str:
        """
        Get valid access token, refreshing if necessary.
        Thread-safe with async lock.
        """
        async with self._lock:
            # Check if token exists and is still valid
            if self.access_token and self.token_expiry:
                # Refresh if within 5 minutes of expiry
                if datetime.utcnow() < (self.token_expiry - timedelta(minutes=5)):
                    return self.access_token
            
            # Need to refresh
            await self._refresh_token()
            return self.access_token
    
    async def _refresh_token(self):
        """Refresh JWT access token using refresh token"""
        if not self.refresh_token:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No refresh token available"
            )
        
        logger.info("Refreshing Label Studio JWT token")
        
        url = f"{LABEL_STUDIO_URL}/api/tokens/refresh"
        payload = {"refresh": self.refresh_token}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                self.access_token = data.get("access")
                
                # Label Studio JWTs typically expire in 5 minutes
                # Adjust if different
                self.token_expiry = datetime.utcnow() + timedelta(minutes=5)
                
                logger.info("Token refreshed successfully")
                
        except httpx.HTTPError as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to refresh Label Studio token: {str(e)}"
            )


# Global token manager instance
token_manager = TokenManager()


async def get_ls_headers() -> Dict[str, str]:
    """Build Label Studio API headers with current JWT token"""
    access_token = await token_manager.get_access_token()
    
    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }


# Request/Response models
class ProjectListResponse(BaseModel):
    """Label Studio projects list response"""
    count: int
    results: List[Dict[str, Any]]


class TaskCreateRequest(BaseModel):
    """Create annotation task in Label Studio"""
    project_id: int
    data: Dict[str, Any]  # Task data payload


class TaskCreateResponse(BaseModel):
    """Task creation response"""
    id: int
    project: int
    data: Dict[str, Any]


@router.get("/projects")
async def list_projects() -> ProjectListResponse:
    """
    List all Label Studio projects.
    
    Returns:
        ProjectListResponse with project list
    """
    with tracer.start_as_current_span("vision.list_projects") if tracer else nullcontext() as span:
        if span and span.is_recording():
            span.set_attribute("labelstudio.operation", "list_projects")
        
        logger.info("Fetching Label Studio projects")
        
        url = f"{LABEL_STUDIO_URL}/api/projects"
        headers = await get_ls_headers()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"Retrieved {len(data.get('results', []))} projects")
                return ProjectListResponse(**data)
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Label Studio API error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Label Studio API error: {e.response.text}"
            )
        except httpx.HTTPError as e:
            logger.error(f"Failed to reach Label Studio: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to communicate with Label Studio: {str(e)}"
            )


@router.get("/projects/{project_id}")
async def get_project(project_id: int) -> Dict[str, Any]:
    """
    Get specific Label Studio project details.
    
    Args:
        project_id: Label Studio project ID
    
    Returns:
        Project details
    """
    with tracer.start_as_current_span("vision.get_project") if tracer else nullcontext() as span:
        if span and span.is_recording():
            span.set_attribute("labelstudio.operation", "get_project")
            span.set_attribute("labelstudio.project_id", project_id)
        
        logger.info(f"Fetching Label Studio project {project_id}")
        
        url = f"{LABEL_STUDIO_URL}/api/projects/{project_id}"
        headers = await get_ls_headers()
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Label Studio API error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Label Studio API error: {e.response.text}"
            )
        except httpx.HTTPError as e:
            logger.error(f"Failed to reach Label Studio: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to communicate with Label Studio: {str(e)}"
            )


@router.post("/tasks")
async def create_task(request: TaskCreateRequest) -> TaskCreateResponse:
    """
    Create annotation task in Label Studio project.
    
    Args:
        request: Task creation request
    
    Returns:
        Created task details
    """
    with tracer.start_as_current_span("vision.create_task") if tracer else nullcontext() as span:
        if span and span.is_recording():
            span.set_attribute("labelstudio.operation", "create_task")
            span.set_attribute("labelstudio.project_id", request.project_id)
        
        logger.info(f"Creating task in Label Studio project {request.project_id}")
        
        url = f"{LABEL_STUDIO_URL}/api/projects/{request.project_id}/tasks"
        headers = await get_ls_headers()
        
        payload = {"data": request.data}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                task_data = response.json()
                
                logger.info(f"Created task {task_data.get('id')} in project {request.project_id}")
                return TaskCreateResponse(**task_data)
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Label Studio API error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Label Studio API error: {e.response.text}"
            )
        except httpx.HTTPError as e:
            logger.error(f"Failed to reach Label Studio: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to communicate with Label Studio: {str(e)}"
            )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check for Label Studio connectivity.
    
    Returns:
        Health status
    """
    with tracer.start_as_current_span("vision.health") if tracer else nullcontext():
        logger.debug("Vision service health check")
        
        url = f"{LABEL_STUDIO_URL}/api/projects"
        
        try:
            headers = await get_ls_headers()
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                return {
                    "status": "healthy",
                    "label_studio_url": LABEL_STUDIO_URL,
                    "token_configured": bool(LABEL_STUDIO_TOKEN),
                    "token_valid": bool(token_manager.access_token)
                }
                
        except Exception as e:
            logger.error(f"Label Studio health check failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Label Studio unavailable: {str(e)}"
            )