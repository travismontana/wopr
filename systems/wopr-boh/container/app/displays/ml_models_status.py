import streamlit as st
import pandas as pd
import numpy as np

from lib.helpers import debug_log, debug_json

from lib.api import (
    api_get_models,
    api_get_model_families,
)


def render_models_status():
    """
    Render the ML Models Editor display.
    """

    if "models" not in st.session_state:
        models_response = api_get_models()
        debug_log("Fetched models for status:")
        debug_json(models_response)
        if "error" in models_response:
            st.error(f"Error fetching models: {models_response['message']}")
        st.session_state["models"] = models_response
        debug_json(models_response)

    if "model_families" not in st.session_state:
        families_response = api_get_model_families()
        if "error" in families_response:
            st.error(f"Error fetching model families: {families_response['message']}")
        st.session_state["model_families"] = families_response
        debug_json(families_response)

    models_data = st.session_state.get("models", [])
    debug_log("Models Data for Status:")
    debug_json(models_data)
    status_table = {}

    for model in models_data:
        if "model_status" not in model:
            model["model_status"] = "unknown"
            status_table[model["id"]] = {
                "name": model["name"],
                "model_status": "unknown"
            }
        else:
            family = next(
                (
                    f
                    for f in st.session_state["model_families"]
                    if f["id"] == model["familyid"]
                ),
                None,
            )
            model["family_name"] = family["name"] if family else "Unknown"
            status_table[model["id"]] = {
                "name": model["name"],
                "model_status": model["model_status"],
            }

    #df = pd.DataFrame.from_dict(status_table, orient="index")
    #st.dataframe(df, use_container_width=True)

    status_table = {}
    for model in models_data:
        if "model_status" in model and model["model_status"] is not None:
            debug_log(f"Rendering status details for model {model['name']}:")
            debug_json(model.get("model_status", {}))
            status = model["model_status"]
            has_distfile = status.get("has_distfile", False)
            has_backup = status["backup"] is not None
            has_filename = status.get("filename") is not None
            is_active = status.get("active", False)
            status_table[model["name"]] = {
                "Active": is_active,
                "Has Distfile": has_distfile,
                "Has Backup": has_backup,
                "Has Filename": has_filename,
            }
        else:
            status_table[model["name"]] = {
                "Active": False,
                "Has Distfile": False,
                "Has Backup": False,
                "Has Filename": False,
            }
    df_status = pd.DataFrame.from_dict(status_table, orient="index")
    st.dataframe(df_status)