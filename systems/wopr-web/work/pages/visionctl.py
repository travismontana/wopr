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

st.title("WOPR Vision Interface")
st.write("Welcome to the WOPR Vision Interface.")

API_BASE = "https://api.wopr.tailandtraillabs.org"

# Initialize session state
if 'session_uuid' not in st.session_state:
	st.session_state.session_uuid = None
if 'current_round' not in st.session_state:
	st.session_state.current_round = 0
if 'round_started' not in st.session_state:
	st.session_state.round_started = False
if 'selected_game' not in st.session_state:
	st.session_state.selected_game = None

def fetch_config():
	response = httpx.get(f"{API_BASE}/api/v2/config/all")
	response.raise_for_status()
	return response.json()

config = fetch_config()

@st.cache_data(ttl=60)
def fetch_games():
	response = httpx.get(f"{API_BASE}/api/v2/games")
	response.raise_for_status()
	return response.json()

@st.cache_data(ttl=60)
def fetch_projects():
	response = httpx.get(f"{API_BASE}/api/v2/vision/projects")
	response.raise_for_status()
	return response.json()

#project_names = fetch_projects()
#selected_project = st.selectbox("Select a project:", options=project_names)
if st.button("Get projects"):
	st.json(fetch_projects())
