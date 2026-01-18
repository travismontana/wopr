#
#
# WOPR - Session Main Interface
# -------------------------
# idea: 1 page to see existing sessions and their plays, and create new sessions
# -------------------------

import streamlit as st
import httpx
import random
import re
import logging
import sys
from datetime import datetime
from pathlib import Path
from helpers import *



if "selected_game" not in st.session_state:
	st.session_state.selected_game = None
if "selected_session" not in st.session_state:
	st.session_state.selected_session = None
if "selected_session_id" not in st.session_state:
	st.session_state.selected_session_id = None

# -------------------------
# Streamlit UI
# -------------------------
st.title("WOPR Session Interface")
st.write("Welcome to the WOPR Session Interface.")

def new_session():
    st.subheader("Start a New Session")
    st.write("Functionality to start a new session will go here.")

def archive_play_records(session_id: str, plays: list):
    log.info(f"Archiving play records for session ID: {session_id}")
    payload = {
        "status": "archived"
    }
    log.info(f"Updating {len(plays)} plays to archived status.")
    for play in plays:
        play_id = play['id']
        log.info(f'update_item("playtracker", {play_id}, {payload})')
        update_item("playtracker", play_id, payload)
    return {"status": "success", "message": f"Archived {len(plays)} plays."}

def archive_session(session_id: str):
    log.info(f"Archiving session ID: {session_id}")
    payload = {
        "status": "archived"
    }
    log.info(f'update_item("session", {session_id}, {payload})')
    update_item("session", session_id, payload)
    return {"status": "success", "message": f"Archived session {session_id}."}

def jobs_interface():
    st.subheader("Jobs Interface")
    st.write("Functionality for managing and viewing jobs will go here.")
    st.table(all_session_tasks())

def session_management():
    st.subheader("Session Management")
    st.write("Functionality for session management will go here.")
    current_session_id = st.session_state.get("selected_session_id", None)
    current_session_uuid = st.session_state.get("selected_session", None)
    log.info(f"Current Session ID from state: {current_session_id}")
    log.info(f"Current Session UUID from state: {current_session_uuid}")
    session_info = get_one("session", current_session_id) if current_session_id else None
    if current_session_id:
        plays = get_session_plays(current_session_id)
        log.info(f"Number of Plays in this Session: {len(plays)}")
    games = get_all("games")
    game_id = session_info['gameid'] if session_info else None
    log.info(f"Game ID for this Session: {game_id}")
    game_name = games[game_id]['name'] if game_id and game_id < len(games) else "Unknown"
    session_uuid = session_info['uuid'] if session_info else "N/A"
    status = session_info['status'] if session_info else "N/A"
    headerCol, infoCol = st.columns([1, 3])
    with headerCol:
        st.write("Game Name: ")
        st.write("Number of Plays:")
        st.write("Status:")
        st.write("Session UUID:")
    with infoCol:
        st.write(game_name)
        st.write(len(plays))
        st.write(status)
        st.write(session_uuid)
    # Initialize session state
    if status != "archived":
        if 'confirm_archive' not in st.session_state:
            st.session_state.confirm_archive = False
        # First click: show confirmation
        if not st.session_state.confirm_archive:
            if st.button("🗄️ Archive", type="secondary"):
                st.session_state.confirm_archive = True
                st.rerun()

        # Confirmation state: show warning and confirm button
        else:
            st.warning("⚠️ Confirm archive operation?")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✓ Yes, Archive", type="primary"):
                    # DO THE ARCHIVE THING HERE
                    image_archive_results = queue_session_task(current_session_id, "archive")
                    task_id = image_archive_results.get("task_id", "N/A")
                    log.info(f"Queued image archive task with ID: {task_id}")
                    if task_id != "N/A":
                        image_archive_final_results = wait_for_task(task_id)
                    log.info(f"Image archive task completed with results: {image_archive_results}")
                    db_archive_results = archive_play_records(current_session_id, plays)
                    log.info(f"Database archive completed with results: {db_archive_results}")
                    session_archive_results = archive_session(current_session_id)
                    log.info(f"Session archive completed with results: {session_archive_results}")
                    st.success("Archived!")
                    st.session_state.confirm_archive = False
                    st.rerun()
            
            with col2:
                if st.button("✗ Cancel"):
                    st.session_state.confirm_archive = False
                    st.rerun()

