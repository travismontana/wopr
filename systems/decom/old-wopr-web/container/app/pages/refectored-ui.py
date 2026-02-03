#!/usr/bin/env python3
"""
WOPR - Session Main Interface (Refactored)
==========================================
Separated into three layers:
1. Data Collection - fetch data, return dicts
2. Data Processing - transform data for display
3. Display - render UI components

Author: Bob
Date: 2026-01-19
"""

import streamlit as st
import httpx
import random
import re
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from helpers import *
import pandas as pd
from urllib.parse import urlparse, parse_qs, unquote

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "selected_game": None,
        "selected_session": None,
        "selected_session_id": None,
        "cache_loaded": [],
        "debug": False,
        "confirm_archive": False,
        "confirm_unarchive": False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()
debug = st.session_state.debug

# ============================================================================
# DATA COLLECTION LAYER
# ============================================================================
# Pure functions that fetch data and return dictionaries
# No UI side effects, no display code

def fetch_session_data(session_id: int) -> dict:
    """
    Collect all session-related data in one operation.
    
    Returns:
        dict: {
            'session_info': session record,
            'plays': list of play records,
            'games': list of all games
        }
    """
    log.info(f"Fetching session data for session_id: {session_id}")
    return {
        'session_info': get_one("session", session_id),
        'plays': get_session_plays(session_id),
        'games': get_all("games")
    }

def fetch_file_presence(session_id: int) -> dict:
    """
    Get file presence across all locations (incoming, archive, etc).
    
    Returns:
        dict: Celery task result with file locations and counts
    """
    log.info(f"Fetching file presence for session_id: {session_id}")
    presence = queue_session_task(session_id, "file_status")
    task_id = presence.get("task_id")
    
    if task_id and task_id != "N/A":
        log.info(f"Waiting for file status task: {task_id}")
        return wait_for_task(task_id)
    
    return presence

def fetch_label_studio_state(game_id: int) -> dict:
    """
    Get Label Studio project state for a specific game.
    
    Args:
        game_id: Game ID to match against Label Studio projects
    
    Returns:
        dict: Label Studio project with tasks, or None if not found
    """
    log.info(f"Fetching Label Studio state for game_id: {game_id}")
    ls_projects = get_label_studio_projects()
    
    if not ls_projects or not ls_projects.get("results"):
        log.warning("No Label Studio projects found")
        return None
    
    # Find project matching this game
    for project in ls_projects.get("results", []):
        description = project.get("description", "")
        match = re.search(r'<gameId:(\d+)>', description)
        
        if match and int(match.group(1)) == game_id:
            proj_id = project['id']
            log.info(f"Found matching Label Studio project: {project['title']} (ID: {proj_id})")
            
            # Fetch tasks for this project
            project['tasks'] = get_label_studio_projects_tasks(proj_id) or []
            return project
    
    log.info(f"No Label Studio project found for game_id: {game_id}")
    return None

def fetch_all_session_tasks() -> list:
    """
    Fetch all session tasks from the job queue.
    
    Returns:
        list: All session tasks
    """
    log.info("Fetching all session tasks")
    return all_session_tasks()

# ============================================================================
# ARCHIVE OPERATION DATA LAYER
# ============================================================================

def archive_session_files(session_id: int) -> dict:
    """
    Move files from incoming to archive.
    
    Returns:
        dict: Celery task result
    """
    log.info(f"Starting file archive for session_id: {session_id}")
    result = queue_session_task(session_id, "archive")
    task_id = result.get("task_id")
    
    if task_id and task_id != "N/A":
        log.info(f"Waiting for archive task: {task_id}")
        return wait_for_task(task_id)
    
    return result

def unarchive_session_files(session_id: int) -> dict:
    """
    Move files from archive back to incoming.
    
    Returns:
        dict: Celery task result
    """
    log.info(f"Starting file unarchive for session_id: {session_id}")
    result = queue_session_task(session_id, "unarchive")
    task_id = result.get("task_id")
    
    if task_id and task_id != "N/A":
        log.info(f"Waiting for unarchive task: {task_id}")
        return wait_for_task(task_id)
    
    return result

