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


config = fetch_config()

st.header("Current WOPR Configuration")
st.json(config)