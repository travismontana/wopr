import streamlit as st
from lib.basic_functions import (
    setup_logger, get_all, create_new
)

logger = setup_logger()

debug = ""

# General stuff
@st.cache_data()
def get_models():
    return get_all("models")

def create_new_model(model, debug):
    logger.info("Creating a new model")
    st.write("Creating a new model")
    results = create_new("models", model)
    logger.info("Creating a new model - Completed")
    logger.info(f"Data: {model}")
    logger.info(f"Results: {results}")
    if results:
        return results
    else:
        return 1

def update_model_info(edited_df, debug):
    logger.info("Updating model information")
    logger.debug(f"Edited DataFrame: {edited_df}")
    if debug:
        st.write("Model information has been edited.")
        st.json(edited_df, expanded=False)
    update_item("models",)