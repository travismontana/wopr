import streamlit as st

DEBUG=st.session_state["debug"]

def debugit(message,data):
    """Display debug information if debug set"""
    if DEBUG:
        st.write(f"Message: {message}")
        st.write(data)