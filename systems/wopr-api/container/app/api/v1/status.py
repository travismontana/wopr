"""
WOPR - Wargaming Oversight & Position Recognition
# Copyright (c) 2025-present Bob <bob@example.com>
# See git log for detailed authorship

WOPR API - cameras api.

"""

from wopr import config as woprconfig
from wopr import storage as woprstorage
from app import globals as woprvar
from datetime import datetime, timezone
import logging
import os
import asyncpg
from pydantic import BaseModel
import base64
import json
import httpx

import logging
import sys
logger = logging.getLogger(woprvar.APP_NAME)
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter(tags=["status"])

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
    diff_timestamp_ms: int
    diff_timestamp_s: float

async def get_db_uri() -> str:
    """
    Get database URI from environment or k8s secret.
    
    In k8s, wopr_config-db_cluster-app secret should be mounted as env var:
    DATABASE_URL from secret/wopr_config-db_cluster-app/uri
    """
    uri = os.getenv("DATABASE_URL")
    if not uri:
        logger.error("DATABASE_URL environment variable not set")
        raise RuntimeError("DATABASE_URL environment variable not set")
    return uri

@router.get("/db_up")
async def check_db_up() -> StatusCheck:
    """
    Check if database is reachable and accepting connections.
    
    Test: Can we connect to the port and execute SELECT 1?
    """
    start_time = datetime.now(timezone.utc)
    logger.debug("Checking database connectivity... starttime=%s", start_time)
    try:
        db_uri = await get_db_uri()
        logger.debug("Database URI obtained.")
        # Connect and run simplest possible query
        conn = await asyncpg.connect(db_uri)
        logger.debug("Database connection established.")
        try:
            result = await conn.fetchval("SELECT 1")
            logger.debug("Database query executed, result=%s", result)
            if result == 1:
                logger.debug("Database is up and running.")
                return StatusCheck(
                    test_name="db_up",
                    test_start_timestamp=start_time,
                    test_result="pass",
                    test_end_timestamp=datetime.now(timezone.utc),
                )
        finally:
            await conn.close()
            logger.debug("Database connection closed.")
            
    except Exception as e:
        logger.error("Database connectivity check failed: %s", str(e))
        return StatusCheck(
            test_name="db_up",
            test_start_timestamp=start_time,
            test_result="fail",
            test_end_timestamp=datetime.now(timezone.utc),
            error_message=str(e),
        )
@router.get("/db_queriable")
async def check_db_queriable() -> StatusCheck:
    """
    Check if database is queriable (can SELECT from real tables).
    
    Test: Can we query the config_values table?
    """
    start_time = datetime.now(timezone.utc)
    logger.debug("Checking database queriability... starttime=%s", start_time)
    try:
        db_uri = await get_db_uri()
        logger.debug("Database URI obtained.")
        conn = await asyncpg.connect(db_uri)
        logger.debug("Database connection established.")
        try:
            # Query something we actually care about
            result = await conn.fetchval(
                "SELECT COUNT(*) FROM settings"
            )
            logger.debug("Database queriability query executed, result=%s", result)
            if result is not None:  # Even 0 is valid
                logger.debug("Database is queriable.")
                return StatusCheck(
                    test_name="db_queriable",
                    test_start_timestamp=start_time,
                    test_result="pass",
                    test_end_timestamp=datetime.now(timezone.utc),
                )
        finally:
            await conn.close()
            logger.debug("Database connection closed.")
            
    except Exception as e:
        logger.error("Database queriability check failed: %s", str(e))
        return StatusCheck(
            test_name="db_queriable",
            test_start_timestamp=start_time,
            test_result="fail",
            test_end_timestamp=datetime.now(timezone.utc),
            error_message=str(e),
        )


