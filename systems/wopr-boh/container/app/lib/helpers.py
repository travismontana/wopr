import os
import streamlit as st


def init_session_defaults() -> None:
    """
    Initialize default session state variables.
    """
    if "debug" not in st.session_state:
        st.session_state["debug"] = False

    if "api_host" not in st.session_state:
        api_host = os.getenv("API_URL", "")
        if not api_host:
            st.error("API_URL environment variable is not set.")
            raise SystemExit(1)
        st.session_state["api_host"] = api_host
    else:
        api_host = st.session_state["api_host"]


def clear_ui_cache() -> None:
    """
    Clear Streamlit cache and session-cached API payloads.

    Useful when API-side data changed and you want a hard refresh.
    """
    st.cache_data.clear()
    for key in ("models", "model_families", "modelsdf"):
        if key in st.session_state:
            del st.session_state[key]


def debug_log(message: str) -> None:
    """
    Log a debug message if debugging is enabled in session state.
    """
    if st.session_state.get("debug", False):
        st.write(f"DEBUG: {message}")


def debug_json(message: dict) -> None:
    """
    Log a debug message if debugging is enabled in session state.
    """
    if st.session_state.get("debug", False):
        st.json(message, expanded=False)
