#!/usr/bin/env python3
"""
WOPR Config Service - Directus API Proxy
"""
from fastapi import APIRouter, HTTPException
import httpx
import os
import logging
import sys
from opentelemetry import trace
from contextlib import nullcontext

logger = logging.getLogger(__name__)
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

router = APIRouter(tags=["config"])

# Directus configuration
DIRECTUS_URL = os.getenv(
    'DIRECTUS_URL', 
    'https://directus.wopr.tailandtraillabs.org'
)
DIRECTUS_TOKEN = os.getenv('DIRECTUS_TOKEN', '')

# Get tracer (if tracing enabled)
try:
    from app import globals as woprvar
    tracer = trace.get_tracer(woprvar.APP_NAME, woprvar.APP_VERSION)
except:
    tracer = None


@router.get("/all")
async def get_all(environment: str = "production"):
    """
    Get entire configuration for specified environment.
    Proxies request to Directus API.
    
    Args:
        environment: Config environment (production, stage, dev)
    
    Returns:
        Configuration JSONB document
    """
    # Start custom span for better tracing granularity
    with tracer.start_as_current_span("config.get_all") if tracer else nullcontext() as span:
        if span and span.is_recording():
            span.set_attribute("config.environment", environment)
            span.set_attribute("config.source", "directus")
        
        logger.info(f"Fetching config for environment: {environment}")
        
        # Build Directus API request
        url = f"{DIRECTUS_URL}/items/woprconfig"
        params = {
            "filter[environment][_eq]": environment,
            "fields": "data"
        }
        
        headers = {}
        if DIRECTUS_TOKEN:
            headers["Authorization"] = f"Bearer {DIRECTUS_TOKEN}"
        
        try:
            # HTTPX call - automatically instrumented
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
            
            if span and span.is_recording():
                span.set_attribute("http.response.status_code", response.status_code)
                span.set_attribute("config.directus.url", url)
            
            result = response.json()
            
            # Extract config data from Directus response
            if not result.get("data") or len(result["data"]) == 0:
                if span and span.is_recording():
                    span.set_attribute("config.found", False)
                raise HTTPException(
                    status_code=404,
                    detail=f"No configuration found for environment: {environment}"
                )
            
            # Return the actual config JSONB (unwrap Directus wrapper)
            config_data = result["data"][0]["data"]
            
            if span and span.is_recording():
                span.set_attribute("config.found", True)
                span.set_attribute("config.keys_count", len(config_data.keys()))
            
            logger.info(f"Successfully retrieved config for {environment}")
            return config_data
            
        except httpx.HTTPError as e:
            logger.error(f"Directus API error: {e}")
            if span and span.is_recording():
                span.set_attribute("error", True)
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch config from Directus: {str(e)}"
            )
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected Directus response format: {e}")
            if span and span.is_recording():
                span.set_attribute("error", True)
                span.set_attribute("error.type", "invalid_response_format")
            raise HTTPException(
                status_code=500,
                detail="Invalid response from Directus API"
            )

@router.get("/environments")
async def get_environments():
    """
    Get entire configuration for specified environment.
    Proxies request to Directus API.
    
    Args:
        environment: Config environment (production, stage, dev)
    
    Returns:
        Configuration JSONB document
    """
    # Start custom span for better tracing granularity
    with tracer.start_as_current_span("config.get_environments") if tracer else nullcontext() as span:
        if span and span.is_recording():
            span.set_attribute("config.source", "directus")

        logger.info(f"Fetching all environments config")
        
        # Build Directus API request
        url = f"{DIRECTUS_URL}/items/woprconfig?groupBy[]=environment&aggregate[count]=*"
        params = {
                "fields": "data"
        }
        
        headers = {}
        if DIRECTUS_TOKEN:
            headers["Authorization"] = f"Bearer {DIRECTUS_TOKEN}"
        
        try:
            # HTTPX call - automatically instrumented
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
            
            if span and span.is_recording():
                span.set_attribute("http.response.status_code", response.status_code)
                span.set_attribute("config.directus.url", url)
            
            result = response.json()
            
            # Extract config data from Directus response
            if not result.get("data") or len(result["data"]) == 0:
                if span and span.is_recording():
                    span.set_attribute("config.found", False)
                raise HTTPException(
                    status_code=404,
                    detail=f"No configuration found for data: {data}"
                )
            
            # Return the actual config JSONB (unwrap Directus wrapper)
            config_data = result["data"]
            
            if span and span.is_recording():
                span.set_attribute("config.found", True)
                span.set_attribute("config.keys_count", len(config_data.keys()))
            
            logger.info(f"Successfully retrieved result for {config_data}")
            return config_data
            
        except httpx.HTTPError as e:
            logger.error(f"Directus API error: {e}")
            if span and span.is_recording():
                span.set_attribute("error", True)
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch config from Directus: {str(e)}"
            )
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected Directus response format: {e}")
            if span and span.is_recording():
                span.set_attribute("error", True)
                span.set_attribute("error.type", "invalid_response_format")
            raise HTTPException(
                status_code=500,
                detail="Invalid response from Directus API"
            )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    with tracer.start_as_current_span("config.health") if tracer else nullcontext():
        return {"status": "ok", "service": "wopr-config"}
