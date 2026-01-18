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

imgproxy = "http://imgproxy.wopr.tailandtraillabs.org/insecure/resize:fill:300/plain/https://images.wopr.tailandtraillabs.org/ml/incoming"
imgurl = "https://images.wopr.tailandtraillabs.org/ml/incoming"

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
        item = response.json()
        log.info(f"Fetcdasdasdasshed item {item_id} from {noun} item: {response.json()}")
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

def games_selectbox():
    games = get_all("games")
    game_names = [game['name'] for game in games]
    selected_game = st.selectbox("Select a Game", game_names)
    return selected_game

def sessions_selectbox():
    sessions = get_all("sessions")
    session_uuid = [session['uuid'] for session in sessions]
    selected_session = st.selectbox("Select a Session", session_uuid)
    session = sessions[session_uuid.index(selected_session)]
    session_gameid = sessions[session_uuid.index(selected_session)]['gameid']
    log.info(f"Selected session ID: {session}")
    return selected_session, session

def get_session_plays(session_id):
    plays = get_all("plays")
    session_plays = [play for play in plays if play['sessionid'] == session_id]
    return session_plays

# In helpers.py

def lazy_tabs(tabs, default_tab=None, key_prefix="lazy_tab"):
    """
    Render tabs that only execute when selected.
    
    Args:
        tabs: dict of {"Tab Name": callable_function} or list of tuples
        default_tab: str, name of default tab (uses first if None)
        key_prefix: str, unique key for session state
    
    Example:
        tabs = {
            "New Session": new_session,
            "Existing Session": existing_session
        }
        lazy_tabs(tabs)
    """
    # Convert dict to list of tuples if needed (maintains order in 3.7+)
    if isinstance(tabs, dict):
        tab_list = list(tabs.items())
    else:
        tab_list = tabs
    
    tab_names = [name for name, _ in tab_list]
    tab_funcs = {name: func for name, func in tab_list}
    
    # Initialize state
    state_key = f"{key_prefix}_active"
    if state_key not in st.session_state:
        st.session_state[state_key] = default_tab or tab_names[0]
    
    # Render selector
    selected_tab = st.radio(
        "Mode",
        tab_names,
        horizontal=True,
        index=tab_names.index(st.session_state[state_key]),
        key=f"{key_prefix}_selector",
        label_visibility="collapsed"
    )
    
    # Update state and render
    st.session_state[state_key] = selected_tab
    
    # Call the selected function
    tab_funcs[selected_tab]()

# Add to helpers.py

# ------------------------
# Task Operations
# -------------------------

def queue_session_task(session_id: str, task_type: str = "archive") -> dict:
    """
    Queue a task for a session (currently supports 'archive').
    Returns task_id and status.
    """
    url = f"{API_BASE}/api/v2/session/task/{session_id}/{task_type}"
    try:
        response = httpx.post(url, timeout=10.0)
        response.raise_for_status()
        task_data = response.json()
        log.info(f"Queued {task_type} task for session {session_id}, task_id: {task_data.get('task_id')}")
        return task_data
    except httpx.HTTPError as e:
        log.error(f"Error queuing {task_type} task for session {session_id}: {e}")
        st.error(f"Failed to queue task: {e}")
        return {}


def get_task_status(task_id: str) -> dict:
    """
    Get current status of a task.
    Returns state, result, and progress info.
    """
    url = f"{API_BASE}/api/v2/session/task/{task_id}/status"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        status_data = response.json()
        log.info(f"Fetched status for task {task_id}: {status_data.get('state')}")
        return status_data
    except httpx.HTTPError as e:
        log.error(f"Error fetching status for task {task_id}: {e}")
        st.error(f"Failed to get task status: {e}")
        return {}


def revoke_task(task_id: str, terminate: bool = True) -> dict:
    """
    Revoke/cancel a running task.
    Set terminate=True to kill immediately, False for graceful stop.
    """
    url = f"{API_BASE}/api/v2/session/task/{task_id}/revoke"
    payload = {"terminate": terminate}
    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        revoke_data = response.json()
        log.info(f"Revoked task {task_id} (terminate={terminate})")
        return revoke_data
    except httpx.HTTPError as e:
        log.error(f"Error revoking task {task_id}: {e}")
        st.error(f"Failed to revoke task: {e}")
        return {}


def wait_for_task(task_id: str, timeout: int = 300) -> dict:
    """
    Block until task completes or timeout expires.
    Default timeout is 5 minutes (300s).
    """
    url = f"{API_BASE}/api/v2/session/task/{task_id}/wait"
    try:
        response = httpx.post(url, timeout=timeout + 5.0)  # Add buffer to HTTP timeout
        response.raise_for_status()
        result = response.json()
        log.info(f"Task {task_id} completed: {result.get('state')}")
        return result
    except httpx.TimeoutException:
        log.error(f"Task {task_id} timed out after {timeout}s")
        st.error(f"Task timed out after {timeout}s")
        return {"state": "TIMEOUT", "task_id": task_id}
    except httpx.HTTPError as e:
        log.error(f"Error waiting for task {task_id}: {e}")
        st.error(f"Failed to wait for task: {e}")
        return {}


def get_task_info(task_id: str) -> dict:
    """
    Get full task details including args, result, traceback, etc.
    """
    url = f"{API_BASE}/api/v2/session/task/{task_id}"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        task_info = response.json()
        log.info(f"Fetched info for task {task_id}")
        return task_info
    except httpx.HTTPError as e:
        log.error(f"Error fetching info for task {task_id}: {e}")
        st.error(f"Failed to get task info: {e}")
        return {}


def poll_task_until_complete(task_id: str, interval: int = 2, max_attempts: int = 150) -> dict:
    """
    Poll task status until completion. Non-blocking alternative to wait_for_task.
    Returns final task state.
    
    Args:
        task_id: The task to monitor
        interval: Seconds between polls (default 2s)
        max_attempts: Maximum polls before giving up (default 150 = 5min at 2s intervals)
    """
    import time
    
    for attempt in range(max_attempts):
        status = get_task_status(task_id)
        state = status.get('state', 'UNKNOWN')
        
        if state in ['SUCCESS', 'FAILURE', 'REVOKED']:
            log.info(f"Task {task_id} completed with state: {state}")
            return status
        
        time.sleep(interval)
    
    log.warning(f"Task {task_id} did not complete after {max_attempts} attempts")
    return {"state": "POLLING_TIMEOUT", "task_id": task_id}

def get_all_session_tasks(filter_state: str = None) -> list:
    """
    Get all tasks in the Celery queue.
    
    Args:
        filter_state: Optional state filter (PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED)
    
    Returns:
        List of task dicts with id, state, name, args, etc.
    """
    url = f"{API_BASE}/api/v2/session/tasks"
    params = {}
    if filter_state:
        params['state'] = filter_state
    
    try:
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        tasks = response.json()
        log.info(f"Fetched {len(tasks)} tasks from queue" + 
                 (f" (state={filter_state})" if filter_state else ""))
        return tasks
    except httpx.HTTPError as e:
        log.error(f"Error fetching tasks from queue: {e}")
        st.error(f"Failed to load tasks: {e}")
        return []