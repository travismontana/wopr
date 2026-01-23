import logging

import streamlit as st

logger = logging.getLogger(__name__)

DEBUG=st.session_state["debug"]

def debugit(message,data):
    """Display debug information if debug set"""
    if DEBUG:
        st.write(f"Message: {message}")
        st.write(data)


def logit(info_message, debug_message):
    logger.info(f"{info_message}")
    logger.debug(f"{debug_message}")
