import streamlit as st
import httpx
import random
import re
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from datetime import timezone
import pandas as pd
import numpy as np

from lib.basic_functions import (
    setup_logger, 
    get_config,
    debugit
)

from lib.models_lib import (
    get_models,
    create_new_model,
    update_model_info
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
        "debuggers": {},
        "model_df": None
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
            debugit(model, "Creating new model with data")
            results = create_new_model(model)
            st.write(results)

def list_model_page():
    logger.info("Working on model listing")
    
    models = st.session_state.models
    df = pd.DataFrame(
        models
    )
    st.session_state.model_df = df
    edited_df = st.data_editor(
        df, 
        num_rows="dynamic",
        column_config = {
            "id" : st.column_config.NumberColumn(disabled=True),
            "name" : st.column_config.TextColumn(
                "Name",
                validate  = r"^[a-zA-Z0-9_ -]+$",
                max_chars = "63",
                required  = True,
                help      = "Name of the model to be created."
            ),
            "version" : st.column_config.NumberColumn(
                "Version",
                min_value=1,
                max_value=100,
                step=1,
                default=1,
                format="%d"
            ),
            "description" : st.column_config.TextColumn("Description"),
            "familyid" : st.column_config.SelectboxColumn(
                "Model Family",
                options = [f['id'] for f in st.session_state.model_families],
                format_func = lambda x: next((f["name"] for f in st.session_state.model_families if f["id"] == x), ""),
            ),
            "shortname" : st.column_config.TextColumn("Short Name"),
            "note" : st.column_config.TextColumn("Note")
        },
        column_order = (
            "id",
            "name",
            "version",
            "description",
            "familyid",
            "shortname",
            "note",
            "date_updated",
            "model_state",
            "model_status",
            "date_created"
        )
    )

    debugit(edited_df, "Debug message")
    if not edited_df.equals(df):
        new_rows = edited_df[edited_df['id'].isna()]
        updated_rows = edited_df[edited_df['id'].notna()]
        debugit(new_rows, "New rows detected")
        debugit(updated_rows, "Updated rows detected")
        debugit(edited_df, "Model data has been edited")

        logger.info("Model data has been edited")

        results = {'created': [], 'updated': []}

        if not new_rows.empty:
            for _, row in new_rows.iterrows():
                model_data = {k: v for k, v in row.to_dict().items() 
                    if k not in ('id', 'date_created', 'date_updated', 'model_state') 
                    and v is not None}
                create_result = create_new_model(model_data.to_dict(orient="records"), debug)
                results['created'].append(create_result)
    
        # Handle updates to existing models
        if not updated_rows.empty:
            filtered_updates = [
                {k: v for k, v in row.items() 
                if k not in ('id', 'date_created', 'date_updated', 'model_state') 
                and v is not None}
                for row in updated_rows.to_dict(orient="records")
            ]
            sanitized = updated_rows.replace({np.nan: None}).to_dict(orient="records")
            update_result = update_model_info(sanitized)
            debugit(update_result, "Updated model info")
            results['updated'].append(update_result)
        
        debugit(results, "Model operation results")

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
        families
    )

    edited_df = st.data_editor(df)

    if not edited_df.equals(df):
        debugit(edited_df, "list_model_family_page Model family data has been edited")
        
        results = update_model_family_info(edited_df)

        debugit(results, "Update model family results")
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
    #st.session_state.config = get_config()
    #config = st.session_state.config
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

debugit(st.session_state, "Step 1 - Session state")

model_count = len(st.session_state.models)
model_family_count = len(st.session_state.model_families)

if model_count == 0:
    st.warning("No models found.")
if model_family_count == 0:
    st.warning("No model families found.")

modelsCol,modelFamilyCol = st.columns(2)

with modelsCol:
    #get_model_status()
    st.write(f":blue[Status:] Green")

with modelFamilyCol:
    st.write(":blue[Health:]  Green")
# -------
st.divider()

modTab, modFamTab, traTab = st.tabs(["Models", "Model Families", "Training"])


with modTab:
    with st.expander("Create New Model"):
        create_model_page()
    list_model_page()
    
    #with st.expander("Model Download"):
        #model_download()
with modFamTab:
    with st.expander("Create New Model Family"):
        create_model_family_page()
    list_model_family_page()
with traTab:
    st.write("Coming Soon")