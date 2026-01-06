import streamlit as st
import httpx
import requests
import time

st.set_page_config(page_title="WOPR ML Image Capture", layout="centered")

st.title("WOPR ML Image Capture System")
st.write("Welcome to the WOPR ML Image Capture System.")

API_BASE = "https://api.wopr.tailandtraillabs.org"


# -----------------------
# API helpers
# -----------------------
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


# -----------------------
# Session state defaults
# -----------------------
def init_state():
    ss = st.session_state

    ss.setdefault("selected_game_name", None)
    ss.setdefault("selected_game_id", None)

    ss.setdefault("selected_piece_name", None)
    ss.setdefault("selected_piece_id", None)
    ss.setdefault("piece_game_id", None)  # track which game the current piece belongs to

    ss.setdefault("lightIntensity", None)   # value
    ss.setdefault("lightTemp", None)        # key
    ss.setdefault("objectRotationIdx", 0)   # index into rotations list
    ss.setdefault("objectPositionKey", None)  # key into positions dict

init_state()


# -----------------------
# Selection popovers
# -----------------------
def popover_select_game(games):
    game_names = [g["name"] for g in games]
    if not game_names:
        st.error("No games returned from API.")
        st.stop()

    # Initialize to first game once
    if st.session_state.selected_game_name not in game_names:
        first = games[0]
        st.session_state.selected_game_name = first["name"]
        st.session_state.selected_game_id = first["id"]

    with st.popover("Select Game"):
        chosen = st.radio(
            "Games",
            options=game_names,
            index=game_names.index(st.session_state.selected_game_name),
            label_visibility="collapsed",
        )

    if chosen != st.session_state.selected_game_name:
        selected = next(g for g in games if g["name"] == chosen)
        st.session_state.selected_game_name = selected["name"]
        st.session_state.selected_game_id = selected["id"]

        # IMPORTANT: only reset piece when game changes
        st.session_state.piece_game_id = None
        st.session_state.selected_piece_name = None
        st.session_state.selected_piece_id = None


def popover_select_piece(pieces):
    piece_names = [p["name"] for p in pieces]
    if not piece_names:
        st.warning("No pieces returned for this game.")
        return

    # If no piece yet, pick first
    if st.session_state.selected_piece_name not in piece_names:
        first = pieces[0]
        st.session_state.selected_piece_name = first["name"]
        st.session_state.selected_piece_id = first["id"]

    with st.popover("Select Piece"):
        chosen = st.radio(
            "Pieces",
            options=piece_names,
            index=piece_names.index(st.session_state.selected_piece_name),
            label_visibility="collapsed",
        )

    if chosen != st.session_state.selected_piece_name:
        selected = next(p for p in pieces if p["name"] == chosen)
        st.session_state.selected_piece_name = selected["name"]
        st.session_state.selected_piece_id = selected["id"]


def popover_select_light_intensity(config):
    intensities = config["lightSettings"]["intensity"]
    if not intensities:
        st.error("Config: no light intensities.")
        st.stop()

    # default to first
    if st.session_state.lightIntensity is None:
        st.session_state.lightIntensity = intensities[0]

    # normalize for index lookup
    cur = st.session_state.lightIntensity
    if isinstance(intensities[0], int) and isinstance(cur, str) and cur.isdigit():
        cur = int(cur)

    with st.popover("Select Light Intensity"):
        chosen = st.radio(
            "Intensity",
            options=intensities,
            index=intensities.index(cur) if cur in intensities else 0,
            label_visibility="collapsed",
            horizontal=True if len(intensities) <= 6 else False,
        )

    st.session_state.lightIntensity = chosen


def popover_select_light_temp(config):
    temps = config["lightSettings"]["temp"]  # dict key->kelvin
    keys = list(temps.keys())
    if not keys:
        st.error("Config: no light temperatures.")
        st.stop()

    # default to neutral if present
    if st.session_state.lightTemp is None:
        st.session_state.lightTemp = "neutral" if "neutral" in keys else keys[0]

    if st.session_state.lightTemp not in keys:
        st.session_state.lightTemp = keys[0]

    def disp(k): return f"{k} ({temps[k]})"
    options = [disp(k) for k in keys]
    cur_disp = disp(st.session_state.lightTemp)
    disp_to_key = {disp(k): k for k in keys}

    with st.popover("Select Light Temperature"):
        chosen_disp = st.radio(
            "Temp",
            options=options,
            index=options.index(cur_disp) if cur_disp in options else 0,
            label_visibility="collapsed",
            horizontal=True if len(options) <= 4 else False,
        )

    st.session_state.lightTemp = disp_to_key[chosen_disp]


def popover_select_rotation(config):
    rotations = config["object"]["rotations"]
    if not rotations:
        st.error("Config: no rotations.")
        st.stop()

    labels = [f"{d}°" for d in rotations]
    idx = st.session_state.objectRotationIdx
    if not isinstance(idx, int) or idx < 0 or idx >= len(labels):
        idx = 0
        st.session_state.objectRotationIdx = 0

    with st.popover("Select Rotation"):
        chosen = st.radio(
            "Rotation",
            options=labels,
            index=idx,
            label_visibility="collapsed",
            horizontal=True if len(labels) <= 6 else False,
        )

    st.session_state.objectRotationIdx = labels.index(chosen)


