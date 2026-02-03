import streamlit as st
import httpx
import random
import re
import logging
import sys
from datetime import datetime
from pathlib import Path

# -------------------------
# Logging
# -------------------------
LOGGER_NAME = "wopr.singleplayer"

def setup_logger() -> logging.Logger:
	logger = logging.getLogger(LOGGER_NAME)
	if logger.handlers:
		return logger  # already configured

	logger.setLevel(logging.INFO)

	handler = logging.StreamHandler(sys.stdout)
	fmt = logging.Formatter(
		fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S",
	)
	handler.setFormatter(fmt)
	logger.addHandler(handler)

	return logger

log = setup_logger()

# -------------------------
# Streamlit UI
# -------------------------
st.title("WOPR Game Interface")
st.write("Welcome to the WOPR Game Interface.")

API_BASE = "https://api.wopr.tailandtraillabs.org"

PLAYPHRASES = [
	"My move is made",
	"The feud continues",
	"The next blow is struck",
]

# -------------------------
# Session State
# -------------------------
if "session_uuid" not in st.session_state:
	st.session_state.session_uuid = None
if "session_id" not in st.session_state:
	st.session_state.session_id = None
if "current_round" not in st.session_state:
	st.session_state.current_round = 0
if "current_round_play" not in st.session_state:
	st.session_state.current_round_play = 0
if "round_started" not in st.session_state:
	st.session_state.round_started = False
if "selected_game" not in st.session_state:
	st.session_state.selected_game = None
if "start_game_info" not in st.session_state:
	st.session_state.start_game_info = None

# Turn-stability for Streamlit widgets (IMPORTANT)
if "turn_token" not in st.session_state:
	st.session_state.turn_token = None
if "turn_phrase" not in st.session_state:
	st.session_state.turn_phrase = random.choice(PLAYPHRASES)
if "playnote" not in st.session_state:
	st.session_state.playnote = ""


# -------------------------
# API Calls
# -------------------------
@st.cache_data(ttl=240)
def fetch_config():
	url = f"{API_BASE}/api/v2/config/all"
	log.info(f"GET {url}")
	response = httpx.get(url, timeout=30.0)
	response.raise_for_status()
	log.info("Config fetched")
	return response.json()


config = fetch_config()


@st.cache_data(ttl=240)
def fetch_games():
	url = f"{API_BASE}/api/v2/games"
	log.info(f"GET {url}")
	response = httpx.get(url, timeout=30.0)
	response.raise_for_status()
	log.info("Games fetched")
	return response.json()

def newSession(game_id):
	url = f"{API_BASE}/api/v2/session/new/{game_id}"
	log.info(f"GET {url}")
	response = httpx.get(url, timeout=30.0)
	response.raise_for_status()
	sessionuuid = response.json().get("uuid")
	sessionid = response.json().get("id")
	log.info(f"BLAH: {response.json()}")
	log.info(f"New session created sessionuuid={sessionuuid} sessionid={sessionid}")
	return sessionuuid, sessionid

def takeCapture(sessionuuid, camid, suffix):
	filename = f"game-{sessionuuid}-round{st.session_state.current_round}-{suffix}.jpg"
	payload = {
		"camid": camid,
		"filename": filename,
		"sessionuuid": sessionuuid,
	}
	url = f"{API_BASE}/api/v2/session/capture"
	log.info(f"POST {url} camid={camid} filename={filename} sessionuuid={sessionuuid}")
	response = httpx.post(url, json=payload, timeout=120.0)
	response.raise_for_status()
	log.info("Capture OK")
	return response.json()


def workplayer(playername, playerkind):
	isbot = playerkind != "human"
	payload = {
		"name": playername,
		"isbot": isbot,
	}
	url = f"{API_BASE}/api/v2/players"
	log.info(f"POST {url} name={playername} isbot={isbot}")
	response = httpx.post(url, json=payload, timeout=30.0)
	response.raise_for_status()
	data = response.json()
	player = data.get('data',data)
	log.info(f"Player OK id={player.get('id')} name={player.get('name')} isbot={player.get('isbot')}")
	return player


def player_key_sort(k: str) -> int:
	m = re.search(r"(\d+)$", k)
	return int(m.group(1)) if m else 0

