import streamlit as st
from lib.basic_functions import setup_logger, get_all, create_new

logger = setup_logger()

debug = ""

@st.cache_data()
def get_model_family():
    all = get_all("model_family")
    logger.info(f"Retrieved model families: {all}")
    return all

def create_new_model_family(data, debugin):
    logger.info("Creating a new model family")
    st.write("Creating a new model family")
    debug = debugin
    if debug:
        st.write("In create_new_model_family")
        st.write(data)
    results = create_new("model_family", data)
    logger.info(f"New model family created: {results}")
    return results
