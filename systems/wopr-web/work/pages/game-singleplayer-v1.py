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
if 'start_game_info' not in st.session_state:
	st.session_state.start_game_info = None

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
	if type == "human":
		isbot = False
	else:
	  isbot = True

	payload = {
		"name": playername,
		"isbot": isbot
	}

	response = httpx.post(f"{API_BASE}/api/v2/players", json=payload)
	response.raise_for_status()
	st.json(response.json())
	return response.json()

if not st.session_state.start_game_info:
	with st.form("game_form", enter_to_submit=False	):
		playername = st.text_input("Player 1: ", "bpfx")
		bot1character = st.text_input("Rival 1 Character:", "bot1")
		bot2character = st.text_input("Rival 2 Character:", "bot2")
		playercount = 3
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
			players  = [player1info, bot1info, bot2info]
			# Create a dict that has {playercount} entries, each called player#
			gameinfo={f"player{i}": player for i, player in enumerate(players)}
			st.session_state.start_game_info = gameinfo
			st.rerun()
else:
	# Welcome all to the rolls of kanly
	names = ", ".join([player['name'] for player in st.session_state.start_game_info.values()])
	st.write(f"{names} you have been entered into the rolls of kanly.")
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
			if st.button(f"Play {st.session_state.current_round_play} Round {st.session_state.current_round}"):
				# Capture play state
				result = takeCapture(
					st.session_state.session_uuid,
					config.get('default_camera_id', 1),
					f"play{st.session_state.current_round_play}"
				)
				st.success(f"Round {st.session_state.current_round} - Play {st.session_state.current_round_play} - State captured")
				st.session_state.current_round_play += 1
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
		if st.button("End Game", type="secondary"):
			st.session_state.session_uuid = None
			st.session_state.current_round = 0
			st.session_state.current_round_play = 0
			st.session_state.round_started = False
			st.rerun()