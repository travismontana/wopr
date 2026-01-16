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

import streamlit as st
import httpx
import random
import re
import logging
import sys
from datetime import datetime
from pathlib import Path

API_BASE = "https://api.wopr.tailandtraillabs.org"

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
# Logic
# -------------------------

def setup_logger() -> logging.Logger:
	logger = logging.getLogger(LOGGER_NAME)
	if logger.handlers:
		return logger  # already configured

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

def get_random_phrase() -> str:
    return random.choice(PLAYPHRASES)

def get_all(noun) -> list:
    # this gets all of session|plays|games|pieces|etc from the API
    url = f"{API_BASE}/api/v2/{noun}"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        items = response.json()
        log.info(f"Fetched {len(items)} items from {noun}")
        return items
    except httpx.HTTPError as e:
        log.error(f"Error fetching {noun}: {e}")
        st.error(f"Failed to load {noun}: {e}")  # ← Show error in UI
        return []


def get_one(noun, item_id) -> dict:
    # this gets one of session|plays|games|pieces|etc from the API
    url = f"{API_BASE}/api/v2/{noun}/{item_id}"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        item = response.json().get("data", {})
        log.info(f"Fetched item {item_id} from {noun}")
        return item
    except httpx.HTTPError as e:
        log.error(f"Error fetching {noun} {item_id}: {e}")
        return {}

def create_new(noun, payload) -> dict:
    url = f"{API_BASE}/api/v2/{noun}"
    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        item = response.json().get("data", {})
        log.info(f"Created new item in {noun} with ID {item.get('id')}")
        return item
    except httpx.HTTPError as e:
        log.error(f"Error creating new item in {noun}: {e}")
        return {}

def update_item(noun, item_id, payload) -> dict:
    url = f"{API_BASE}/api/v2/{noun}/{item_id}"
    try:
        response = httpx.patch(url, json=payload, timeout=10.0)
        response.raise_for_status()
        item = response.json().get("data", {})
        log.info(f"Updated item {item_id} in {noun}")
        return item
    except httpx.HTTPError as e:
        log.error(f"Error updating item {item_id} in {noun}: {e}")
        return {}

def delete_item(noun, item_id) -> bool:
    url = f"{API_BASE}/api/v2/{noun}/{item_id}"
    try:
        response = httpx.delete(url, timeout=10.0)
        response.raise_for_status()
        log.info(f"Deleted item {item_id} from {noun}")
        return True
    except httpx.HTTPError as e:
        log.error(f"Error deleting item {item_id} from {noun}: {e}")
        return False