def updateplaydb(session_id, player_id, gameid, play_note, imagefile):
		imagefilename = Path(imagefile.get("filename")).name
		log.info(f"Fetched filename: {imagefilename}")
		payload = {
			"sessionid": st.session_state.session_id,
			"playerid": player_id,
			"gameid": gameid,
			"note": play_note,
			"filename": imagefilename
		}
		log.info(f"Updating player DB with payload: {payload}")
		url = f"{API_BASE}/api/v2/plays"
		response = httpx.post(url, json=payload, timeout=30.0)
		response.raise_for_status()
		log.info("Player DB updated successfully")
		return response

# -------------------------
# UI Flow
# -------------------------
if not st.session_state.start_game_info:
	# Step 1: How many total players? (OUTSIDE form so it can rerun)
	num_players = st.number_input(
		"Total Players (including yourself):",
		min_value=2,
		max_value=6,
		value=3,
		step=1
	)
	
	with st.form("game_form", enter_to_submit=False):
		st.divider()
		
		# Step 2: Player 1 is always human
		st.subheader("Player 1 (Human)")
		p1_name = st.text_input("Name:", "bpfx", key="p1_name")
		
		# Step 3: Additional players - choose human or bot
		players_config = [{"name": p1_name, "type": "human"}]
		
		for i in range(2, int(num_players) + 1):
			st.divider()
			st.subheader(f"Player {i}")
			col1, col2 = st.columns([2, 1])
			
			with col1:
				p_name = st.text_input(
					"Name/Character:",
					f"player{i}",
					key=f"p{i}_name"
				)
			with col2:
				p_type = st.selectbox(
					"Type:",
					["bot", "human"],
					key=f"p{i}_type"
				)
			
			players_config.append({"name": p_name, "type": p_type})
		
		submitted = st.form_submit_button("Unleash the spice", key="submit_game_setup")
		
		if submitted:
			log.info(f"Game setup submitted with {num_players} players")
			
			# Build the players list
			players = []
			for i, config in enumerate(players_config, start=1):
				player_info = workplayer(config["name"], config["type"])
				player_info["name"] = config["name"]
				players.append(player_info)
				log.info(f"Player {i}: {config['name']} ({config['type']})")
			
			# Build gameinfo dict
			gameinfo = {f"player{i}": player for i, player in enumerate(players)}
			st.session_state.start_game_info = gameinfo
			log.info(f"Players stored in session: {list(gameinfo.keys())}")
			st.rerun()

