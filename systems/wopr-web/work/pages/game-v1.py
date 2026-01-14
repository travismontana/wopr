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

st.title("WOPR Game Interface")
st.write("Welcome to the WOPR Game Interface.")

# 
# Load WOPR Config from WOPR-API, then display it.
#
API_BASE = "https://api.wopr.tailandtraillabs.org"

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

def selectGame():
    games = fetch_games()
    game_names = [game['name'] for game in games]
    selected_game_name = st.selectbox("Select a game:", options=game_names)
    selected_game = next(g for g in games if g['name'] == selected_game_name)
    return selected_game

selectedGame = selectGame()
