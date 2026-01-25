import streamlit as st
import pandas as pd
import numpy as np

from lib.helpers import debug_log, debug_json

from lib.api import (
    api_get_models,
    api_get_model_families,
    api_create_model,
    api_update_model,
)


def render_models_controls():
    """
    Render the ML Models Editor display.
    """
    if "models" not in st.session_state:
        models_response = api_get_models()
        if "error" in models_response:
            st.error(f"Error fetching models: {models_response['message']}")
            return {"status": "error", "message": models_response["message"]}
        st.session_state["models"] = models_response
        debug_json(models_response)

    for model in st.session_state["models"]:
        c1,c2,c3,c4 = st.columns(4)
        with c1:
            st.write(f"Model: {model['name']} (ID: {model['id']})")
        with c2:
            if st.button("Prep files", key=f"prep_{model['id']}"):
                debug_log(f"Preparing files for model {model['id']}")
                results = api_prep_model_files(model['id'])
                debug_json(results)
        with c3:
            if st.button("Backup model", key=f"backup_{model['id']}"):
                debug_log(f"Backing up model {model['id']}")
                results = api_backup_model(model['id'])
                debug_json(results)
        with c4:
            if st.button("snow", key=f"snow_{model['id']}"):
                st.snow()
        st.divider()
