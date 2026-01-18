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

# Image proxy and URL configurations
imgproxy = "http://imgproxy.wopr.tailandtraillabs.org/insecure/resize:fill:300/plain/https://images.wopr.tailandtraillabs.org/ml/incoming"
imgurl = "https://images.wopr.tailandtraillabs.org/ml/incoming"


# ------------------------
# Utility Functions
# ------------------------

def get_random_phrase() -> str:
    """
    Select a random phrase from PLAYPHRASES.
    
    Returns:
        Random Dune/Terminator-themed phrase
    """
    return random.choice(PLAYPHRASES)


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
        st.error(f"Failed to load {noun}: {e}")
        st.stop()
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
        st.error(f"Failed to load {noun}: {e}")
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
        st.error(f"Failed to create {noun}: {e}")
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
        st.error(f"Failed to update {noun}: {e}")
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
        st.error(f"Failed to delete {noun}: {e}")
        return False


# ------------------------
# UI Helper Functions
# ------------------------

def games_selectbox() -> str:
    """
    Render a Streamlit selectbox for game selection.
    
    Returns:
        Name of selected game
        
    Note:
        Displays error in UI if games cannot be loaded
    """
    games = get_all("games")
    if not games:
        st.warning("No games available")
        return ""
    
    game_names = [game['name'] for game in games]
    selected_game = st.selectbox("Select a Game", game_names)
    log.debug(f"Game selected: {selected_game}")
    return selected_game


def sessions_selectbox() -> tuple:
    """
    Render a Streamlit selectbox for session selection.
    
    Returns:
        Tuple of (selected_session_uuid, session_dict)
        
    Note:
        Returns empty strings/dict if no sessions available
    """
    sessions = get_all("sessions")
    if not sessions:
        st.warning("No sessions available")
        return "", {}
    
    session_uuids = [session['uuid'] for session in sessions]
    selected_uuid = st.selectbox("Select a Session", session_uuids)
    
    # Find the full session object
    session = next((s for s in sessions if s['uuid'] == selected_uuid), {})
    
    log.info(f"Session selected: {selected_uuid}")
    return selected_uuid, session


def get_session_plays(session_id: str) -> list:
    """
    Retrieve all plays for a given session.
    
    Args:
        session_id: UUID of the session
    
    Returns:
        List of play dicts belonging to the session
        
    Note:
        Currently fetches all plays then filters client-side.
        May need optimization for large datasets.
    """
    plays = get_all("plays")
    session_plays = [play for play in plays if play.get('sessionid') == session_id]
    log.info(f"Found {len(session_plays)} plays for session {session_id}")
    return session_plays


def lazy_tabs(tabs, default_tab=None, key_prefix="lazy_tab"):
    """
    Render tabs that only execute content when selected.
    
    Args:
        tabs: Dict of {"Tab Name": callable_function} or list of tuples
        default_tab: Name of default tab (uses first if None)
        key_prefix: Unique key prefix for session state
    
    Returns:
        None - renders directly to Streamlit
        
    Example:
        tabs = {
            "New Session": new_session_func,
            "Existing Session": existing_session_func
        }
        lazy_tabs(tabs)
        
    Note:
        Uses session state to track active tab and prevent
        re-execution of inactive tab content.
    """
    # Convert dict to list of tuples if needed (maintains order in Python 3.7+)
    if isinstance(tabs, dict):
        tab_list = list(tabs.items())
    else:
        tab_list = tabs
    
    tab_names = [name for name, _ in tab_list]
    tab_funcs = {name: func for name, func in tab_list}
    
    # Initialize session state
    state_key = f"{key_prefix}_active"
    if state_key not in st.session_state:
        st.session_state[state_key] = default_tab or tab_names[0]
    
    # Render tab selector
    selected_tab = st.radio(
        "Mode",
        tab_names,
        horizontal=True,
        index=tab_names.index(st.session_state[state_key]),
        key=f"{key_prefix}_selector",
        label_visibility="collapsed"
    )
    
    # Update state and execute selected tab function
    st.session_state[state_key] = selected_tab
    log.debug(f"Active tab: {selected_tab}")
    
    # Call the selected function
    tab_funcs[selected_tab]()


# ------------------------
# Task Operations
# ------------------------