@router.get("/db_writable")
async def check_db_writable() -> StatusCheck:
    """
    Check if database is writable (disks alive?).
    
    Test: Can we INSERT into status_checks table?
    """
    start_time = datetime.now(timezone.utc)
    logger.debug("Checking database writability... starttime=%s", start_time)
    try:
        db_uri = await get_db_uri()
        logger.debug("Database URI obtained.")
        conn = await asyncpg.connect(db_uri)
        logger.debug("Database connection established.")
        try:
            # Write a test record
            test_time = datetime.now(timezone.utc)
            logger.debug("Inserting test record into status_checks table at %s", test_time)
            await conn.execute(
                """
                INSERT INTO status_checks 
                (test_name, test_start_timestamp, test_result, test_end_timestamp)
                VALUES ($1, $2, $3, $4)
                """,
                "db_writable-probe",
                test_time,
                "pass",
                test_time,
            )
            logger.debug("Test record inserted successfully.")
            return StatusCheck(
                test_name="db_writable",
                test_start_timestamp=start_time,
                test_result="pass",
                test_end_timestamp=datetime.now(timezone.utc),
            )
        finally:
            await conn.close()
            logger.debug("Database connection closed.")
            
    except Exception as e:
        logger.error("Database writability check failed: %s", str(e))
        return StatusCheck(
            test_name="db_writable",
            test_start_timestamp=start_time,
            test_result="fail",
            test_end_timestamp=datetime.now(timezone.utc),
            error_message=str(e),
        )