def popover_select_position(config):
    positions = config["object"]["positions"]  # dict label->value
    keys = list(positions.keys())
    if not keys:
        st.error("Config: no positions.")
        st.stop()

    if st.session_state.objectPositionKey is None:
        st.session_state.objectPositionKey = "Center" if "Center" in keys else keys[0]

    if st.session_state.objectPositionKey not in keys:
        st.session_state.objectPositionKey = keys[0]

    with st.popover("Select Position"):
        chosen = st.radio(
            "Position",
            options=keys,
            index=keys.index(st.session_state.objectPositionKey),
            label_visibility="collapsed",
        )

    st.session_state.objectPositionKey = chosen


# -----------------------
# Actions
# -----------------------
def build_capture_payload(config, single_temp=None, single_intensity=None):
    # rotations list -> index to actual degrees
    rotations = config["object"]["rotations"]
    positions = config["object"]["positions"]

    rotation_idx = st.session_state.objectRotationIdx
    rotation_deg = rotations[rotation_idx]

    pos_key = st.session_state.objectPositionKey
    pos_value = positions[pos_key]

    payload = {
        "game_catalog_id": st.session_state.selected_game_id,
        "piece_id": st.session_state.selected_piece_id,
        "light_intensity": single_intensity if single_intensity is not None else st.session_state.lightIntensity,
        "color_temp": single_temp if single_temp is not None else st.session_state.lightTemp,
        "object_rotation": rotation_deg,
        "object_position": pos_value,
    }
    return payload


def run_all_lights(config):
    status_line = st.empty()
    for cTemp in config["lightSettings"]["temp"].keys():
        for cIntensity in config["lightSettings"]["intensity"]:
            status_line.write(f"Capturing: temp={cTemp}, intensity={cIntensity}")
            payload = build_capture_payload(config, single_temp=cTemp, single_intensity=cIntensity)
            post_json(f"{API_BASE}/api/v2/mlimages/capture", payload)
            time.sleep(1)
    status_line.write("Done.")
    notifications("All-light capture requests complete.")


def run_single_light(config):
    payload = build_capture_payload(config)
    post_json(f"{API_BASE}/api/v2/mlimages/capture", payload)
    notifications("Single light capture request complete.")


def reset_all():
    # Keep it simple: clear the selection state, let defaults repopulate on rerun
    for k in [
        "selected_game_name", "selected_game_id",
        "selected_piece_name", "selected_piece_id", "piece_game_id",
        "lightIntensity", "lightTemp",
        "objectRotationIdx", "objectPositionKey",
    ]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()

def notifications(message: str):
    # API/api/v2/notifications
    # Color green
    payload = {
        "message": message,
        "title": "WOPR ML Image Capture",
        "color": "green"
    }
    post_json(f"{API_BASE}/api/v2/notifications", payload)

# -----------------------
# Main UI
# -----------------------
config = fetch_config()
games = fetch_games()

# 1) Selection buttons (each opens a popover)
st.subheader("Selections")

popover_select_game(games)

# Load pieces for the currently selected game
if st.session_state.selected_game_id is not None:
    pieces = fetch_pieces(st.session_state.selected_game_id)

    # Ensure piece selection is only reset when game changes
    if st.session_state.piece_game_id != st.session_state.selected_game_id:
        st.session_state.piece_game_id = st.session_state.selected_game_id
        st.session_state.selected_piece_name = None
        st.session_state.selected_piece_id = None

    popover_select_piece(pieces)

# Remaining selectors
popover_select_light_intensity(config)
popover_select_light_temp(config)
popover_select_rotation(config)
popover_select_position(config)

st.divider()

# 2) Current selection readout
st.subheader("Current Selection")

rotations = config["object"]["rotations"]
positions = config["object"]["positions"]

game_line = st.session_state.selected_game_name or "(none)"
piece_line = st.session_state.selected_piece_name or "(none)"
temp_line = st.session_state.lightTemp or "(none)"
intensity_line = st.session_state.lightIntensity if st.session_state.lightIntensity is not None else "(none)"
rotation_line = f"{rotations[st.session_state.objectRotationIdx]}°" if rotations else "(none)"
pos_key = st.session_state.objectPositionKey or "(none)"
pos_val = positions.get(st.session_state.objectPositionKey) if st.session_state.objectPositionKey in positions else "(none)"

st.code(
    "\n".join([
        f"Game:            {game_line}",
        f"Piece:           {piece_line}",
        f"Light Temp:      {temp_line}",
        f"Light Intensity: {intensity_line}",
        f"Rotation:        {rotation_line}",
        f"Position:        {pos_key} -> {pos_val}",
    ])
)

st.divider()

# 3) Action buttons row
st.subheader("Actions")

# Basic guardrails
ready = all([
    st.session_state.selected_game_id,
    st.session_state.selected_piece_id,
    st.session_state.lightTemp,
    st.session_state.lightIntensity is not None,
    st.session_state.objectPositionKey,
])

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("Run all lights", use_container_width=True, disabled=not ready):
        run_all_lights(config)
        st.success("All-light capture requests submitted!")

with c2:
    if st.button("Run single light", use_container_width=True, disabled=not ready):
        run_single_light(config)
        st.success("Single capture request submitted!")

with c3:
    if st.button("Reset", use_container_width=True):
        reset_all()

if not ready:
    st.info("Select Game + Piece + Light settings + Position before running.")