def queue_session_task(session_id: str, task_type: str = "archive") -> dict:
    """
    Queue a Celery task for a session.
    
    Args:
        session_id: UUID of the session to process
        task_type: Type of task to queue (currently supports 'archive')
    
    Returns:
        Dict containing task_id and status, empty dict on failure
        
    Example:
        result = queue_session_task("abc123", "archive")
        task_id = result.get('task_id')
    """
    url = f"{API_BASE}/api/v2/tasks/session/{session_id}/{task_type}"
    try:
        response = httpx.post(url, timeout=10.0)
        response.raise_for_status()
        task_data = response.json()
        log.info(f"Queued {task_type} task for session {session_id}, task_id: {task_data.get('task_id')}")
        return task_data
    except httpx.HTTPError as e:
        log.error(f"Failed to queue {task_type} task for session {session_id}: {e}")
        st.error(f"Failed to queue task: {e}")
        return {}


def get_task_status(task_id: str) -> dict:
    """
    Retrieve current status of a queued task.
    
    Args:
        task_id: The Celery task ID to check
    
    Returns:
        Dict containing state, result, and progress information
        Empty dict if request fails
        
    States:
        PENDING: Not started or doesn't exist
        STARTED: Currently executing
        SUCCESS: Completed successfully
        FAILURE: Failed with error
        RETRY: Retrying after failure
        REVOKED: Cancelled by user
    """
    url = f"{API_BASE}/api/v2/tasks/session/{task_id}/status"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        status_data = response.json()
        log.info(f"Retrieved status for task {task_id}: {status_data.get('state', 'UNKNOWN')}")
        return status_data
    except httpx.HTTPError as e:
        log.error(f"Failed to fetch status for task {task_id}: {e}")
        st.error(f"Failed to get task status: {e}")
        return {}


def revoke_task(task_id: str, terminate: bool = True) -> dict:
    """
    Cancel a running or queued task.
    
    Args:
        task_id: The Celery task ID to revoke
        terminate: If True, sends SIGTERM to worker (immediate kill)
                   If False, graceful shutdown (waits for current operation)
    
    Returns:
        Dict with revocation status, empty dict on failure
        
    Warning:
        terminate=True may leave resources in inconsistent state.
        Use terminate=False for graceful cancellation when possible.
    """
    url = f"{API_BASE}/api/v2/tasks/session/{task_id}/revoke"
    payload = {"terminate": terminate}
    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        revoke_data = response.json()
        log.info(f"Revoked task {task_id} (terminate={terminate})")
        return revoke_data
    except httpx.HTTPError as e:
        log.error(f"Failed to revoke task {task_id}: {e}")
        st.error(f"Failed to revoke task: {e}")
        return {}


def wait_for_task(task_id: str, timeout: int = 300) -> dict:
    """
    Block until task completes or timeout expires.
    
    Args:
        task_id: The Celery task ID to wait for
        timeout: Maximum seconds to wait (default 300 = 5 minutes)
    
    Returns:
        Dict with final state and result
        Returns {"state": "TIMEOUT"} if timeout expires
        
    Warning:
        Blocking operation - UI will freeze during wait.
        Consider poll_task_until_complete() for non-blocking alternative.
    """
    url = f"{API_BASE}/api/v2/tasks/session/{task_id}/wait"
    try:
        response = httpx.post(url, timeout=timeout + 5.0)  # Buffer for HTTP overhead
        response.raise_for_status()
        result = response.json()
        log.info(f"Task {task_id} completed: {result.get('state', 'UNKNOWN')}")
        return result
    except httpx.TimeoutException:
        log.warning(f"Task {task_id} exceeded timeout of {timeout}s")
        st.error(f"Task timed out after {timeout}s")
        return {"state": "TIMEOUT", "task_id": task_id}
    except httpx.HTTPError as e:
        log.error(f"Failed waiting for task {task_id}: {e}")
        st.error(f"Failed to wait for task: {e}")
        return {}


def get_task_info(task_id: str) -> dict:
    """
    Retrieve detailed task metadata and execution information.
    
    Args:
        task_id: The Celery task ID to inspect
    
    Returns:
        Dict containing:
            - name: Task function name
            - args: Positional arguments passed to task
            - kwargs: Keyword arguments passed to task
            - state: Current execution state
            - result: Return value if completed
            - traceback: Error traceback if failed
            - completed_at: Timestamp of completion
        Empty dict on failure
    """
    url = f"{API_BASE}/api/v2/tasks/session/{task_id}"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        task_info = response.json()
        log.info(f"Retrieved info for task {task_id}: {task_info.get('name', 'unknown')}")
        return task_info
    except httpx.HTTPError as e:
        log.error(f"Failed to fetch info for task {task_id}: {e}")
        st.error(f"Failed to get task info: {e}")
        return {}


