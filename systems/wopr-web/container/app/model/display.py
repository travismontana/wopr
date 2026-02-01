import streamlit as st
import pandas as pd

from lib.models_lib import (
    get_model_status, download_model, check_data
)

from lib.basic_functions import (
    setup_logger, 
    get_config,
    debugit
)

logger = setup_logger()

def model_main_display():
    models = st.session_state['models']
    model_families = st.session_state['model_families']
    debugit(models, "Models main display")

    cols = st.columns([2,2,2,4])
    cols[0].markdown(":blue[**Name**]")
    cols[1].markdown(":blue[**Base Model**]")
    cols[2].markdown(":blue[**Status**]")
    cols[3].markdown(":blue[**Actions**]")

    st.divider()

    for model in models:
        cols = st.columns([2,2,2,4])
        try:
            model_status = get_model_status(model['shortname'])
            downloaded = model_status['downloaded']
            distfile = model_status['distfile']
            backedup = model_status['backedup']
        except:
            model_status = {}
            downloaded = False
            distfile = False
            backedup = False

        cols[0].write(model['name'])
        cols[1].write(next((f["name"] for f in model_families if f["id"] == model["familyid"]), ""))
        if downloaded:
            cols[2].badge("Downloaded", icon=":material/check:", color="green")
        else:
            cols[2].badge("Not Downloaded", icon=":material/cancel:", color="red")
        if distfile:
            cols[2].badge("Distfile Present", icon=":material/check:", color="green")
        else:
            cols[2].badge("Distfile Not Present", icon=":material/cancel:", color="red")
        if backedup:
            cols[2].badge("Backed Up", icon=":material/check:", color="green")
        else:
            cols[2].badge("Not Backed Up", icon=":material/cancel:", color="red")

        with cols[3]:
            button_cols = st.columns(3)
            if button_cols[0].button(
                "Download", 
                key=f"dl_{model['shortname']}",
                disabled = downloaded
                ):
                st.toast(f"Downloading {model['shortname']}")
                try:
                    data = download_model(model['shortname'])
                except Exception as e:
                    st.error(f"Error downloading {model['shortname']}: {e}")
                try:
                    check_data(data)
                except Exception as e:
                    st.error(f"Error checking data for {model['shortname']}: {e}")

                debugit(data, f"Downloaded model data for {model['shortname']}")
            if button_cols[1].button(
                "Backup", 
                key=f"bak_{model['shortname']}"):
                st.toast(f"Backing up {model['shortname']}")
                # Do the thing
                
            if button_cols[2].button(
                "Config", 
                key=f"cfg_{model['shortname']}"):
                st.toast(f"Backing up config for {model['shortname']}")
                # Do the thing