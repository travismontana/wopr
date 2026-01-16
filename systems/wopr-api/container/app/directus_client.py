#
# get_one()
# get_all()
# post()
# update()
# delete()
#
# payload = {
#  
#}
#
#
#
# app/directus_client.py

import httpx
from typing import Optional, Dict, List, Any
from fastapi import HTTPException
import logging
from app import globals as woprvar

logger = logging.getLogger(__name__)

# Create session at module level (connection pooling)
client = httpx.Client(
    base_url=woprvar.DIRECTUS_URL,
    headers=woprvar.DIRECTUS_HEADERS,
    timeout=30.0
)

def _build_params(filters=None, fields=None, sort=None, limit=None, offset=None):
    """Build Directus query parameters"""
    params = {}
    
    if filters:
        # Directus filter syntax: filter[field][operator]=value
        for key, value in filters.items():
            if isinstance(value, dict):
                for op, val in value.items():
                    params[f"filter[{key}]{op}"] = val
            else:
                params[f"filter[{key}][_eq]"] = value
    
    if fields:
        params["fields"] = ",".join(fields)
    
    if sort:
        params["sort"] = ",".join(sort)
    
    if limit:
        params["limit"] = limit
    
    if offset:
        params["offset"] = offset
    
    return params


def get_one(collection: str, item_id: str, fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """Get single item from Directus collection"""
    url = f"/items/{collection}/{item_id}"
    params = _build_params(fields=fields)
    
    try:
        response = client.get(url, params=params)
        response.raise_for_status()
        logger.info(f"GET {collection}/{item_id} succeeded")
        return response.json()["data"]
    except httpx.HTTPError as e:
        logger.error(f"GET {collection}/{item_id} failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_all(
    collection: str,
    filters: Optional[Dict] = None,
    fields: Optional[List[str]] = None,
    sort: Optional[List[str]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Get multiple items from Directus collection"""
    url = f"/items/{collection}"
    params = _build_params(filters, fields, sort, limit, offset)
    
    try:
        response = client.get(url, params=params)
        response.raise_for_status()
        logger.info(f"GET {collection} succeeded (returned {len(response.json()['data'])} items)")
        return response.json()["data"]
    except httpx.HTTPError as e:
        logger.error(f"GET {collection} failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def post(collection: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Create new item in Directus collection"""
    url = f"/items/{collection}"
    
    try:
        response = client.post(url, json=data)
        response.raise_for_status()
        logger.info(f"POST {collection} succeeded")
        return response.json()["data"]
    except httpx.HTTPError as e:
        logger.error(f"POST {collection} failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def update(collection: str, item_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update existing item in Directus collection"""
    url = f"/items/{collection}/{item_id}"
    
    try:
        response = client.patch(url, json=data)
        response.raise_for_status()
        logger.info(f"PATCH {collection}/{item_id} succeeded")
        return response.json()["data"]
    except httpx.HTTPError as e:
        logger.error(f"PATCH {collection}/{item_id} failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def delete(collection: str, item_id: str) -> None:
    """Delete item from Directus collection"""
    url = f"/items/{collection}/{item_id}"
    
    try:
        response = client.delete(url)
        response.raise_for_status()
        logger.info(f"DELETE {collection}/{item_id} succeeded")
    except httpx.HTTPError as e:
        logger.error(f"DELETE {collection}/{item_id} failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))