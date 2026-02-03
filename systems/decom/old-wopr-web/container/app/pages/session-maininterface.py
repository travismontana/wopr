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
import pandas as pd
from urllib.parse import urlparse, parse_qs, unquote



if "selected_game" not in st.session_state:
	st.session_state.selected_game = None
if "selected_session" not in st.session_state:
	st.session_state.selected_session = None
if "selected_session_id" not in st.session_state:
	st.session_state.selected_session_id = None
if "cache_loaded" not in st.session_state:
    st.session_state.cache_loaded = []
if "debug" not in st.session_state:
    st.session_state.debug = False

debug = st.session_state.debug
# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(layout="wide", page_title="WOPR Session Interface")
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

def get_file_presence(session_id):
    presence = queue_session_task(session_id, "file_status")
    task_id = presence.get("task_id", "N/A")
    log.info(f"Queued file status task with ID: {task_id}")
    if task_id != "N/A":
        presence = wait_for_task(task_id)
    log.info(f"File status task completed with results: {presence}")
    
    return presence

def copy_files_to_source(session_id):
    results = copy_files_to_source(st.session_state.selected_session_id)
    log.info(f"Copy files to source completed with results: {results}")
    task_id = results.get("task_id", "N/A")
    results2 = None
    if task_id != "N/A":
        results2 = wait_for_task(task_id)
        log.info(f"File copy task completed with results: {results2}")
        st.success("Files copied to source.")
        formatted_data_files = handle_celery_output(results2)


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

def play_walkthrough():
    log.info(f"Starting Play Walkthrough with {len(plays)} plays Players: {len(players)}.")
    players = get_all("players")
    plays = get_all("plays", session_id)
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

def process_management():
    log.info("Process management interface accessed.")
    load_into_labeler_status = "workin on it"
    load_into_project_dataset_status = "workin on it"
    st.write(f":gray[Load into label studio status:] {load_into_labeler_status}")
    st.write(f":gray[Load into project dataset status:] {load_into_project_dataset_status}")
    pass

# Jobs approach
# 
# status is stored in the db
# 
# 
#
def get_process_states(session_info):
    log.info(f"Getting process states for session_id: {session_info['ID']}")
    log.debug(f"Session Info: {session_info}")
    if debug:
        st.write(f"Session Info: {session_info}")
    
    # Get Label Studio projects
    ls_projects = get_label_studio_projects()
    log.info(f"Received: {ls_projects}")
    if debug:
        st.write("is_projects")
        #st.json(ls_projects)
    
    num_proj = ls_projects.get("count", 0)
    if debug:
        st.write(f"Number of projects: {num_proj}")
    
    # Find project matching session's game ID
    # Note: session_info doesn't have GameID, need to add it or get from session
    # Assuming you'll add it to session_info dict
    target_game_id = session_info.get("GameID")  # Add this to session_info creation
    
    if not target_game_id:
        log.warning("No GameID in session_info")
        return ls_projects
    
    matching_project = None
    for project in ls_projects.get("results", []):
        description = project.get("description", "")
        # Extract gameId from description like "<gameId:4>"
        match = re.search(r'<gameId:(\d+)>', description)
        if match:
            project_game_id = int(match.group(1))
            log.debug(f"Project {project['id']} has gameId: {project_game_id}")
            if project_game_id == target_game_id:
                matching_project = project
                log.info(f"Found matching project: {project['title']} (ID: {project['id']})")
                break
    
    if debug and matching_project:
        st.success(f"Matched Label Studio project: {matching_project['title']}")
        st.json(matching_project)
    elif debug:
        st.warning(f"No Label Studio project found for gameId: {target_game_id}")
    
    return matching_project

def process_proj_tasks(proj_tasks):
    logger.info("Processing project tasks")
    logger.debug(f"Project tasks data: {proj_tasks}")
    if debug:
        st.write("Processing project tasks")
        #st.json(proj_tasks)
    simplified_tasks= []
    for task in proj_tasks:
        task_id = task['id']
        url = task['data']['image']
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        file_path = query_params['d'][0]  # 'labelstudio/source/game-...-play2.jpg'
        filename = unquote(file_path.split('/')[-1])  
        task_is_labeled = task['is_labeled']
        simplified_tasks.append({
            "task_id": task_id,
            "filename": filename,
            "is_labeled": task_is_labeled
        })
    return simplified_tasks

def process_states_display(session_info,process_states, file_presence):
    if debug:
        st.write("in process_states_display")
        #st.json(process_states)
    proj_id = process_states.get("id") if process_states else None
    proj_title = process_states.get("title") if process_states else None
    proj_tasks_queue_total = process_states.get("queue_total") if process_states else None
    proj_tasks_queue_done = process_states.get("queue_done") if process_states else None
    proj_tasks_finished_tasks = process_states.get("finished_task_number") if process_states else None

    proj_tasks = get_label_studio_projects_tasks(proj_id) if proj_id else None
    #if debug:
        #st.json(proj_tasks)
    simplified_tasks = process_proj_tasks(proj_tasks)
    if debug:
        st.write("Simplified Tasks and File Presence")
        #st.json(simplified_tasks)
        #st.json(file_presence)
    
    st.success("A Label Studio Project Found")
    st.write(f":gray[**Project Title:**] {proj_title}")
    st.write(f":gray[**Project Id:**] {proj_id}")

    is_game_in_tasks = is_game_in_tasks_check(simplified_tasks, session_info.get("UUID"))
    if debug:
        st.write("is_game_in_tasks")
        st.json(is_game_in_tasks)
    num_session_in_tasks = len(is_game_in_tasks) if isinstance(is_game_in_tasks, list) else 0
    st.write(f"Number of images from this session in the project tasks: {num_session_in_tasks}")

    # are there files in the file_presence that match the game uuid

