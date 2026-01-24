import streamlit as st
import pandas as pd
from lib.helpers import debug_log, debug_json

from lib.api import api_get_models, api_get_model_families

def render_models_editor():
    """
    Render the ML Models Editor display.
    """
    if "models" not in st.session_state:
        models_response = api_get_models()
        if "error" in models_response:
            st.error(f"Error fetching models: {models_response['message']}")
            return {"status": "error", "message": models_response['message']}
        st.session_state["models"] = models_response
        debug_json(models_response)

    if "model_families" not in st.session_state:
        families_response = api_get_model_families()
        if "error" in families_response:
            st.error(f"Error fetching model families: {families_response['message']}")
            return {"status": "error", "message": families_response["message"]}
        st.session_state["model_families"] = families_response
        debug_json(families_response)
    models_data = st.session_state.get("models", [])

    DISPLAY_COLUMNS = [
        "id",
        "name",
        "shortname",
        "version",
        "familyid",
        "description",
        "note",
        "date_updated",
    ]

    models_df = pd.DataFrame(models_data)
    models_df = models_df[DISPLAY_COLUMNS]
    st.session_state["models_df"] = models_df
    st.dataframe(models_df)

    # Placeholder for actual model editing logic
    return {"status": "Models editor rendered"}