def update_play_records_status(session_id: int, plays: list, status: str) -> dict:
    """
    Update status for all plays in a session.
    
    Args:
        session_id: Session containing the plays
        plays: List of play records
        status: New status ('archived' or 'active')
    
    Returns:
        dict: {
            'status': 'success'|'partial'|'failed',
            'updated': list of updated play IDs,
            'failed': list of failed updates,
            'message': summary message
        }
    """
    log.info(f"Updating {len(plays)} play records to '{status}' status")
    payload = {"status": status}
    
    updated = []
    failed = []
    
    for play in plays:
        play_id = play['id']
        try:
            update_item("playtracker", play_id, payload)
            updated.append(play_id)
            log.debug(f"Updated play {play_id} to {status}")
        except Exception as e:
            log.error(f"Failed to update play {play_id}: {e}")
            failed.append({"play_id": play_id, "error": str(e)})
    
    status_result = "success" if not failed else ("partial" if updated else "failed")
    
    return {
        "status": status_result,
        "updated": updated,
        "failed": failed,
        "message": f"Updated {len(updated)} of {len(plays)} plays"
    }

def update_session_status(session_id: int, status: str) -> dict:
    """
    Update session status.
    
    Args:
        session_id: Session to update
        status: New status ('archived' or 'active')
    
    Returns:
        dict: {
            'status': 'success'|'failed',
            'message': description
        }
    """
    log.info(f"Updating session {session_id} to '{status}' status")
    payload = {"status": status}
    
    try:
        update_item("session", session_id, payload)
        return {
            "status": "success",
            "message": f"Session {session_id} set to {status}"
        }
    except Exception as e:
        log.error(f"Failed to update session {session_id}: {e}")
        return {
            "status": "failed",
            "message": str(e)
        }

# ============================================================================
# DATA PROCESSING LAYER
# ============================================================================
# Transform raw data into display-ready structures

def process_file_presence(raw_presence: dict) -> dict:
    """
    Transform file presence data into display-ready format.
    
    Args:
        raw_presence: Raw celery task result
    
    Returns:
        dict: {
            'locations': [{key, name, count, files}],
            'total': total file count
        }
    """
    if raw_presence.get('status') != 'success':
        log.warning(f"File presence check status: {raw_presence.get('status')}")
        return {'locations': [], 'total': 0}
    
    locations = []
    for location, files in raw_presence.get('result', {}).items():
        locations.append({
            'key': location,
            'name': location.replace('_', ' ').title(),
            'count': len(files),
            'files': files
        })
    
    total = sum(loc['count'] for loc in locations)
    log.info(f"Processed file presence: {total} files across {len(locations)} locations")
    
    return {
        'locations': locations,
        'total': total
    }

def process_label_tasks(tasks: list, session_uuid: str) -> dict:
    """
    Extract task info and filter by session UUID.
    
    Args:
        tasks: Raw Label Studio task list
        session_uuid: UUID to match against task filenames
    
    Returns:
        dict: {
            'all_tasks': simplified task list,
            'session_tasks': tasks belonging to this session,
            'session_count': number of session tasks
        }
    """
    log.info(f"Processing {len(tasks)} Label Studio tasks for session UUID: {session_uuid}")
    
    simplified = []
    for task in tasks:
        try:
            url = task['data']['image']
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            file_path = query_params.get('d', [''])[0]
            filename = unquote(file_path.split('/')[-1]) if file_path else 'unknown'
            
            simplified.append({
                'task_id': task['id'],
                'filename': filename,
                'is_labeled': task.get('is_labeled', False),
                'belongs_to_session': session_uuid in filename
            })
        except Exception as e:
            log.warning(f"Failed to process task {task.get('id')}: {e}")
    
    session_tasks = [t for t in simplified if t['belongs_to_session']]
    log.info(f"Found {len(session_tasks)} tasks for this session")
    
    return {
        'all_tasks': simplified,
        'session_tasks': session_tasks,
        'session_count': len(session_tasks)
    }