def poll_task_until_complete(task_id: str, interval: int = 2, max_attempts: int = 150) -> dict:
    """
    Poll task status until completion. Non-blocking alternative to wait_for_task.
    
    Args:
        task_id: The task to monitor
        interval: Seconds between status checks (default 2s)
        max_attempts: Maximum polls before giving up (default 150 = 5min @ 2s intervals)
    
    Returns:
        Final task state dict when completed or polling timeout
        
    Note:
        Unlike wait_for_task(), this allows UI updates between polls.
        Still blocks execution but permits Streamlit to remain responsive.
    """
    import time
    
    log.info(f"Starting polling for task {task_id} (interval={interval}s, max_attempts={max_attempts})")
    
    for attempt in range(max_attempts):
        status = get_task_status(task_id)
        state = status.get('state', 'UNKNOWN')
        
        if state in ['SUCCESS', 'FAILURE', 'REVOKED']:
            log.info(f"Task {task_id} completed after {attempt + 1} polls with state: {state}")
            return status
        
        log.debug(f"Task {task_id} still running ({state}), poll {attempt + 1}/{max_attempts}")
        time.sleep(interval)
    
    log.warning(f"Task {task_id} polling timeout after {max_attempts} attempts ({max_attempts * interval}s)")
    return {"state": "POLLING_TIMEOUT", "task_id": task_id}


def all_session_tasks(filter_state: str = None) -> list:
    """
    Retrieve all tasks currently in Celery queue.
    
    Args:
        filter_state: Optional state filter (active, scheduled, reserved)
                     Case-insensitive, gets uppercased for API
    
    Returns:
        List of task dicts containing:
            - task_id: Unique task identifier
            - name: Task function name
            - state: Current state (ACTIVE, SCHEDULED, RESERVED)
            - worker: Worker hostname processing the task
            - args: Task arguments
            - kwargs: Task keyword arguments
            - eta: Scheduled execution time (for SCHEDULED tasks)
        Empty list on failure
        
    Limitations:
        Only returns tasks visible to currently running workers.
        Completed tasks (SUCCESS/FAILURE) are not included unless
        specifically persisted by result backend.
        
    Example:
        # Get all tasks
        all_tasks = all_session_tasks()
        
        # Get only actively executing tasks
        active = all_session_tasks(filter_state="active")
    """
    url = f"{API_BASE}/api/v2/tasks/session"
    params = {}
    if filter_state:
        params['state'] = filter_state.upper()
        log.debug(f"Filtering tasks by state: {filter_state.upper()}")
    
    try:
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        tasks = response.json()
        
        task_count = len(tasks)
        filter_msg = f" (filtered: {filter_state})" if filter_state else ""
        log.info(f"Retrieved {task_count} task(s) from queue{filter_msg}")
        
        return tasks
    except httpx.HTTPError as e:
        log.error(f"Failed to fetch tasks from queue: {e}")
        st.error(f"Failed to load tasks: {e}")
        return []

def session_image_status(session_id: str) -> list:
    """
    Get the status of all the images for a session.
    
    Args:
        session_id: The session to monitor
    
    Returns:
        List of file status dicts containing:
            - filename: Name of the image file
            - status: Current processing status (pending, processed, error)
            - processed_at: Timestamp of processing completion
        Empty list on failure
        
    Limitations:
        Only returns tasks visible to currently running workers.
        Completed tasks (SUCCESS/FAILURE) are not included unless
        specifically persisted by result backend.
        
    Example:
        # Get all tasks
        all_tasks = all_session_tasks()
        
        # Get only actively executing tasks
        active = all_session_tasks(filter_state="active")
    """
    url = f"{API_BASE}/api/v2/tasks/session/{session_id}/file_status"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        file_statuses = response.json()
        
        log.info(f"Retrieved file statuses for session {session_id}, count: {len(file_statuses)}")
        
        return file_statuses
    except httpx.HTTPError as e:
        log.error(f"Failed to fetch file statuses for session {session_id}: {e}")
        st.error(f"Failed to load file statuses: {e}")
        return []

def copy_files_to_source(session_id: str) -> dict:
    """
    Queue a task to copy session files to label studio source directory.
    
    Args:
        session_id: UUID of the session to process
    
    Returns:
        Dict containing task_id and status, empty dict on failure
        
    Example:
        result = copy_files_to_source("abc123")
        task_id = result.get('task_id')
    """
    url = f"{API_BASE}/api/v2/tasks/session/{session_id}/copy_to_label_source"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        task_data = response.json()
        log.info(f"Queued copy_to_label_source task for session {session_id}, task_id: {task_data.get('task_id')}")
        return task_data
    except httpx.HTTPError as e:
        log.error(f"Failed to queue copy_to_label_source task for session {session_id}: {e}")
        st.error(f"Failed to queue task: {e}")
        return {}