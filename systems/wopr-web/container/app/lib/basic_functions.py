"""
WOPR Frontend Helpers
Utility functions for Streamlit UI interactions with WOPR API.
"""

import streamlit as st
import httpx
import random
import re
import logging
import sys
from datetime import datetime
from pathlib import Path

# API configuration
API_BASE = "https://api.wopr.tailandtraillabs.org"
API_VERSION = "v2"

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
logger = log

# Image proxy and URL configurations
imgproxy = "http://imgproxy.wopr.tailandtraillabs.org/insecure/resize:fill:300/plain/https://images.wopr.tailandtraillabs.org/ml/incoming"
imgurl = "https://images.wopr.tailandtraillabs.org/ml/incoming"


# ------------------------
# Utility Functions
# ------------------------

def get_random_phrase() -> str:
    return random.choice(PLAYPHRASES)

# ------------------------
# CRUD Operations
# ------------------------

@st.cache_data()
def get_all(noun: str) -> list:
    url = f"{API_BASE}/api/v2/{noun}"
    response = do_api_things("get", API_BASE, noun, "", payload=None)
    return response

@st.cache_data()
def get_one(noun: str, item_id: str) -> dict:
    url = f"{API_BASE}/api/v2/{noun}/{item_id}"
    response = do_api_things("get", API_BASE, noun, item_id, payload=None)
    return response

@st.cache_data()
def create_new(noun: str, payload: dict) -> dict:
    url = f"{API_BASE}/api/v2/{noun}"
    response = do_api_things("post", API_BASE, noun, "", payload)
    return response.get("data", {})

@st.cache_data()
def update_item(noun: str, item_id: str, payload: dict) -> dict:
    url = f"{API_BASE}/api/v2/{noun}/{item_id}"
    response = do_api_things("patch", API_BASE, noun, item_id, payload)
    return response

@st.cache_data()
def delete_item(noun: str, item_id: str) -> bool:
    url = f"{API_BASE}/api/v2/{noun}/{item_id}"
    response = do_api_things("delete", API_BASE, noun, item_id,payload=None)
    return response

@st.cache_data()
def do_api_things(action, base_url, route, path, payload):
    headers = ""
    logger.info(
        f"Doing API things - "
        f"Action: {action}, "
        f"Base URL: {base_url}, "
        f"Route: {route}, "
        f"Path: {path}, "
        f"Headers: {headers}, "
        f"Payload: {payload}"
    )

    action_map = {
        "get": httpx.get,
        "post": httpx.post,
        "put": httpx.put,
        "delete": httpx.delete
    }
    
    method = action_map[action.lower()]
    logger.info(f"Using HTTP method: {method.__name__}")
    
    timeout = 30.0
    parts = [base_url, "api", API_VERSION, route, path]
    url = "/".join(p.strip('/') for p in parts if p)
    logger.info(f"Constructed URL: {url}")
    
    # Build request kwargs based on HTTP method
    kwargs = {"timeout": timeout, "headers": headers}
    
    if action.lower() in ["post", "put", "patch"] and payload:
        kwargs["json"] = payload
    elif action.lower() == "get" and payload:
        # If payload exists for GET, treat as query params
        kwargs["params"] = payload
    
    response = method(url, **kwargs)
    response.raise_for_status()
    result = response.json()
    logger.info(f"Response status code: {response}")
    logger.debug(response.text)
    
    return result

def get_config():
    return get_all("config")