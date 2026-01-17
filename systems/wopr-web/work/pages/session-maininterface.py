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

def session_management():
    st.subheader("Session Management")
    st.write("Functionality for session management will go here.")
    current_session_id = st.session_state.get("selected_session_id", None)
    session_info = get_one("sessions", {"id": current_session_id}) if current_session_id else None
    log.info(f"Current Session Info: {session_info}")
    if current_session_id:
        log.info(f"Managing session ID: {current_session_id}")
        plays = get_session_plays(current_session_id)
        log.info(f"Number of Plays in this Session: {len(plays)}")
        session_info['plays'] = plays
        


def ml_prep():
    st.subheader("ML Preparation")
    st.write("Functionality for ML preparation will go here.")
    # files in /ml/incoming/ to be processed for ML training
    # files in /labelstudio/source 
    

def play_walkthrough(plays, players):
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
    players = get_all("players")
    
    session_uuid, session = sessions_selectbox()
    session_id = session['id']
    st.session_state.selected_session = session_uuid
    st.session_state.selected_session_id = session_id
    log.info(f"Session selected in UI: {st.session_state.selected_session} with ID {st.session_state.selected_session_id}")

    plays = get_session_plays(st.session_state.selected_session_id)
    gamename = games[0]['name'] if games else "Unknown"
    st.write(f"Session Game: {gamename}")

    sesstabs = {
        "Session Management": session_management,
        "ML Prep": ml_prep,
        "Play Walkthrough": lambda: play_walkthrough(plays, players)
    }

    lazy_tabs(sesstabs, key_prefix="session_tabs")

# -------------------------
#  UI - Single Page - Interface
# -------------------------
 
tabs = {
    "New Session": new_session,
    "Existing Session": existing_session
}

lazy_tabs(tabs)