def execute_archive_operation(session_id: int, plays: list, direction: str) -> dict:
    """
    Execute complete archive or unarchive operation.
    
    Args:
        session_id: Session to operate on
        plays: List of play records
        direction: 'archive' or 'unarchive'
    
    Returns:
        dict: {
            'direction': operation direction,
            'files': file operation results,
            'plays': play update results,
            'session': session update results,
            'overall_status': 'success'|'failed'
        }
    """
    log.info(f"Executing {direction} operation for session {session_id}")
    
    target_status = "archived" if direction == "archive" else "active"
    file_operation = archive_session_files if direction == "archive" else unarchive_session_files
    
    results = {
        "direction": direction,
        "files": None,
        "plays": None,
        "session": None,
        "overall_status": "failed"
    }
    
    # Step 1: Move files
    log.info(f"Step 1/3: Moving files ({direction})")
    file_result = file_operation(session_id)
    results["files"] = file_result
    
    if file_result.get("status") != "success":
        log.error(f"File {direction} failed: {file_result.get('status')}")
        return results
    
    # Step 2: Update play records
    log.info(f"Step 2/3: Updating play records to {target_status}")
    play_result = update_play_records_status(session_id, plays, target_status)
    results["plays"] = play_result
    
    if play_result.get("status") not in ["success", "partial"]:
        log.error(f"Play record update failed")
        return results
    
    # Step 3: Update session
    log.info(f"Step 3/3: Updating session to {target_status}")
    session_result = update_session_status(session_id, target_status)
    results["session"] = session_result
    
    if session_result.get("status") == "success":
        results["overall_status"] = "success"
        log.info(f"{direction.title()} operation completed successfully")
    else:
        log.error(f"Session update failed")
    
    return results

# ============================================================================
# DISPLAY LAYER
# ============================================================================
# Pure UI rendering - receives data, displays it

def display_session_header(session_data: dict):
    """
    Render session header information in sidebar.
    
    Args:
        session_data: Output from fetch_session_data()
    """
    info = session_data['session_info']
    game = next((g for g in session_data['games'] if g['id'] == info['gameid']), None)
    game_name = game['name'] if game else 'Unknown'
    
    with st.sidebar:
        st.write(f":blue[**Name:**] {info.get('name', 'N/A')}")
        st.write(f":blue[**Status:**] {info.get('status', 'N/A')}")
        st.write(f":blue[**Game:**] {game_name}")
        st.write(f":blue[**Notes:**] {info.get('notes', 'N/A')}")

def display_file_presence(file_data: dict):
    """
    Render file presence metrics.
    
    Args:
        file_data: Output from process_file_presence()
    """
    if not file_data.get('locations'):
        st.warning("No file presence data available")
        return
    
    st.divider()
    st.subheader("File Presence Overview")
    
    cols = st.columns(len(file_data['locations']))
    for col, location in zip(cols, file_data['locations']):
        with col:
            st.metric(location['name'], location['count'])
            if location['files']:
                with st.expander("Files"):
                    for f in location['files']:
                        st.write(f"• {f}")

def display_label_studio_state(ls_data: dict, task_data: dict):
    """
    Render Label Studio project status.
    
    Args:
        ls_data: Label Studio project data
        task_data: Output from process_label_tasks()
    """
    if not ls_data:
        st.info("No Label Studio project found for this game")
        return
    
    st.success("Label Studio Project Found")
    st.write(f":gray[**Project Title:**] {ls_data['title']}")
    st.write(f":gray[**Project ID:**] {ls_data['id']}")
    st.write(f"Tasks from this session in project: {task_data['session_count']}")
    
    # Progress metrics
    total = ls_data.get('queue_total', 0)
    done = ls_data.get('queue_done', 0)
    finished = ls_data.get('finished_task_number', 0)
    
    if total == 0:
        st.subheader("Label Studio Task Progress")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Queue Total", total)
        with col2:
            pct = (done / total * 100)
            st.metric("Queue Done", done, delta=f"{pct:.1f}%")
        with col3:
            st.metric("Finished", finished)
        
        st.progress(done / total, text=f"{done} of {total} tasks completed")
        
        # Detailed chart
        chart_data = pd.DataFrame({
            "Count": [done, total - done, finished]
        }, index=["Completed", "Pending", "Finished"])
        st.bar_chart(chart_data)

