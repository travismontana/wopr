import re
import streamlit as st

from lib.helpers import debug_log, debug_json
from lib.api import api_capture_move, api_new_game_session


def create_game_session() -> str:
    # 1. sanitize the note
    # 2. create the session via API
    debug_log(f"Creating game session")
    # Call the API to create a new game session
    response = api_new_game_session()
    debug_log("API response for new game session:")
    debug_log(response)
    return response.get("uuid", "unknown-uuid")


def capture_move(player_name: str, move: str, game_session_uuid: str):
    # 1. sanitize the inputs
    # 2. create the session
    # 3. determine the file path
    # 4. call capture
    debug_log(f"Capturing move for {player_name}: {move}")
    sanitized_player = sanitize(player_name)
    sanitized_move = sanitize(move)
    debug_log(f"Sanitized player: {sanitized_player}, move: {sanitized_move}")

    # now we have sanitized_player-sanitized_move
    # need to get to {base_path}/{ml_subdir}/{incoming_subdir}/game-{uuid}-{sanitized_player}-{sanitized_move}.jpg
    paths = st.session_state.get("paths", {})
    base_path = paths.get("base_path", "/dev/null")
    ml_subdir = paths.get("ml_subdir", "ml_data")
    incoming_subdir = paths.get("incoming_subdir", "incoming")
    file_path = f"{base_path}/{ml_subdir}/{incoming_subdir}/game-{game_session_uuid}-{sanitized_player}-{sanitized_move}.jpg"
    return api_capture_move(file_path)


def sanitize(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "_", s.lower())
