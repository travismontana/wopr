import streamlit as st
import httpx
import os 
import requests

st.title("WOPR ML Cam Check System")
st.write("Welcome to the WOPR ML Cam Check System.")

# 
# Load WOPR Config from WOPR-API, then display it.
#
API_BASE = "https://api.wopr.tailandtraillabs.org"

def fetch_config():
    response = httpx.get(f"{API_BASE}/api/v2/config/all")
    response.raise_for_status()
    return response.json()


config = fetch_config()

#
# Get a list of the cameras
# Select one
# button to grab image from API_BASE/api/v2/stream/grab/{camera_id}
# run that, and show image.
#

st.header("Cameras")
cameras = config['camera']['camDict']

camera_options = {cam['name']: cam['id'] for cam in cameras.values()}
selected_camera_name = st.selectbox("Select a camera", list(camera_options.keys()))
selected_camera_id = camera_options[selected_camera_name]

if st.button("Display Image"):
    response = httpx.get(f"{API_BASE}/api/v2/stream/grab/{selected_camera_id}")
    response.raise_for_status()
    st.image(response.content, caption=f"Image from {selected_camera_name}")