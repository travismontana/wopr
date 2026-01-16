#
#
# WOPR - Single Page Interface
# -------------------------
# idea: a single page interface that can interact with the WOPR API
# -------------------------

import streamlit as st
import httpx
import random
import re
import logging
import sys
from datetime import datetime
from pathlib import Path

# -------------------------
# Logging
# -------------------------
LOGGER_NAME = "wopr.singleplayer"

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

# -------------------------
# Streamlit UI
# -------------------------
st.title("WOPR Game Interface")
st.write("Welcome to the WOPR Game Interface.")

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

# ------------------------
# UI - Single Page - Logic
# -------------------------

def get_random_phrase() -> str:
    return random.choice(PLAYPHRASES)

def get_all(noun) -> list:
    # this gets all of session|plays|games|pieces|etc from the API
    url = f"{API_BASE}/api/v2/{noun}"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        items = response.json().get("data", [])
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

# -------------------------
#  UI - Single Page - Interface
# -------------------------

st.header("Single Page Interface")
mainselection = ["Sessions", "Plays", "Games", "Pieces", "Players"]
mainselection_dict = {
    "Sessions": "sessions",
    "Plays": "plays",
    "Games": "games",
    "Pieces": "pieces",
    "Players": "players"
}
mainsection = st.selectbox("Select Section", mainselection)
selected_noun = mainselection_dict[mainsection]
data = get_all(selected_noun)
st.json(data, expanded=False)

edited_data = st.data_editor(
    data, 
    num_rows="dynamic",
    key="data_editor_1"
)

#st.data_editor(data, height=300)

if st.button("Save Changes"):
    st.write("Saving changes...")
    for row in edited_data:
        item_id = row.get("id")
        if item_id:
            # existing item, update it
            update_item(selected_noun, item_id, row)
        else:
            # new item, create it
            create_new(selected_noun, row)
    st.success("Changes saved!")