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
    file_path = "/tmp/wopr.log"
    logger = logging.getLogger(LOGGER_NAME)
    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(logging.DEBUG)
    logging.FileHandler(file_path)
    handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    return logger


log = setup_logger()

#################################
#
# Start of the new openapi-pyton stuff
#
#################################


def logit(note, data):
    """_summary_

    Args:
        note (_type_): _description_
        data (_type_, optional): _description_. Defaults to None.
    """
    logger = setup_logger()
    logger.info(f"Note: ({note})")
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
        logit(f"Failed to list files in {directory}: {e}", "list_files")
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
