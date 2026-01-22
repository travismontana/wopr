"""
WOPR Frontend Helpers
Utility functions for Streamlit UI interactions with WOPR API.
"""

import httpx
import re
import logging
import sys
from datetime import datetime
from pathlib import Path

from wopr_api_client import Client
API_BASE = "https://api.wopr.tailandtraillabs.org"
client = Client(base_url=API_BASE)


# Flavor text for play submissions
PLAYPHRASES = [
    "My move is made",
    "The feud continues",
    "The next blow is struck",
    "I was friend of Jamis",
    "Fear is the mind killer",
    "There is no escape",
    "You're worm food",
    "Hasta la vista wormy"
]

LOGGER_NAME = "helpers"

project_cheat = {
    "name": "Dune Imperium Uprising Project",
    "shortname": "duneup",
    "id": 6,
    "uuid": "some-unique-uuid"
}

# ------------------------
# Logging Setup
# ------------------------

def setup_logger() -> logging.Logger:
    """
    Configure logging for helper functions.
    
    Returns:
        Configured logger instance
        
    Note:
        Only configures once - subsequent calls return existing logger
    """
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    return logger


log = setup_logger()

# ------------------------
# CRUD Operations
# ------------------------

def get_all(noun: str) -> list:
    """
    Fetch all items of a given type from WOPR API.
    
    Args:
        noun: Resource type (sessions, plays, games, pieces, etc.)
    
    Returns:
        List of items, empty list on failure
        
    Example:
        games = get_all("games")
        sessions = get_all("sessions")
    """
    url = f"{API_BASE}/api/v2/{noun}"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        items = response.json()
        log.info(f"Retrieved {len(items)} items from {noun}")
        return items
    except httpx.HTTPError as e:
        log.error(f"Failed to fetch {noun}: {e}")
        return []


def get_one(noun: str, item_id: str) -> dict:
    """
    Fetch a single item by ID from WOPR API.
    
    Args:
        noun: Resource type (sessions, plays, games, pieces, etc.)
        item_id: Unique identifier for the item
    
    Returns:
        Dict containing item data, empty dict on failure
        
    Example:
        session = get_one("sessions", "abc-123-def")
    """
    url = f"{API_BASE}/api/v2/{noun}/{item_id}"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        item = response.json()
        log.info(f"Retrieved item {item_id} from {noun}")
        return item
    except httpx.HTTPError as e:
        log.error(f"Failed to fetch {noun} {item_id}: {e}")
        return {}


def create_new(noun: str, payload: dict) -> dict:
    """
    Create a new item via WOPR API.
    
    Args:
        noun: Resource type to create
        payload: Dict containing item data
    
    Returns:
        Created item data, empty dict on failure
        
    Example:
        new_session = create_new("sessions", {"gameid": 1})
    """
    url = f"{API_BASE}/api/v2/{noun}"
    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        item = response.json().get("data", {})
        item_id = item.get('id', 'unknown')
        log.info(f"Created new item in {noun} with ID {item_id}")
        return item
    except httpx.HTTPError as e:
        log.error(f"Failed to create item in {noun}: {e}")
        return {}


def update_item(noun: str, item_id: str, payload: dict) -> dict:
    """
    Update an existing item via WOPR API.
    
    Args:
        noun: Resource type
        item_id: ID of item to update
        payload: Dict containing updated fields
    
    Returns:
        Updated item data, empty dict on failure
        
    Example:
        updated = update_item("sessions", "abc-123", {"status": "complete"})
    """
    url = f"{API_BASE}/api/v2/{noun}/{item_id}"
    try:
        response = httpx.patch(url, json=payload, timeout=10.0)
        response.raise_for_status()
        item = response.json().get("data", {})
        log.info(f"Updated item {item_id} in {noun}")
        return item
    except httpx.HTTPError as e:
        log.error(f"Failed to update {noun} {item_id}: {e}")
        return {}


def delete_item(noun: str, item_id: str) -> bool:
    """
    Delete an item via WOPR API.
    
    Args:
        noun: Resource type
        item_id: ID of item to delete
    
    Returns:
        True if successful, False on failure
        
    Warning:
        Deletion is permanent - no undo available
    """
    url = f"{API_BASE}/api/v2/{noun}/{item_id}"
    try:
        response = httpx.delete(url, timeout=10.0)
        response.raise_for_status()
        log.info(f"Deleted item {item_id} from {noun}")
        return True
    except httpx.HTTPError as e:
        log.error(f"Failed to delete {noun} {item_id}: {e}")
        return False

def get_config():
    url = f"{API_BASE}/api/v2/config/all"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        log.info(f"Config item {response.json()}")
        return response.json()
    except httpx.HTTPError as e:
        log.error(f"Failed to confg: {e}")
        return False

