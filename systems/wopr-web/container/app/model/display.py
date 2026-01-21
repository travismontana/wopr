import streamlit as st


from lib.basic_functions import (
    setup_logger, 
    get_config,
    debugit
)

logger = setup_logger()

def model_main_display():
    models = st.session_state['models']
    debugit(models, "Models main display")

    