def display_operation_results(results: dict):
    """
    Display results from archive/unarchive operation.
    
    Args:
        results: Output from execute_archive_operation()
    """
    direction = results["direction"]
    
    # Overall status banner
    if results["overall_status"] == "success":
        st.success(f"✓ {direction.title()} completed successfully")
    else:
        st.error(f"✗ {direction.title()} failed or incomplete")
    
    # File operation results
    with st.expander("📁 File Operations", expanded=True):
        if results["files"]:
            handle_celery_output(results["files"])
        else:
            st.warning("No file operation results")
    
    # Database operation results
    with st.expander("💾 Database Updates"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Play Records**")
            if results["plays"]:
                st.metric("Updated", len(results["plays"].get("updated", [])))
                if results["plays"].get("failed"):
                    st.error(f"Failed: {len(results['plays']['failed'])}")
                    for fail in results["plays"]["failed"]:
                        st.write(f"• Play {fail['play_id']}: {fail['error']}")
            else:
                st.warning("No play updates")
        
        with col2:
            st.write("**Session Record**")
            if results["session"]:
                if results["session"]["status"] == "success":
                    st.success(results["session"]["message"])
                else:
                    st.error(results["session"]["message"])
            else:
                st.warning("No session update")

def handle_celery_output(output: dict):
    """
    Display Celery task output with success/failure breakdown.
    
    Args:
        output: Celery task result
    """
    overall_status = output.get("status")
    result = output.get('result', {})
    successes = result.get('success', [])
    failures = result.get('failed', [])
    
    overallCol, successCol, failCol = st.columns(3)
    
    with overallCol:
        st.write(f"**Overall Status:** {overall_status}")
        if overall_status == "success":
            st.success("✓ Success")
        elif overall_status == "failed":
            st.error("✗ Failed")
        else:
            st.info(f"Status: {overall_status}")
    
    with successCol:
        num_success = len(successes)
        st.metric("Successful", num_success)
        if num_success > 0:
            with st.expander("Files"):
                for item in successes:
                    st.write(f"✓ {item}")
    
    with failCol:
        num_fail = len(failures)
        st.metric("Failed", num_fail)
        if num_fail > 0:
            with st.expander("Files"):
                for item in failures:
                    name = item.get('filename', 'unknown')
                    reason = item.get('error', 'unknown error')
                    st.write(f"**File:** {name}")
                    st.write(f"**Reason:** {reason}")
                    st.divider()

def display_archive_controls(session_id: int, plays: list, current_status: str):
    """
    Display archive or unarchive button with two-click confirmation.
    
    Args:
        session_id: Session to operate on
        plays: Play records for the session
        current_status: Current session status
    """
    # Determine operation based on current status
    is_archived = current_status == "archived"
    operation = "unarchive" if is_archived else "archive"
    button_icon = "📥" if is_archived else "🗄️"
    button_text = f"{button_icon} {operation.title()}"
    confirm_key = f"confirm_{operation}"
    
    # Initialize confirmation state
    if confirm_key not in st.session_state:
        st.session_state[confirm_key] = False
    
    # First click: show action button
    if not st.session_state[confirm_key]:
        if st.button(button_text, type="secondary", key=f"btn_{operation}"):
            st.session_state[confirm_key] = True
            st.rerun()
    
    # Second click: show confirmation
    else:
        st.warning(f"⚠️ Confirm {operation} operation?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"✓ Yes, {operation.title()}", type="primary", key=f"confirm_yes_{operation}"):
                # Execute the operation
                with st.spinner(f"{operation.title()}ing session..."):
                    results = execute_archive_operation(session_id, plays, operation)
                
                # Display results
                display_operation_results(results)
                
                # Clear cache and reset confirmation
                clear_session_cache()
                st.session_state[confirm_key] = False
                
                # Only rerun if successful (so user can see results)
                if results["overall_status"] == "success":
                    st.balloons()
                    time.sleep(2)  # Let them see the success
                    st.rerun()
        
        with col2:
            if st.button("✗ Cancel", key=f"confirm_no_{operation}"):
                st.session_state[confirm_key] = False
                st.rerun()

def display_jobs_table(tasks: list):
    """
    Display session tasks table.
    
    Args:
        tasks: List of session tasks
    """
    st.subheader("Jobs Interface")
    if tasks:
        st.table(tasks)
    else:
        st.info("No active tasks")

# ============================================================================
# CACHE MANAGEMENT
# ============================================================================

def clear_session_cache():
    """Clear all cached session data."""
    cache_keys = [
        'file_presence_cache',
        'label_studio_cache',
        'confirm_archive',
        'confirm_unarchive'
    ]
    for key in cache_keys:
        st.session_state.pop(key, None)
    
    log.info("Session cache cleared")

# ============================================================================
# UI ORCHESTRATION
# ============================================================================
# Main functions that coordinate data fetch, process, and display

def new_session():
    """Start a new session interface."""
    st.subheader("Start a New Session")
    st.write("Functionality to start a new session will go here.")

def jobs_interface():
    """Jobs management interface."""
    tasks = fetch_all_session_tasks()
    display_jobs_table(tasks)

def existing_session():
    """Main session view - orchestrate data collection and display."""
    # Get session selection from UI
    session_uuid, session = sessions_selectbox()
    session_id = session['id']
    
    # Update state
    st.session_state.selected_session = session_uuid
    st.session_state.selected_session_id = session_id
    
    log.info(f"Selected session: {session_uuid} (ID: {session_id})")
    
    # === DATA COLLECTION ===
    session_data = fetch_session_data(session_id)
    current_status = session_data['session_info']['status']
    
    # === DISPLAY HEADER ===
    display_session_header(session_data)
    
    st.divider()
    
    # === ARCHIVE CONTROLS ===
    display_archive_controls(session_id, session_data['plays'], current_status)
    
    st.divider()
    
    # === ADDITIONAL DATA (only if not archived) ===
    if current_status != "archived":
        # File presence (with caching)
        cache_key_files = 'file_presence_cache'
        if cache_key_files not in st.session_state:
            with st.spinner("Checking file presence..."):
                raw_presence = fetch_file_presence(session_id)
                file_data = process_file_presence(raw_presence)
                st.session_state[cache_key_files] = file_data
        else:
            file_data = st.session_state[cache_key_files]
        
        display_file_presence(file_data)
        
        st.divider()
        
        # Label Studio state (with caching)
        cache_key_ls = 'label_studio_cache'
        game_id = session_data['session_info']['gameid']
        
        if cache_key_ls not in st.session_state:
            with st.spinner("Checking Label Studio..."):
                ls_project = fetch_label_studio_state(game_id)
                if ls_project:
                    task_data = process_label_tasks(
                        ls_project.get('tasks', []),
                        session_uuid
                    )
                    st.session_state[cache_key_ls] = (ls_project, task_data)
                else:
                    st.session_state[cache_key_ls] = None
        
        if st.session_state[cache_key_ls]:
            ls_project, task_data = st.session_state[cache_key_ls]
            display_label_studio_state(ls_project, task_data)
        else:
            st.info("No Label Studio project found for this game")
        
        # Manual refresh button
        if st.button("🔄 Refresh Data", key="manual_refresh"):
            clear_session_cache()
            st.rerun()
    else:
        st.info("📦 Session is archived. Unarchive to view file and Label Studio status.")

# ============================================================================
# MAIN UI
# ============================================================================

st.set_page_config(layout="wide", page_title="WOPR Session Interface")
st.title("WOPR Session Interface")
st.write("Welcome to the WOPR Session Interface.")

# Debug toggle
debug_toggle = st.toggle("Activate debugging", value=st.session_state.debug)
st.session_state.debug = debug_toggle
debug = st.session_state.debug

# Main tab navigation
tabs = {
    "New Session": new_session,
    "Existing Session": existing_session,
    "Jobs": jobs_interface
}

lazy_tabs(tabs)