else:
	names = ", ".join([player["name"] for player in st.session_state.start_game_info.values()])
	st.write(f"{names} you have been entered into the rolls of kanly.")

	# Game Selection
	if st.session_state.session_uuid is None:
		games = fetch_games()
		game_names = [game["name"] for game in games]
		selected_game_name = st.selectbox("Select a game:", options=game_names, key="game_selectbox")
		selected_game = next(g for g in games if g["name"] == selected_game_name)
		st.session_state.selected_game = selected_game

		if st.button("Start New Game", key="start_new_game_button"):
			log.info(f"Start New Game clicked game_id={selected_game.get('id')} game_name={selected_game.get('name')}")
			st.session_state.session_uuid, st.session_state.session_id = newSession(selected_game["id"])
			st.session_state.current_round = 1
			st.session_state.current_round_play = 0
			st.session_state.round_started = False

			st.session_state.turn_token = None
			st.session_state.turn_phrase = random.choice(PLAYPHRASES)
			st.session_state.playnote = ""

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
			if st.button(f"Start Round {st.session_state.current_round}", key=f"start_round_{st.session_state.current_round}"):
				log.info(f"Start Round clicked round={st.session_state.current_round}")
				st.session_state.current_round_play = 0

				try:
					with st.spinner("Capturing start of round..."):
						_ = takeCapture(
							st.session_state.session_uuid,
							config.get("default_camera_id", 1),
							"start",
						)
				except Exception as e:
					log.exception("Start-round capture failed")
					st.error(f"Start-round capture failed: {e}")
				else:
					st.success(f"Round {st.session_state.current_round} started - Initial state captured")
					st.session_state.round_started = True

					st.session_state.turn_token = None
					st.session_state.turn_phrase = random.choice(PLAYPHRASES)
					st.session_state.playnote = ""

					st.rerun()

		# Round in progress
		else:
			player_keys = sorted(
				[k for k in st.session_state.start_game_info.keys()],
				key=player_key_sort,
			)

			# All players have played this round
			if st.session_state.current_round_play >= len(player_keys):
				if st.button(f"End Round {st.session_state.current_round}", key=f"end_round_{st.session_state.current_round}"):
					log.info(f"End Round clicked round={st.session_state.current_round}")
					try:
						with st.spinner("Capturing end of round..."):
							_ = takeCapture(
								st.session_state.session_uuid,
								config.get("default_camera_id", 1),
								"end",
							)
					except Exception as e:
						log.exception("End-round capture failed")
						st.error(f"End-round capture failed: {e}")
					else:
						st.success(f"Round {st.session_state.current_round} ended - Final state captured")

						max_rounds = game.get("max_rounds", 10)
						if st.session_state.current_round >= max_rounds:
							log.info("Game complete")
							st.balloons()
							st.success("🎮 Game Complete!")
							if st.button("Start New Game", key="start_new_game_after_complete"):
								log.info("Start New Game after complete clicked")
								st.session_state.session_uuid = None
								st.session_state.current_round = 0
								st.session_state.current_round_play = 0
								st.session_state.round_started = False

								st.session_state.turn_token = None
								st.session_state.turn_phrase = random.choice(PLAYPHRASES)
								st.session_state.playnote = ""

								st.rerun()
						else:
							st.session_state.current_round += 1
							st.session_state.current_round_play = 0
							st.session_state.round_started = False

							st.session_state.turn_token = None
							st.session_state.turn_phrase = random.choice(PLAYPHRASES)
							st.session_state.playnote = ""

							log.info(f"Advance to next round round={st.session_state.current_round}")
							st.rerun()

			# Player turn
			else:
				current_player_key = player_keys[st.session_state.current_round_play]
				current_player = st.session_state.start_game_info[current_player_key]

				play_num = st.session_state.current_round_play + 1
				turn_token = f"r{st.session_state.current_round}-p{st.session_state.current_round_play}"

				if st.session_state.turn_token != turn_token:
					st.session_state.turn_token = turn_token
					st.session_state.turn_phrase = random.choice(PLAYPHRASES)
					st.session_state.playnote = ""
					log.info(f"New turn token={turn_token} player={current_player.get('name')}")

				st.info(f"Round {st.session_state.current_round} - {current_player['name']}'s turn (Play {play_num})")

				with st.form("play_form", enter_to_submit=False):
					st.text_area(
						f"Play Note for {current_player['name']}:",
						key="playnote",
					)

					submitted = st.form_submit_button(
						st.session_state.turn_phrase,
						key="submit_play",
					)

					if submitted:
						log.info(f"Play submitted turn_token={turn_token} player={current_player.get('name')} play_num={play_num}")
						try:
							with st.spinner("Capturing..."):
								suffix = f"{current_player['name']}-play{play_num}"
								result = takeCapture(
									st.session_state.session_uuid,
									config.get("default_camera_id", 1),
									suffix,
								)
						except Exception as e:
							log.exception("Capture failed")
							st.error(f"Capture failed: {e}")
						else:
							st.json(result)
							result = updateplaydb(st.session_state.session_id,current_player['id'], game.get("id"), st.session_state.playnote,result)
							log.info(f"Play DB update result: {result}")
							st.success(f"Round {st.session_state.current_round} - {current_player['name']}'s play captured")
							st.session_state.current_round_play += 1
							log.info(f"Advance to next play current_round_play={st.session_state.current_round_play}")
							st.rerun()

		# Emergency reset
		st.divider()
		if st.button("End Game", type="secondary", key="end_game_button"):
			log.info("End Game clicked (reset session state)")
			st.session_state.session_uuid = None
			st.session_state.current_round = 0
			st.session_state.current_round_play = 0
			st.session_state.round_started = False

			st.session_state.turn_token = None
			st.session_state.turn_phrase = random.choice(PLAYPHRASES)
			st.session_state.playnote = ""

			st.rerun()
