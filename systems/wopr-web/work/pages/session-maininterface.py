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
from helpers import *



if "selected_game" not in st.session_state:
	st.session_state.selected_game = None
if "selected_session" not in st.session_state:
	st.session_state.selected_session = None

# -------------------------
# Streamlit UI
# -------------------------
st.title("WOPR Session Interface")
st.write("Welcome to the WOPR Session Interface.")

def new_session():
    st.subheader("Start a New Session")
    st.write("Functionality to start a new session will go here.")

def existing_session():
    st.subheader("Work an Existing Session")
    st.write("Functionality to join an existing session will go here.")
    st.session_state.selected_session = sessions_selectbox()


# -------------------------
#  UI - Single Page - Interface
# -------------------------

st.session_state.selected_game = games_selectbox()

newsession, existingsession = st.tabs(["New Session", "Existing Session"])

with newsession:
    new_session()

with existingsession:
    existing_session()