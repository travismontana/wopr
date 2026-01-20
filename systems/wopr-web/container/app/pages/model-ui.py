import streamlit as st
import httpx
import random
import re
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from lib.models_lib         import get_models
from lib.basic_functions    import setup_logger
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
        "debug": False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ============================================================================
# MAIN UI
# ============================================================================

st.set_page_config(layout="wide", page_title="WOPR Model Control")
st.title("WOPR Model Control")
st.write("Use as the template for control of models.")

init_session_state()
debug = st.session_state.debug

with st.sidebar:
    logger.info("Sidebar started")
    with st.expander("Settings"):
        # Debug toggle
        debug_toggle = st.toggle("Activate debugging", value=st.session_state.debug)
        st.session_state.debug = debug_toggle
        debug = st.session_state.debug
        # Cache control
        if st.button("Clear Cache"):
            clear_cache()

models = get_models()