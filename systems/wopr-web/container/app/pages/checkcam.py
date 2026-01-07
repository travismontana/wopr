# Copyright 2026 Bob Bomar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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