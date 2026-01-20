import streamlit as st
import httpx
import random
import re
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from lib.models_lib import (
    get_models,
    get_model_family,
    create_new_model
)
from lib.basic_functions import setup_logger
import pandas as pd

# Setup some defaults

logger = setup_logger()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """
    Initialize all session state variables.
    defaults is for things that should be reported on and are important.
    """
    
    defaults = {
        "selected_game": None,
        "attempts": 0,
        "model_families": None,
        "debug": False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# pages

def create_model_page():
    st.title("Create Model")
    with st.form("create_model_form"):
        st.text_input("Model Name")
        st.text_area("Model Description")
        selected_family = st.selectbox("Model Family", st.session_state.model_families or [])
        submitted = st.form_submit_button("Create Model")
        if submitted:
            create_new_model()

# ============================================================================
# MAIN UI
# ============================================================================

st.set_page_config(layout="wide", page_title="WOPR Model Control")
st.title("WOPR Model Control")
st.write("Use as the template for control of models.")

init_session_state()
debug = st.session_state.debug

with st.sidebar:
    with st.expander("Settings"):
        # Debug toggle
        debug_toggle = st.toggle("Activate debugging", value=st.session_state.debug)
        st.session_state.debug = debug_toggle
        debug = st.session_state.debug
        # Cache control
        if st.button("Clear Cache"):
            clear_cache()

try:
    st.session_state.models = get_models()
    st.session_state.model_families = get_model_family()
    st.session_state.attempts = 0
except Exception as e:
    if e.response.status_code == 503:
        if st.session_state.attempts < 3:
            st.session_state.attempts += 1
            with st.spinner("Waiting for API to load...will retry 3 times every 60 seconds", show_time=True):
                time.sleep(60)
            st.rerun()
        else:
            st.error("Api Not loading")
            st.session_state.attempts = 0  # reset for next time
    else:
        raise

if debug:
    st.write("Debugging is active.")
    st.json(models)

model_count = len(models)

if model_count == 0:
    st.warning("No models found.")

with st.sidebar:
    newmodel = st.button("Create New Model")

# -------
st.divider()
    
if newmodel:
    results = create_model_page()