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
import re
from urllib.parse import unquote
from typing import Dict, List, Set

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

@st.cache_data(ttl=60)
def fetch_projects_detail(id):
	response = httpx.get(f"{API_BASE}/api/v2/vision/projects/{id}")
	response.raise_for_status()
	return response.json()

@st.cache_data(ttl=60)
def fetch_tasks(project_id):
	response = httpx.get(f"{API_BASE}/api/v2/vision/projects/{project_id}/tasks")
	response.raise_for_status()
	return response.json()

@st.cache_data(ttl=60)
def fetch_files(game_id):
	response = httpx.get(f"{API_BASE}/api/v2/images/gameid/{game_id}")
	response.raise_for_status()
	return response.json()


def extract_ls_filename(image_url: str) -> str:
	"""Extract filename from Label Studio image URL"""
	# Match ?d=path or &d=path in URL
	match = re.search(r'[?&]d=([^&]+)', image_url)
	if not match:
		return ''
	path = unquote(match.group(1))
	return path.split('/')[-1]


def compare_image_lists(ls_tasks: List[dict], wopr_images: List[dict]) -> Dict[str, List[str]]:
	"""Compare Label Studio tasks vs WOPR images"""
	# Extract filenames from Label Studio tasks
	ls_files: Set[str] = set()
	for task in ls_tasks:
		if task.get('data', {}).get('image'):
			filename = extract_ls_filename(task['data']['image'])
			if filename:
				ls_files.add(filename)
	
	# Extract filenames from WOPR images
	wopr_files: Set[str] = set()
	for image in wopr_images:
		if image.get('filenames', {}).get('fullImageFilename'):
			wopr_files.add(image['filenames']['fullImageFilename'])
	
	# Find differences
	in_wopr_not_ls = sorted(wopr_files - ls_files)
	in_ls_not_wopr = sorted(ls_files - wopr_files)
	synchronized = sorted(ls_files & wopr_files)
	
	return {
		'inWoprNotLs': in_wopr_not_ls,
		'inLsNotWopr': in_ls_not_wopr,
		'synchronized': synchronized
	}


project_names = fetch_projects()

selected_project = st.selectbox("Select a project:", 
  options=project_names["results"],
	format_func=lambda x: x['title'])

if st.button("Get Details"):
	selectedProjectDeets = fetch_projects_detail(selected_project['id'])
	st.json(selectedProjectDeets, expanded=False)

if st.button("Get Tasks"):
	tasks = fetch_tasks(selected_project['id'])
	files = fetch_files("4")
	
	result = compare_image_lists(tasks, files)
	
	st.write('**In WOPR but NOT in Label Studio:**', len(result['inWoprNotLs']))
	st.write(result['inWoprNotLs'])
	
	st.write('**In Label Studio but NOT in WOPR:**', len(result['inLsNotWopr']))
	st.write(result['inLsNotWopr'])
	
	st.write('**Synchronized:**', len(result['synchronized']))
	st.write(result['synchronized'])