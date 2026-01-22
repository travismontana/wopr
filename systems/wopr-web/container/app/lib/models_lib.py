"""WElcome"""

import streamlit as st

from lib.basic_functions import (
    setup_logger,
    get_all,
    create_new,
    update_item,
    debugit,
    do_api_things,
)

from models import models

logger = setup_logger()

DEBUG = ""

BASE_MODELS_PATH = "/remote/wopr/models"

# General stuff
@st.cache_data()
def get_models():
    """Returns all models"""
    return get_all("models")

def create_new_model(model):
    """Creates a new model"""
    debugit(model, "Creating a new model")
    results = create_new("models", model)
    logger.info("Creating a new model - Completed")
    logger.info(f"Data: {model}")
    logger.info(f"Results: {results}")
    if results:
        return results
    return 1

def update_model_info(edited_df):
    """Updates model information"""
    logger.info("Updating model information")
    debugit(edited_df, "Updating model information")
    results = []
    for item in edited_df:
        id_var = item["id"]
        results.append(update_item("models", id_var, item))
    debugit(results, "Updated model information")
    return results

def talk_to_model_ctl(action, data):
    """router for talking to model ctl directly"""
    url = st.session_state['config']['api']['models_url']
    match action:
        case "status":
            # thing = do_api_things("post", url, "models", "model_status", data)
            return create_new("model/status", data)
        case "download":
            thing = do_api_things("post", url, "models", "download", data)
            return thing
        case _:
            return False

def download_model(model):
    """tells model control to download a model"""
    url = st.session_state['config']['api']['models_url']
    data = talk_to_model_ctl("download", {"model": model})
    debugit(data, "Download model response")
    return data

@st.cache_data()
def get_model_status(model):
    """Gets the status of a model"""
    debugit(model, "Getting model status")
    data = {
        "model": model,
        "backedup": False,
        "checksum": None,
        "downloaded": False,
        "filename": None
    }
    debugit(data, "Model status data")
    results = talk_to_model_ctl("status", data)
    debugit(results, "Model status after talk_to_model_ctl")
    return results

def check_data(data):
    """Checks the status of the last operation in the data"""
    debugit(data, "Checking data")
    if data['last_operation']['status'] != "success":
        st.error(f"Operation ({data['last_operation']['task']}) failed\n"
        f"Note: ({data['last_operation']['note']})\n"
        f"Extra Data: ({data['last_operation']['extradata']})")
