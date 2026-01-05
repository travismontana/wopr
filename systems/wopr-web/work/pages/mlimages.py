import streamlit as st
import httpx

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

games = fetch_games()

game_names = [game['name'] for game in games]

selected_game_name = st.selectbox(
    "Choose a game:",
    options=game_names
)

# Find the full game object
selected_game = next(g for g in games if g['name'] == selected_game_name)

pieces = fetch_pieces(selected_game['id'])

st.write(f"Pieces for game: {selected_game_name}")
for piece in pieces:
    st.write(f"- Piece ID: {piece['id']}, Type: {piece['type']}, Position: ({piece['x']}, {piece['y']})")