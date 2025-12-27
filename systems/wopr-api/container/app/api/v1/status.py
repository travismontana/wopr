"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob <bob@example.com>
# See git log for detailed authorship

WOPR API - cameras api.

"""

from wopr import config as woprconfig
from wopr import storage as woprstorage
from wopr import logging as woprlogging
from app import globals as woprvar
from datetime import datetime, timezone
import logging
import os
import asyncpg
from pydantic import BaseModel
import base64
import json

woprconfig.init_config(service_url=os.getenv("WOPR_API_URL") or woprvar.WOPR_API_URL)
logger = woprlogging.setup_logging(woprvar.APP_NAME)

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/status", tags=["status"])

class StatusCheck(BaseModel):
    """Single status check result"""
    test_name: str
    test_start_timestamp: datetime
    test_result: str  # pass|fail|norun
    test_end_timestamp: datetime
    error_message: str | None = None

class SystemStatus(BaseModel):
    """Overall system status"""
    timestamp_right_before_data_pull: datetime
    db_up: bool
    db_queriable: bool
    db_writable: bool
    wopr_web_up: bool
    wopr_web_functional: bool
    wopr_api_up: bool
    wopr_api_functional: bool
    wopr_cam_up: bool
    wopr_cam_functional: bool
    wopr_config_map_present: bool
    timestamp_right_after_data_pull: datetime

async def get_db_uri() -> str:
    """
    Get database URI from environment or k8s secret.
    
    In k8s, wopr-config-db-cluster-app secret should be mounted as env var:
    DATABASE_URL from secret/wopr-config-db-cluster-app/uri
    """
    uri = os.getenv("DATABASE_URL")
    if not uri:
        raise RuntimeError("DATABASE_URL environment variable not set")
    return uri

@router.get("/db-up")
async def check_db_up() -> StatusCheck:
    """
    Check if database is reachable and accepting connections.
    
    Test: Can we connect to the port and execute SELECT 1?
    """
    start_time = datetime.now(timezone.utc)
    
    try:
        db_uri = await get_db_uri()
        
        # Connect and run simplest possible query
        conn = await asyncpg.connect(db_uri)
        try:
            result = await conn.fetchval("SELECT 1")
            if result == 1:
                return StatusCheck(
                    test_name="db-up",
                    test_start_timestamp=start_time,
                    test_result="pass",
                    test_end_timestamp=datetime.now(timezone.utc),
                )
        finally:
            await conn.close()
            
    except Exception as e:
        return StatusCheck(
            test_name="db-up",
            test_start_timestamp=start_time,
            test_result="fail",
            test_end_timestamp=datetime.now(timezone.utc),
            error_message=str(e),
        )
@router.get("/db-queriable")
async def check_db_queriable() -> StatusCheck:
    """
    Check if database is queriable (can SELECT from real tables).
    
    Test: Can we query the config_values table?
    """
    start_time = datetime.now(timezone.utc)
    
    try:
        db_uri = await get_db_uri()
        
        conn = await asyncpg.connect(db_uri)
        try:
            # Query something we actually care about
            result = await conn.fetchval(
                "SELECT COUNT(*) FROM config_values WHERE is_active = true"
            )
            
            if result is not None:  # Even 0 is valid
                return StatusCheck(
                    test_name="db-queriable",
                    test_start_timestamp=start_time,
                    test_result="pass",
                    test_end_timestamp=datetime.now(timezone.utc),
                )
        finally:
            await conn.close()
            
    except Exception as e:
        return StatusCheck(
            test_name="db-queriable",
            test_start_timestamp=start_time,
            test_result="fail",
            test_end_timestamp=datetime.now(timezone.utc),
            error_message=str(e),
        )


@router.get("/db-writable")
async def check_db_writable() -> StatusCheck:
    """
    Check if database is writable (disks alive?).
    
    Test: Can we INSERT into status_checks table?
    """
    start_time = datetime.now(timezone.utc)
    
    try:
        db_uri = await get_db_uri()
        
        conn = await asyncpg.connect(db_uri)
        try:
            # Write a test record
            test_time = datetime.now(timezone.utc)
            await conn.execute(
                """
                INSERT INTO status_checks 
                (test_name, test_start_timestamp, test_result, test_end_timestamp)
                VALUES ($1, $2, $3, $4)
                """,
                "db-writable-probe",
                test_time,
                "pass",
                test_time,
            )
            
            return StatusCheck(
                test_name="db-writable",
                test_start_timestamp=start_time,
                test_result="pass",
                test_end_timestamp=datetime.now(timezone.utc),
            )
        finally:
            await conn.close()
            
    except Exception as e:
        return StatusCheck(
            test_name="db-writable",
            test_start_timestamp=start_time,
            test_result="fail",
            test_end_timestamp=datetime.now(timezone.utc),
            error_message=str(e),
        )


@router.get("/")
async def get_system_status() -> SystemStatus:
    """
    Get current status of all WOPR components.
    
    Returns aggregated health check results.
    """
    before = datetime.now(timezone.utc)
    
    # Run all checks (placeholder - you'll implement these)
    db_up = await check_db_up()
    db_queriable = await check_db_queriable()
    db_writable = await check_db_writable()
    
    # TODO: Implement other checks
    wopr_web_up = False  # HTTP GET to wopr-web
    wopr_web_functional = False  # Check for dynamic content
    wopr_api_up = True  # Self-check (you're here, aren't you?)
    wopr_api_functional = False  # Can create a game?
    wopr_cam_up = False  # HTTP GET to wopr-cam
    wopr_cam_functional = False  # Get camera status
    config_map_present = False  # Check k8s API
    
    after = datetime.now(timezone.utc)
    
    return SystemStatus(
        timestamp_right_before_data_pull=before,
        db_up=(db_up.test_result == "pass"),
        db_queriable=(db_queriable.test_result == "pass"),
        db_writable=(db_writable.test_result == "pass"),
        wopr_web_up=wopr_web_up,
        wopr_web_functional=wopr_web_functional,
        wopr_api_up=wopr_api_up,
        wopr_api_functional=wopr_api_functional,
        wopr_cam_up=wopr_cam_up,
        wopr_cam_functional=wopr_cam_functional,
        wopr_config_map_present=config_map_present,
        timestamp_right_after_data_pull=after,
    )