def is_game_in_tasks_check(simplified_tasks,session_uuid):
    logger.info(f"Checking if game UUID {session_uuid} is in tasks")
    results = []
    for task in simplified_tasks:
        if session_uuid in task['filename']:
            logger.info(f"Found game UUID {session_uuid} in task {task['task_id']}")
            results.append({
                "filename": task['filename'],
                "task_id": task['task_id']
            })
    if results:
        return results
    else: 
        logger.info(f"Session UUID {session_uuid} not found in any task")
        return 1

def process_states_display2(process_states):
    if debug:
        st.write("in process_states_display")
        #st.json(process_states)
    proj_id = process_states.get("id") if process_states else None
    proj_title = process_states.get("title") if process_states else None
    proj_tasks_queue_total = process_states.get("queue_total") if process_states else None
    proj_tasks_queue_done = process_states.get("queue_done") if process_states else None
    proj_tasks_finished_tasks = process_states.get("finished_task_number") if process_states else None

    st.success("Label Studio Project Found")
    st.write(f":gray[**Project Title:**] {proj_title}")
    st.write(f":gray[**Project Id:**] {proj_id}")
    total = proj_tasks_queue_total or 0
    done = proj_tasks_queue_done or 0
    finished = proj_tasks_finished_tasks or 0

    st.subheader("Label Studio Task Progress")

    # Top row: metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Queue Total", total)
    with col2:
        pct = (done/total*100) if total > 0 else 0
        st.metric("Queue Done", done, delta=f"{pct:.1f}%")
    with col3:
        st.metric("Finished", finished)

    # Progress bar
    if total > 0:
        st.progress(done / total, text=f"{done} of {total} tasks completed")
        
        # Detailed chart
        chart_data = pd.DataFrame({
            "Count": [done, total - done, finished]
        }, index=["Completed", "Pending", "Finished"])
        st.bar_chart(chart_data)

    return 0

def file_presence_display(file_presence):
        status = file_presence['status']
        if status == 'success':
            formatted_data = []
            for location in file_presence['result']:
                formatted_data.append({
                    "loc": location,
                    "locname": location.replace('_', ' ').title(),
                    "count": len(file_presence['result'][location]),
                    "files": file_presence['result'][location]
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
            return 0
        else:
            st.write("No file presence data available.")
            return 1

def existing_session():
    session_uuid, session = sessions_selectbox()
    games = get_all("games")
    session_id = session['id']
    session_game_id = session['gameid']
    st.session_state.selected_session = session_uuid
    st.session_state.selected_session_id = session_id

    log.info(f"Fetched {len(games)} games from backend.")
    log.info(f"Selected session from UI: {session_uuid}")
    log.info(f"Session ID resolved: {session_id}")
    log.info(f"Session selected in UI: {st.session_state.selected_session} with ID {st.session_state.selected_session_id}")
    log.info(f"Session Game ID: {session_game_id}")

    gamenamelist = [item for item in games if item["id"] == session_game_id]
    gamename = gamenamelist[0]['name'] if gamenamelist else 'Unknown'
    session_status = get_session_status(st.session_state.selected_session_id)
    session_notes = session["notes"]
    session_name = session["name"]
    session_info = {
        "Name": session_name,
        "Status": session_status,
        "Game": gamename,
        "GameID": session_game_id,
        "Notes": session_notes,
        "ID": session_id,
        "UUID": session_uuid
        }

    with st.sidebar:
        st.write(f":blue[**Name:**]        {session_name}")
        st.write(f":blue[**Status:**]     {session_status}")
        st.write(f":blue[**Game:**]       {gamename}")
        st.write(f":blue[**Notes:**]      {session_notes}")

    if session_status != "archived":
        file_presence = get_file_presence(session_id)
        file_presence_display(file_presence)
        st.divider()

        process_states = get_process_states(session_info)
        log.info(f"Process states: {process_states}")
        process_states_display(session_info, process_states, file_presence)
        st.divider()

        #sesstabs = {
        #    "Session Management": session_management,
        #    "Process Management": process_management,
        #    "File Management": ml_files,
        #    "Play Walkthrough": play_walkthrough
        #}
        #lazy_tabs(sesstabs, key_prefix="session_tabs")
    else:
        st.write("Session archived, click here to unarchive.")

def get_session_status(session_id):
    log.info(f"Fetching status for session ID: {session_id}")
    return get_one("sessions", session_id)["status"]

# -------------------------
#  UI - Single Page - Interface
# -------------------------
on = st.toggle("Activate debugging")

if on:
    st.session_state.debug = True
    
else:
    st.session_state.debug = False
debug = st.session_state.debug
tabs = {
    "New Session": new_session,
    "Existing Session": existing_session,
    "Jobs": jobs_interface
}

lazy_tabs(tabs)