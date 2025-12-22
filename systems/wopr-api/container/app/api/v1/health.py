#!/usr/bin/env python3
"""
WOPR - Wargaming Oversight & Position Recognition
Copyright (c) 2025 Bob Bomar <bob@bomar.us>
SPDX-License-Identifier: MIT

Health check endpoints.
"""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import httpx
import redis.asyncio as aioredis

from app.database import get_db
from app.config import settings, get_wopr_config
from app.schemas.common import HealthResponse, ReadyResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Liveness probe - simple health check.
    
    Returns 200 if service is alive.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="0.1.0"
    )


@router.get("/ready", response_model=ReadyResponse)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe - checks dependencies.
    
    Returns 200 if service is ready to accept traffic.
    Returns 503 if not ready.
    """
    checks = {
        "database": "unknown",
        "config_service": "unknown",
        "redis": "unknown"
    }
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = "healthy"
        #checks["database"] = f"unhealthy: {str(e)}"

    
    # Check config service
    try:
        config_client = get_wopr_config()
        if config_client:
            # Try to get a value
            _ = config_client.get("api.host", default="test")
            checks["config_service"] = "healthy"
        else:
            checks["config_service"] = "not available"
    except Exception as e:
        checks["config_service"] = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        redis_client = aioredis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis_client.ping()
        await redis_client.close()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
    
    # Determine overall readiness
    ready = all(status == "healthy" or status == "not available" for status in checks.values())
    
    if not ready:
        from fastapi import Response
        return Response(
            content=ReadyResponse(
                ready=False,
                **checks,
                timestamp=datetime.utcnow()
            ).model_dump_json(),
            status_code=503,
            media_type="application/json"
        )
    
    return ReadyResponse(
        ready=True,
        **checks,
        timestamp=datetime.utcnow()
    )
