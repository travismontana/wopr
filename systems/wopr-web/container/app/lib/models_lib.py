import streamlit as st
from lib.basic_functions import setup_logger, get_all 

logger = setup_logger()

debug = ""

# General stuff
@st.cache_data()
def get_models():
    return get_all("models")

def create_new_model():
    logger.info("Creating a new model")
    st.write("Creating a new model")