def ml_files():
    st.subheader("ML Files")
    presence = queue_session_task(st.session_state.selected_session_id, "file_status")
    task_id = presence.get("task_id", "N/A")
    log.info(f"Queued file status task with ID: {task_id}")
    if task_id != "N/A":
        presence = wait_for_task(task_id)
    log.info(f"File status task completed with results: {presence}")
    formatted_data = []
    if st.button("Copy files to source"):
        results = copy_files_to_source(st.session_state.selected_session_id)
        log.info(f"Copy files to source completed with results: {results}")
        task_id = results.get("task_id", "N/A")
        results2 = None
        if task_id != "N/A":
            results2 = wait_for_task(task_id)
            log.info(f"File copy task completed with results: {results2}")
            st.success("Files copied to source.")
            formatted_data_files = handle_celery_output(results2)
    status = presence['status']
    if status == 'success':
        for location in presence['result']:
            formatted_data.append({
                "loc": location,
                "locname": location.replace('_', ' ').title(),
                "count": len(presence['result'][location]),
                "files": presence['result'][location]
            })
        log.info(f"Formatted file presence data: {formatted_data}")
        if len(formatted_data) > 0:
            st.divider()
            st.subheader("File Presence Overview")
            cols = st.columns(len(formatted_data))
            for col, item in zip(cols, formatted_data):
                with col:
                    st.metric(item['locname'], item['count'])
                    if item['files']:
                        with st.expander("Files"):
                            st.write(item['files'])
    else:
        st.write("No files found")

def  handle_celery_output(output):
    #st.json(output)
    overall_status = output.get("status")
    successes = output['result']['success']
    failures = output['result']['failed']

    # Do the display:
    overallCol,successCol,failCol = st.columns(3)
    with overallCol:
        st.write(f"Overall Status: {overall_status}")
        if overall_status == "success":
            st.badge("Success", color="green")
        elif overall_status == "failed":
            st.badge("Failed", color="red")
        else:
            st.badge("Unknown")
    with successCol:
        num_success = len(successes)
        st.metric("Successful", num_success)
        if num_success > 0:
            with st.expander("Files"):
                st.table(successes)
    with failCol:
        num_fail = len(failures)
        st.metric("Failed", num_fail)
        if num_fail > 0:
            with st.expander("Files"):
                for item in failures:
                    name = item.get('filename')
                    reason = item.get('error')
                    st.write(f"File: {name}")
                    st.write(f"Reason: {reason}")
                    st.divider()
                #st.table(failures)
                
    return 0

def play_walkthrough(plays, players):
    log.info(f"Starting Play Walkthrough with {len(plays)} plays Players: {len(players)}.")
    play_data_dict = []
    for play in plays:
        playername = next((player['name'] for player in players if player['id'] == play['playerid']), "Unknown Player")
        playimagefile = play.get('filename', 'No Image')
        playimagethumb = f"{imgproxy}/{playimagefile}"
        playimagefull = f"{imgurl}/{playimagefile}"
        playnote = play.get('note', 'No Description')
        playid = play.get('id', 'No ID')
        
        row = {
            "Play ID": playid,
            "Player": playername,
            "Note": playnote,
            "Image": playimagefile
        }
        play_data_dict.append(row)

        colId, colPlayer, colNote, colImage = st.columns([1, 2, 4, 4])
        with colId:
            st.write(playid)
        with colPlayer:
            st.write(playername)
        with colNote:
            st.write(playnote)
        with colImage:
            st.image(playimagethumb, caption=playnote)
            st.markdown(f"[Full Image]({playimagefull})")

def existing_session():
    st.subheader("Work an Existing Session")
    games = get_all("games")
    log.info(f"Fetched {len(games)} games from backend.")
    players = get_all("players")
    log.info(f"Fetched {len(players)} players from backend.")
    
    session_uuid, session = sessions_selectbox()
    log.info(f"Selected session from UI: {session_uuid}")
    session_id = session['id']
    log.info(f"Session ID resolved: {session_id}")
    st.session_state.selected_session = session_uuid
    st.session_state.selected_session_id = session_id
    log.info(f"Session selected in UI: {st.session_state.selected_session} with ID {st.session_state.selected_session_id}")
    plays = get_session_plays(st.session_state.selected_session_id)
    gamename = games[0]['name'] if games else "Unknown"
    st.write(f"Session Game: {gamename}")
    sessionstatus = get_session_status(st.session_state.selected_session_id)
    st.write(f"Session Status: {sessionstatus}")
    sesstabs = {
        "Session Management": session_management,
        "ML Files": ml_files,
        "Play Walkthrough": lambda: play_walkthrough(plays, players)
    }
    lazy_tabs(sesstabs, key_prefix="session_tabs")

def get_session_status(session_id):
    log.info(f"Fetching status for session ID: {session_id}")
    return get_one("sessions", session_id)["status"]

# -------------------------
#  UI - Single Page - Interface
# -------------------------
 
tabs = {
    "New Session": new_session,
    "Existing Session": existing_session,
    "Jobs": jobs_interface
}

lazy_tabs(tabs)