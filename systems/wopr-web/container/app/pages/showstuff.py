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

st.title("WOPR ML Config System")
st.write("Welcome to the WOPR ML Config System.")

# 
# Load WOPR Config from WOPR-API, then display it.
#
API_BASE = "https://api.wopr.tailandtraillabs.org"

@st.cache_data(ttl=60)
def fetch_games():
    r = httpx.get(f"{API_BASE}/api/v2/games")
    r.raise_for_status()
    return r.json()

def fetch_pieces(game_id):
    r = httpx.get(f"{API_BASE}/api/v2/pieces/gameid/{game_id}")
    r.raise_for_status()
    return r.json()

def fetch_config():
    r = httpx.get(f"{API_BASE}/api/v2/config/all")
    r.raise_for_status()
    return r.json()

def post_json(url: str, payload: dict) -> requests.Response:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    return r

def show_config():
    st.header("WOPR Configuration")
    config = fetch_config()
    st.json(config)

def show_games():
    st.header("Games")
    games = fetch_games()
    for game in games['data']:
        st.subheader(f"Game ID: {game['id']}")
        st.json(game)

def show_pieces(game_id: str):
    st.header(f"Pieces for Game ID: {game_id}")
    pieces = fetch_pieces(game_id)
    for piece in pieces['data']:
        st.subheader(f"Piece ID: {piece['id']}")
        st.json(piece)

#
# Stuff to list:
# Games, Pieces, Config
# Games will list the games
# Pieces, you'll be asked for the game_id to list pieces for
# Config will just dump the current config
#

st.header("WOPR Data Viewer")
option = st.selectbox(
    "Select data to view:",
    ("Configuration", "Games", "Pieces by Game ID")
)

if option == "Configuration":
    show_config()
elif option == "Games":
    show_games()
elif option == "Pieces by Game ID":
    game_id = st.text_input("Enter Game ID:")
    if game_id:
        show_pieces(game_id)
