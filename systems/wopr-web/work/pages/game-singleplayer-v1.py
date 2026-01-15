import streamlit as st
import httpx

st.title("WOPR Single Player Game Interface")
st.write("Welcome to the WOPR Single Player Game Interface.")

API_BASE = "https://api.wopr.tailandtraillabs.org"

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

def workplayer(playername, type):
	# Implement the logic to check if player exists in playerdb
	# If not, create the player and bot] with payload
	# payload = {
	#   docreate = true,
	#   name = {playername},
	#   type = {type}
	# }

	pass


with st.form("game_form", enter_to_submit=False	):
	playername = st.text_input("Player 1: ", "bpfx")
	bot1character = st.text_input("Rival 1 Character:", "")
	bot2character = st.text_input("Rival 2 Character:", "")
	submitted = st.form_submit_button("Unleash the spice")
	if submitted:
		# does player exist in playerdb
		# if not create and use
		# does rival exist in rivaldb
		# if not create and use
		# once those
		# Create game in newSession
		player1info = workplayer(playername, "human")
		bot1info = workplayer(bot1character, "bot")
		bot2info = workplayer(bot2character, "bot")
		