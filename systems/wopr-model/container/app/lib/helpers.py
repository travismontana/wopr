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

API_BASE = "https://api.wopr.tailandtraillabs.org"


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

    logger.setLevel(logging.DEBUG)

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
    log.info(f"Fetching {noun} with ID {item_id} from {url}")
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
    """_summary_

    Returns:
        _type_: _description_
    """
    url = f"{API_BASE}/api/v2/config/all"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        log.info(f"Config item {response.json()}")
        return response.json()
    except httpx.HTTPError as e:
        log.error(f"Failed to confg: {e}")
        return False

#################################
#
# Start of the new openapi-pyton stuff
#
#################################


def update_operations(data, note, extradata, status):
    """_summary_

    Args:
        data (_type_): _description_
        note (_type_): _description_
        extradata (_type_): _description_
        status (_type_): _description_

    Returns:
        _type_: _description_
    """
    logit(
        "Updating ops",
        f"Data: {data}, Note: {note}, ExtraData: {extradata}, Status: {status}",
    )

    caller = inspect.stack()[1].function
    operation = {
        "task": caller,
        "data": data.model,
        "note": note,
        "extradata": extradata,
        "status": status,
    }

    data.operations.append(operation)
    return data


def logit(note, data=None):
    """_summary_

    Args:
        note (_type_): _description_
        data (_type_, optional): _description_. Defaults to None.
    """
    logger = setup_logger()
    logger.info(f"({note})")
    if not data:
        data = note
    logger.debug(f"Data: ({data})")


def list_files(protected_path, directory):
    """_summary_

    Args:
        potected_path (_type_): _description_
        directory (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        return protected_path.listdir(directory)
    except Exception as e:
        logit(f"Failed to list files in {directory}: {e}")
        return []


def check_for_file_in_dir(filename, directory, protected_path):
    """_summary_

    Args:
        filename (_type_): _description_
        directory (_type_): _description_
        protected_path (_type_): _description_

    Returns:
        _type_: _description_
    """
    logit(
        "Checking for file in directory", {"filename": filename, "directory": directory}
    )
    files = list_files(protected_path, directory)
    for file in files:
        if file == filename:
            return True
    return False


async def download_file(url, filename, paths):
    """_summary_

    Args:
        url (_type_): _description_
        filename (_type_): _description_
        paths (_type_): _description_

    Returns:
        _type_: _description_
    """
    timeout = 30.0
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            async with client.stream("GET", url) as response:
                # ← ADDED: Check response status
                response.raise_for_status()

                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(fullpath, "wb") as file:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        file.write(chunk)
                        downloaded += len(chunk)

                logger.info(f"Downloaded {downloaded} bytes to {fullpath}")
                data.downloaded = True

    except httpx.HTTPStatusError as e:
        logit(f"HTTP error downloading {url}: {e}")
        return e

    except Exception as e:
        logit(f"Error downloading {url}: {e}")
        return e

    return d


def copy_file_to_dist(filename, paths, protected_path):
    """_summary_

    Args:
        filename (_type_): _description_
        paths (_type_): _description_
    """
    logit(f"Copying file {filename} to dist directory")
    base_path = paths["models_path"]
    dist_subdir = paths["models_distfiles_path"]
    down_subdir = paths["models_download_path"]
    distfile = f"{dist_subdir}/{filename}"
    downfile = f"{down_subdir}/{filename}"
    logit(f"Copying from {downfile} to {distfile}")
    return protected_path.copy_file(downfile, distfile)


def copy_modfam_to_model(filename, model_filename, paths, protected_path):
    """_summary_

    Args:
        filename (_type_): _description_
        model_filename (_type_): _description_
        paths (_type_): _description_
        protected_path (_type_): _description_
    """
    logit(f"Copying from {filename} to {model_filename}")
    base_path = paths["models_path"]
    dist_sub = paths["models_distfiles_path"]
    model_file = f"{dist_sub}/{model_filename}"
    modfam_file = f"{dist_sub}/{filename}"
    return protected_path.copy_file(modfam_file, model_file)


def backup_dist_file(filename, paths, protected_path):
    """_summary_

    Args:
        filename (_type_): _description_
        paths (_type_): _description_
        protected_path (_type_): _description_
    """
    logit(f"Backing up file {filename}")
    base_path = paths["models_path"]
    dist_sub = paths["models_distfiles_path"]
    down_sub = paths["models_download_path"]
    source = f"{dist_sub}/{filename}"
    dest = f"{down_sub}/{filename}"
    return protected_path.copy_file(source, dest)
