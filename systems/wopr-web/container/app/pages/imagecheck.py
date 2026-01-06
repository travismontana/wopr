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

def fetch_mlimages(game_id):
  response = httpx.get(f"{API_BASE}/api/v2/images/gameid/{game_id}")
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

config = fetch_config()
selectedGame = selectGame()
selectedPiece = selectPiece(selectedGame)
pieces = fetch_pieces(selectedGame['id'])
mlimages = fetch_mlimages(selectedGame['id'])
#st.write(f"mlimages: {mlimages}")
#
# dict:
# missing = {
#  piece_id: {
#     'positions': [list of missing positions], (from config['object']['positions'])  ((key:value))])
#     'defaults': [list of missing default images], # to be added later
#     'numrandom': int,
#  }
#

missing = {}
has = {}
status_line = st.empty()

# --- build per-position status rows for the selected piece ---
piece_id = selectedPiece["id"]
piece_name = selectedPiece["name"]

rows = []
status_line = st.empty()

# optional: pre-index images for speed/readability
images_for_piece = [img for img in mlimages if img.get("piece_id") == piece_id]

for position in config["object"]["positions"].values():
    status_line.text(f"Checking position: {position}")

    matching = [img for img in images_for_piece if img.get("object_position") == position]
    count = len(matching)

    ok = count > 0

    rows.append({
        "Piece": piece_name,
        "Position": position,
        "Status": "OK" if ok else "MISSING",
        "Count": count,
    })

# --- summary dicts (optional, if you still want them) ---
missing = {
    piece_id: {
        "piece_name": piece_name,
        "positions": [r["Position"] for r in rows if r["Status"] == "MISSING"],
        "defaults": [],
        "numrandom": sum(1 for r in rows if r["Status"] == "MISSING" and r["Position"] == "random"),
    }
} if any(r["Status"] == "MISSING" for r in rows) else {}

has = {
    piece_id: {
        "piece_name": piece_name,
        "positions": [r["Position"] for r in rows if r["Status"] == "OK"],
        "defaults": [],
        "numrandom": sum(1 for r in rows if r["Status"] == "OK" and r["Position"] == "random"),
    }
} if any(r["Status"] == "OK" for r in rows) else {}

# --- UI output ---
#st.write("## Missing ML Images Summary")
#st.write(missing)

#st.write("## Available ML Images Summary")
#st.write(has)

st.write("## ML Image Coverage (Selected Piece)")
st.dataframe(
    rows,
    use_container_width=True,
    hide_index=True,
)
