"""
WOPR Back of House - Main Page

Streamlit main entry for Back of House UI.
Currently focuses on WOPR ML Models admin.
"""

from __future__ import annotations

import streamlit as st

from lib.helpers import init_session_defaults, clear_ui_cache

from displays.ml_models_editor import render_models_editor
from displays.ml_models_status import render_models_status
from displays.ml_model_controls import render_models_controls
from displays.controls import system_controls


def render_sidebar() -> None:
    """
    Render sidebar controls (settings, debug, cache).
    """
    with st.sidebar:
        with st.expander("Settings"):
            st.session_state["debug"] = st.toggle(
                "Activate debugging",
                value=st.session_state.get("debug", False),
            )

            if st.button("Clear Cache"):
                clear_ui_cache()
                st.toast("Cache cleared", icon="🧹")


def main() -> None:
    """
    Main Streamlit page renderer.
    """
    st.set_page_config(
        page_title="WOPR Back of House",
        page_icon=":joystick:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    init_session_defaults()

    st.title("WOPR Back of House")

    placeholder = st.empty()
    with placeholder.container():
        st.markdown("System Loading...")
    placeholder.empty()

    render_sidebar()

    # System Controls
    st.subheader("System Controls")
    _results = system_controls()

    # Models editor section
    st.subheader("Models")
    _results = render_models_editor()

    st.subheader("Model Status")
    _results = render_models_status()

    st.subheader("Model Controls")
    _results = render_models_controls()
    # _results = render_model_status()
    # You can optionally show a summary when debug is on
    if st.session_state.get("debug", False):
        st.write("Operation results:", _results)


if __name__ == "__main__":
    main()
