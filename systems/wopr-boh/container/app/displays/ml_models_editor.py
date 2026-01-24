import streamlit as st
from lib.helpers import debug_log, debug_json

from lib.api import api_get_models

def render_models_editor():
    """
    Render the ML Models Editor display.
    """
    if models := st.session_state.get("models") is None:
        models_response = api_get_models()
        if "error" in models_response:
            st.error(f"Error fetching models: {models_response['message']}")
            return {"status": "error", "message": models_response['message']}
        st.session_state["models"] = models_response.get("models", [])
        debug_json(models_response)
        
    models_data = st.session_state.get("models", [])
    
    st.dataframe(models_data)
    
    # Placeholder for actual model editing logic
    return {"status": "Models editor rendered"}
