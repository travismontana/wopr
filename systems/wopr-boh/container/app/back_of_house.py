"""
WOPR Back of House - Main Page

Streamlit main entry for Back of House UI.
Currently focuses on WOPR ML Models admin.
"""

from __future__ import annotations

import streamlit as st

from lib.helpers import init_session_defaults, clear_ui_cache, render_sidebar


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

    # _results = render_model_status()
    # You can optionally show a summary when debug is on
    if st.session_state.get("debug", False):
        st.write("Operation results:", _results)


if __name__ == "__main__":
    main()
