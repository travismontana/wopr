import streamlit as st
import httpx
import os 
import requests

st.title("WOPR ML Image Capture System")
st.write("Welcome to the WOPR ML Image Capture System.")

API_BASE = "https://api.wopr.tailandtraillabs.org"

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

def selectPiece(selectedGame):
    pieces = fetch_pieces(selectedGame['id'])
    piece_names = [piece['name'] for piece in pieces]
    selected_piece_name = st.selectbox(
        "Select a piece:",
        options=piece_names
    )
    selected_piece = next(p for p in pieces if p['name'] == selected_piece_name)
    st.session_state.selectedPiece = selected_piece
    return selected_piece

def selectLightIntensity():
    selected_intensity = st.selectbox(
        "Choose light intensity:",
        options=config['lightSettings']['intensity']
    )
    return selected_intensity

def selectLightTemperature():
    temps = config["lightSettings"]["temp"]
    display_to_key = {
        f"{k} ({v})": k
        for k, v in temps.items()
    }

    if "light_temp_key" not in st.session_state:
        st.session_state.light_temp_key = "neutral"

    display_options = list(display_to_key.keys())

    # Find default index from stored key
    default_display = next(
        label for label, key in display_to_key.items()
        if key == st.session_state.light_temp_key
    )

    selected_display = st.selectbox(
        "Light temperature",
        options=display_options,
        index=display_options.index(default_display)
    )

    # Resolve back to key + value
    temp_key = display_to_key[selected_display]
    temp_value = temps[temp_key]
    
    return temp_value

def selectObjectRotation():
    selected_rotation = st.selectbox(
        "Choose object rotation:",
        options=config['object']['rotations']
    )
    return selected_rotation

def selectObjectPosition():
    selected_position = st.selectbox(
        "Choose object position:",
        options=list(config['object']['positions'].keys())
    )
    return selected_position

if "lightTemp" not in st.session_state:
    st.session_state.lightTemp = "neutral"
if "lightIntensity" not in st.session_state:
    st.session_state.lightIntensity = "70"
if "objectRotation" not in st.session_state:
    st.session_state.objectRotation = "0"
if "objectPosition" not in st.session_state:
    st.session_state.objectPosition = "random"
if "selectedPiece" not in st.session_state:
    st.session_state.selectedPiece = None
if "selectedGame" not in st.session_state:
    st.session_state.selectedGame = None

selectedGame = selectGame()
selectedPiece = selectPiece(selectedGame)
st.write(f"You selected piece: {selectedPiece['name']} from game: {selectedGame['name']}")

config = fetch_config()

lightIntensity = selectLightIntensity()
lightTemp = selectLightTemperature()
objectRotation = selectObjectRotation()
objectPosition = selectObjectPosition()

with st.form("capture_form"):
    submit = st.form_submit_button("Capture Image")
    if submit:
        payload = {
            "game_id": selectedGame['id'],
            "piece_id": selectedPiece['id'],
            "light_intensity": lightIntensity,
            "color_temp": lightTemp,
            "object_rotation": objectRotation,
            "object_position": objectPosition
        }
        post_json(f"{API_BASE}/api/v2/mlimages/capture", payload)
        st.success("Image capture request submitted!")