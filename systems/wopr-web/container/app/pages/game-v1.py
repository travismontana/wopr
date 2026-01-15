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

st.title("WOPR Game Interface")
st.write("Welcome to the WOPR Game Interface.")

API_BASE = "https://api.wopr.tailandtraillabs.org"

midcounter = 0

# Initialize session state
if 'session_uuid' not in st.session_state:
	st.session_state.session_uuid = None
if 'current_round' not in st.session_state:
	st.session_state.current_round = 0
if 'current_round_play' not in st.session_state:
	st.session_state.current_round_play = 0
if 'round_started' not in st.session_state:
	st.session_state.round_started = False
if 'selected_game' not in st.session_state:
	st.session_state.selected_game = None

def fetch_config():
	response = httpx.get(f"{API_BASE}/api/v2/config/all")
	response.raise_for_status()
	return response.json()

config = fetch_config()

@st.cache_data(ttl=240)
def fetch_games():
	response = httpx.get(f"{API_BASE}/api/v2/games")
	response.raise_for_status()
	return response.json()

def newSession(game_id):
	response = httpx.get(f"{API_BASE}/api/v2/session/new/{game_id}")
	response.raise_for_status()
	return response.json().get('sessionuuid')

def takeCapture(sessionuuid, camid, startorend):
	filename = f"game-{sessionuuid}-round{st.session_state.current_round}-{startorend}.jpg"
	payload = {
		"camid": camid,
		"filename": filename,
		"sessionuuid": sessionuuid
	}
	response = httpx.post(f"{API_BASE}/api/v2/session/capture", json=payload, timeout=120.0)
	response.raise_for_status()
	return response.json()

# Game Selection
if st.session_state.session_uuid is None:
	games = fetch_games()
	game_names = [game['name'] for game in games]
	selected_game_name = st.selectbox("Select a game:", options=game_names)
	selected_game = next(g for g in games if g['name'] == selected_game_name)
	st.session_state.selected_game = selected_game
	
	if st.button("Start New Game"):
		st.session_state.session_uuid = newSession(selected_game['id'])
		st.session_state.current_round = 1
		st.session_state.round_started = False
		
		st.success(f"New game session started: {st.session_state.session_uuid}")
		st.rerun()

# Game in Progress
else:
	game = st.session_state.selected_game
	st.subheader(f"Playing: {game['name']}")
	st.write(f"Session UUID: {st.session_state.session_uuid}")
	st.write(f"Round: {st.session_state.current_round} / {game.get('max_rounds', 'Unknown')}")
	
	# Round hasn't started yet
	if not st.session_state.round_started:
		if st.button(f"Start Round {st.session_state.current_round}"):
			# Capture initial state
			result = takeCapture(
				st.session_state.session_uuid,
				config.get('default_camera_id', 1),
				"start"
			)
			st.success(f"Round {st.session_state.current_round} started - Initial state captured")
			st.session_state.round_started = True
			st.rerun()
	
	# Round in progress
	else:
		st.info(f"Round {st.session_state.current_round} in progress...")
		
		if st.button(f"Mid Round {st.session_state.current_round}"):
			# Capture mid state
			result = takeCapture(
				st.session_state.session_uuid,
				config.get('default_camera_id', 1),
				f"mid{st.session_state.current_round_play}"
			)
			st.session_state.current_round_play += 1
			st.success(f"Round {st.session_state.current_round} - mid game {st.session_state.current_round_play} - State captured")

		if st.button(f"End Round {st.session_state.current_round}"):
			# Capture end state
			result = takeCapture(
				st.session_state.session_uuid,
				config.get('default_camera_id', 1),
				"end"
			)
			st.success(f"Round {st.session_state.current_round} ended - Final state captured")
			
			# Check if game is complete
			max_rounds = game.get('max_rounds', 10)
			if st.session_state.current_round >= max_rounds:
				st.balloons()
				st.success("🎮 Game Complete!")
				if st.button("Start New Game"):
					st.session_state.session_uuid = None
					st.session_state.current_round = 0
					st.session_state.round_started = False
					st.rerun()
			else:

				st.session_state.current_round += 1
				st.session_state.current_round_play += 1
				st.session_state.round_started = False
				st.rerun()
	
	# Emergency reset
	st.divider()
	if st.button("⚠️ Abort Game", type="secondary"):
		st.session_state.session_uuid = None
		st.session_state.current_round = 0
		st.session_state.round_started = False
		st.rerun()