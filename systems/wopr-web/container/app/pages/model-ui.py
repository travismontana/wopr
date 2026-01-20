import streamlit as st
import httpx
import random
import re
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
import pandas as pd

from lib.basic_functions import (
    setup_logger, 
    get_config
)

from lib.models_lib import (
    get_models,
    create_new_model
)

from lib.model_family_lib import (
    get_model_family,
    create_new_model_family
)

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
        "model_families": [],
        "models": [],
        "debug": False,
        "debuggers": {}
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# pages
def create_model_page():
    st.title("Create Model")
    model = {}
    model_families = st.session_state.model_families
    with st.form("create_model_form"):
        model['name'] = st.text_input("Model Name")
        model['description'] = st.text_area("Model Description")
        model['family'] = st.selectbox(
            "Model Family", 
            options=model_families,
            format_func = lambda x: x["name"]
            )
        submitted = st.form_submit_button("Create Model")
        if submitted:
            if debug:
                st.write("Creating new model with data:")
                st.json(model)
            results = create_new_model(model,debug)
            st.write(results)

def list_model_page():
    logger.info("Working on model listing")
    
    models = st.session_state.models
    df = pd.DataFrame(
        models,
        columns=["name","description","note"]
    )
    st.table(df)

def create_model_family_page():
    st.title("Create Model Family")
    model_family = {}
    with st.form("create_model_family_form", enter_to_submit=False):
        model_family['name'] = st.text_input("Model Family Name")
        model_family['description'] = st.text_area("Model Family Description")
        model_family['note'] = st.text_area("Additional Information")
        submitted = st.form_submit_button("Create Model Family", key="create_model_family_submit")
        logger.info(f"Form submitted: {submitted}")
        logger.info(f"Form data: {model_family}")
    if submitted:
        st.write("Yes!")
        results = create_new_model_family(model_family, debug)
        logger.info(f"New model family created: {results}")
        st.session_state.debuggers['create_model_family_page'] = results
        if st.session_state.debug:
            st.write("new model family")
            st.write(f"({results})<-shouldbedata")
            st.write(f"({st.session_state.debuggers['create_model_family_page']})<-shouldbedata")
            #t.json(results, expanded=False)

def list_model_family_page():
    logger.info("Working on model family listing")
    
    families = st.session_state.model_families
    df = pd.DataFrame(
        families,
        columns=["name","description","note"]
    )
    st.table(df)

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
            st.cache_data.clear()

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
    st.write("Models: ")
    st.json(st.session_state.models)
    st.write("Model Families: ")
    st.json(st.session_state.model_families)

model_count = len(st.session_state.models)
model_family_count = len(st.session_state.model_families)

if model_count == 0:
    st.warning("No models found.")
if model_family_count == 0:
    st.warning("No model families found.")

countCol,statusCol = st.columns(2)

with countCol:
    st.write(f":blue[Model Families:] {model_family_count}")
    st.write(f":blue[Models:]         {model_count}")

with statusCol:
    st.write(":blue[Model Families:]")
    for item in st.session_state.model_families:
        st.write(f"- {item['name']}")
    st.write(":blue[Models:]")
    for item in st.session_state.models:
        st.write(f"- {item['name']}")

# -------
st.divider()

modFamTab, modTab, traTab = st.tabs(["Model Families", "Models", "Training"])
with modFamTab:
    with st.expander("Create New Model Family"):
        create_model_family_page()
    list_model_family_page()

with modTab:
    with st.expander("Create New Model"):
        create_model_page()
    list_model_page()

with traTab:
    st.write("Coming Soon")