import streamlit as st
from lib.basic_functions import (
    setup_logger, get_all, 
    create_new, update_item,
    debugit
)

logger = setup_logger()

debug = ""

# General stuff
@st.cache_data()
def get_models():
    return get_all("models")

def create_new_model(model):
    debugit(model, "Creating a new model")
    results = create_new("models", model)
    logger.info("Creating a new model - Completed")
    logger.info(f"Data: {model}")
    logger.info(f"Results: {results}")
    if results:
        return results
    else:
        return 1

def update_model_info(edited_df):
    logger.info("Updating model information")
    debugit(edited_df, "Updating model information")
    results = []
    for item in edited_df:
        id = item["id"]
        results.append(update_item("models", id, item))
    debugit(results, "Updated model information")
    return results

def get_model_status(model):
    debugit(model, "Getting model status")

    status = {
        'distfile_exists': False,
        'checksum'       : None,
        'downloaded'     : False,
        'filename'       : None
    }

    model['']