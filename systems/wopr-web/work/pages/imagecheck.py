import streamlit as st
import httpx
import os 
import requests

st.title("WOPR ML Image Check System")
st.write("Welcome to the WOPR ML Image Check System.")

API_BASE = "https://api.wopr.tailandtraillabs.org"

#
# Get the game in question
# Get the list of pieces
# Get the list of mlimages for that game
# Compare the 2 and see what's missing.
# it's position that matters.
# then light level/intensity, but they must have at least 1 each of warm/neural/cool at 70% intensity.
#

@st.cache_data(ttl=60)
def fetch_games():
  response = httpx.get(f"{API_BASE}/api/v2/games")
  response.raise_for_status()
  return response.json()

def fetch_pieces(game_id):
  response = httpx.get(f"{API_BASE}/api/v2/pieces/gameid/{game_id}")
  response.raise_for_status()
  return response.json()

def fetch_config():
  response = httpx.get(f"{API_BASE}/api/v2/config/all")
  response.raise_for_status()
  return response.json()

def post_json(url: str, payload: dict) -> requests.Response:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response

def selectGame():
    games = fetch_games()
    game_names = [game['name'] for game in games]
    selected_game_name = st.selectbox(
        "Select a game:",
        options=game_names
    )
    selected_game = next(g for g in games if g['name'] == selected_game_name)
    st.session_state.selectedGame = selected_game
    return selected_game

config = fetch_config()
selectedGame = selectGame()