@router.get("/inittable")
async def init_status_checks_table() -> str:
    """
    Initialize the status_checks table in the database.
    
    This should be run once during setup.
    """
    db_uri = await get_db_uri()
    
    conn = await asyncpg.connect(db_uri)
    try:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS status_checks (
                id SERIAL PRIMARY KEY,
                test_name VARCHAR(100) NOT NULL,
                test_start_timestamp TIMESTAMPTZ NOT NULL,
                test_result VARCHAR(20) NOT NULL,  -- 'pass', 'fail', 'norun'
                test_end_timestamp TIMESTAMPTZ NOT NULL,
                error_message TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_status_checks_test_name ON status_checks(test_name);
            CREATE INDEX IF NOT EXISTS idx_status_checks_created_at ON status_checks(created_at DESC);
            """
        )
        return "status_checks table initialized successfully."
    finally:
        await conn.close()

@router.get("/wopr-web-up")
async def check_wopr_web_up() -> StatusCheck:
    """
    Check if WOPR web is up.
    """
    start_time = datetime.now(timezone.utc)
    logger.debug("Checking WOPR web up... starttime=%s", start_time)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://wopr.{woprvar.APP_DOMAIN}", timeout=5.0)
            response.raise_for_status()
            logger.debug("WOPR web up check passed.")
            return StatusCheck(
                test_name="wopr_web_up",
                test_start_timestamp=start_time,
                test_result="pass",
                test_end_timestamp=datetime.now(timezone.utc),
            )
    except Exception as e:
        logger.error("WOPR web up check failed: %s", str(e))
        return StatusCheck(
            test_name="wopr_web_up",
            test_start_timestamp=start_time,
            test_result="fail",
            test_end_timestamp=datetime.now(timezone.utc),
            error_message=str(e),
        )

@router.get("/wopr-web-functional")
async def check_wopr_web_functional() -> StatusCheck:
    """
    Check if WOPR web is functional.
    """
    start_time = datetime.now(timezone.utc)
    logger.debug("Checking WOPR web functional... starttime=%s", start_time)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://wopr.{woprvar.APP_DOMAIN}/ml", timeout=5.0)
            response.raise_for_status()
            logger.debug("WOPR web functional check passed.")
            return StatusCheck(
                test_name="wopr_web_functional",
                test_start_timestamp=start_time,
                test_result="pass",
                test_end_timestamp=datetime.now(timezone.utc),
            )
    except Exception as e:
        logger.error("WOPR web functional check failed: %s", str(e))
        return StatusCheck(
            test_name="wopr_web_functional",
            test_start_timestamp=start_time,
            test_result="fail",
            test_end_timestamp=datetime.now(timezone.utc),
            error_message=str(e),
        )

#Samething, but now for api, and will check WOPR_API_URL for up, and WOPR_API_URL/docs for functional
@router.get("/wopr-api-up")
async def check_wopr_api_up() -> StatusCheck:
    """
    Check if WOPR API is up.
    """
    start_time = datetime.now(timezone.utc)
    logger.debug("Checking WOPR API up... starttime=%s", start_time)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{woprvar.WOPR_API_URL}/health", timeout=5.0)
            response.raise_for_status()
            logger.debug("WOPR API up check passed.")
            return StatusCheck(
                test_name="wopr_api_up",
                test_start_timestamp=start_time,
                test_result="pass",
                test_end_timestamp=datetime.now(timezone.utc),
            )
    except Exception as e:
        logger.error("WOPR API up check failed: %s", str(e))
        return StatusCheck(
            test_name="wopr_api_up",
            test_start_timestamp=start_time,
            test_result="fail",
            test_end_timestamp=datetime.now(timezone.utc),
            error_message=str(e),
        )

@router.get("/wopr-api-functional")
async def check_wopr_api_functional() -> StatusCheck:
    """
    Check if WOPR API is functional.
    """
    start_time = datetime.now(timezone.utc)
    logger.debug("Checking WOPR API functional... starttime=%s", start_time)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{woprvar.WOPR_API_URL}/health", timeout=5.0)
            response.raise_for_status()
            logger.debug("WOPR API functional check passed.")
            return StatusCheck(
                test_name="wopr_api_functional",
                test_start_timestamp=start_time,
                test_result="pass",
                test_end_timestamp=datetime.now(timezone.utc),
            )
    except Exception as e:
        logger.error("WOPR API functional check failed: %s", str(e))
        return StatusCheck(
            test_name="wopr_api_functional",
            test_start_timestamp=start_time,
            test_result="fail",
            test_end_timestamp=datetime.now(timezone.utc),
            error_message=str(e),
        )

@router.get("/wopr-cam-up")
async def check_wopr_cam_up() -> StatusCheck:
    """
    Check if WOPR camera is up.
    """
    start_time = datetime.now(timezone.utc)
    camUrl = woprvar.HACK_CAMERA_DICT["1"]["url"]
    camPort = woprvar.HACK_CAMERA_DICT["1"]["port"]
    logger.debug("Checking WOPR camera up... starttime=%s camUrl=%s camPort=%s", start_time, camUrl, camPort)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{camUrl}:{camPort}/status", timeout=5.0)
            response.raise_for_status()
            logger.debug("WOPR camera up check passed.")
            return StatusCheck(
                test_name="wopr_cam_up",
                test_start_timestamp=start_time,
                test_result="pass",
                test_end_timestamp=datetime.now(timezone.utc),
            )
    except Exception as e:
        logger.error("WOPR camera up check failed: error: %s camUrl=%s camPort=%s", str(e), camUrl, camPort)
        return StatusCheck(
            test_name="wopr_cam_up",
            test_start_timestamp=start_time,
            test_result="fail",
            test_end_timestamp=datetime.now(timezone.utc),
            error_message=str(e),
        )

@router.get("/wopr-cam-functional")
async def check_wopr_cam_functional() -> StatusCheck:
    """
    Check if WOPR camera is functional.
    """
    start_time = datetime.now(timezone.utc)
    camUrl = woprvar.HACK_CAMERA_DICT["1"]["url"]
    camPort = woprvar.HACK_CAMERA_DICT["1"]["port"]
    logger.debug("Checking WOPR camera functional... starttime=%s camUrl=%s camPort=%s", start_time, camUrl, camPort)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{camUrl}:{camPort}/status", timeout=5.0)
            response.raise_for_status()
            logger.debug("WOPR camera functional check passed.")
            return StatusCheck(
                test_name="wopr_cam_functional",
                test_start_timestamp=start_time,
                test_result="pass",
                test_end_timestamp=datetime.now(timezone.utc),
            )
    except Exception as e:
        logger.error("WOPR camera functional check failed: %s", str(e))
        return StatusCheck(
            test_name="wopr_cam_functional",
            test_start_timestamp=start_time,
            test_result="fail",
            test_end_timestamp=datetime.now(timezone.utc),
            error_message=str(e),
        )

# for check_config_map_present, we will just check if the environment variable WOPR_API_URL is set, as a proxy for checking if the config map is present
@router.get("/wopr-config-map-present")
async def check_config_map_present() -> StatusCheck:
    """
    Check if WOPR config map is present.
    """
    start_time = datetime.now(timezone.utc)
    logger.debug("Checking WOPR config map present... starttime=%s", start_time)
    try:
        if os.getenv("WOPR_API_URL"):
            logger.debug("WOPR config map present check passed.")
            return StatusCheck(
                test_name="wopr_config_map_present",
                test_start_timestamp=start_time,
                test_result="pass",
                test_end_timestamp=datetime.now(timezone.utc),
            )
        else:
            raise RuntimeError("WOPR_API_URL environment variable not set")
    except Exception as e:
        logger.error("WOPR config map present check failed: %s", str(e))
        return StatusCheck(
            test_name="wopr_config_map_present",
            test_start_timestamp=start_time,
            test_result="fail",
            test_end_timestamp=datetime.now(timezone.utc),
            error_message=str(e),
        )

@router.get("/")
@router.get("")
async def get_system_status() -> SystemStatus:
    """
    Get current status of all WOPR components.
    
    Returns aggregated health check results.
    """
    before = datetime.now(timezone.utc)
    logger.debug("Gathering system status... starttime=%s", before)
    # Run all checks (placeholder - you'll implement these)
    db_up = await check_db_up()
    logger.debug("Database up check result: %s", db_up)
    db_queriable = await check_db_queriable()
    logger.debug("Database queriable check result: %s", db_queriable)
    db_writable = await check_db_writable()
    logger.debug("Database writable check result: %s", db_writable)
    
    # TODO: Implement other checks
    wopr_web_up = await check_wopr_web_up()
    logger.debug("WOPR web up check result: %s", wopr_web_up)
    wopr_web_functional = await check_wopr_web_functional()
    logger.debug("WOPR web functional check result: %s", wopr_web_functional)
    wopr_api_up = await check_wopr_api_up()
    logger.debug("WOPR API up check result: %s", wopr_api_up)
    wopr_api_functional = await check_wopr_api_functional()
    logger.debug("WOPR API functional check result: %s", wopr_api_functional)
    wopr_cam_up = await check_wopr_cam_up()
    logger.debug("WOPR camera up check result: %s", wopr_cam_up)
    wopr_cam_functional = await check_wopr_cam_functional()
    logger.debug("WOPR camera functional check result: %s", wopr_cam_functional)
    config_map_present = await check_config_map_present()
    logger.debug("WOPR config map present check result: %s", config_map_present)
    
    after = datetime.now(timezone.utc)
    logger.debug("System status gathered... endtime=%s", after)
    
    return SystemStatus(
        timestamp_right_before_data_pull=before,
        db_up=(db_up.test_result == "pass"),
        db_queriable=(db_queriable.test_result == "pass"),
        db_writable=(db_writable.test_result == "pass"),
        wopr_web_up=(wopr_web_up.test_result == "pass"),
        wopr_web_functional=(wopr_web_functional.test_result == "pass"),
        wopr_api_up=(wopr_api_up.test_result == "pass"),
        wopr_api_functional=(wopr_api_functional.test_result == "pass"),
        wopr_cam_up=(wopr_cam_up.test_result == "pass"),
        wopr_cam_functional=(wopr_cam_functional.test_result == "pass"),
        wopr_config_map_present=(config_map_present.test_result == "pass"),
        timestamp_right_after_data_pull=after,
        diff_timestamp_ms=int((after - before).total_seconds() * 1000),
        # timestamp in seconds to a significand of 4 digits
        diff_timestamp_s=float(f"{(after - before).total_seconds():.4f}"),
        )
