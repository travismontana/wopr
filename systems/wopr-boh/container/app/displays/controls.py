import streamlit as st

from lib.api import api_get_models
from lib.helpers import init_session_defaults

def system_controls():
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        if st.button("Clear UI Cache"):
            st.session_state.clear()
            init_session_defaults()
            st.toast("UI cache cleared", icon="🧹")
    with col2:
        if st.button("Reload Models from API"):
            models = api_get_models()
            st.session_state["models"] = models
            st.toast("Models reloaded from API", icon="🔄")
    with col3:
        if st.button("Refresh page"):
            st.rerun()
