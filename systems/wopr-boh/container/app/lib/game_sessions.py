import re
import streamlit as st

from lib.helpers import debug_log, debug_json

def create_game_session():
    """Generate a new game session
    """
    number_of_players = st.select_slider("Number of players:", options=[1, 2, 3, 4])

def capture_move(player_name: str, move: str):
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
    file_path = f"{base_path}/{ml_subdir}/{incoming_subdir}/game-{


def sanitize(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "_", s.lower())