import streamlit as st
import httpx
import pandas as pd

st.title("WOPR ML Image Coverage")
st.write("Checking ML training image coverage across pieces, positions, and lighting conditions.")

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

def fetch_mlimages(game_id):
    response = httpx.get(f"{API_BASE}/api/v2/images/gameid/{game_id}")
    response.raise_for_status()
    return response.json()

def fetch_config():
    response = httpx.get(f"{API_BASE}/api/v2/config/all")
    response.raise_for_status()
    return response.json()

def selectGame():
    games = fetch_games()
    game_names = [game['name'] for game in games]
    selected_game_name = st.selectbox("Select a game:", options=game_names)
    selected_game = next(g for g in games if g['name'] == selected_game_name)
    return selected_game

# Load data
config = fetch_config()
selectedGame = selectGame()
pieces = fetch_pieces(selectedGame['id'])
mlimages = fetch_mlimages(selectedGame['id'])

# Extract config values
positions = config["object"]["positions"]
color_temps = ["warm", "neutral", "cool"]  # from config["lightSettings"]["temp"]
intensities = config["lightSettings"]["intensity"]  # [10, 20, 30, ..., 100]

st.write(f"**Requirements:**")
st.write(f"- All positions covered: {len(positions)} positions")
st.write(f"- Center position coverage: {len(intensities)} intensities × {len(color_temps)} temps = {len(intensities) * len(color_temps)} combinations")
st.write(f"- Random position: >3 images")

# Build analysis per piece
piece_status = []

for piece in pieces:
    piece_id = piece["id"]
    piece_name = piece["name"]
    
    # Get all images for this piece
    piece_images = [img for img in mlimages if img.get("piece_id") == piece_id]
    
    # CHECK 1: At least 1 image per position
    position_coverage = {}
    for pos_label, pos_value in positions.items():
        matching = [img for img in piece_images if img.get("object_position") == pos_value]
        position_coverage[pos_label] = len(matching)
    
    positions_complete = all(count > 0 for count in position_coverage.values())
    missing_positions = [pos for pos, count in position_coverage.items() if count == 0]
    
    # CHECK 2: Center position - all intensity/temp combinations
    center_images = [img for img in piece_images if img.get("object_position") == "center"]
    center_combos = set()
    for img in center_images:
        combo = (img.get("light_intensity"), img.get("color_temp"))
        center_combos.add(combo)
    
    required_combos = {(intensity, temp) for intensity in intensities for temp in color_temps}
    center_complete = center_combos >= required_combos
    missing_combos = required_combos - center_combos
    
    # CHECK 3: Random position - more than 3 images
    random_images = [img for img in piece_images if img.get("object_position") == "random"]
    random_count = len(random_images)
    random_complete = random_count > 3
    
    # Overall status
    all_complete = positions_complete and center_complete and random_complete
    
    piece_status.append({
        "Piece": piece_name,
        "All Positions": "✓" if positions_complete else f"✗ Missing: {', '.join(missing_positions)}",
        "Center Coverage": "✓" if center_complete else f"✗ Missing {len(missing_combos)} combos",
        "Random Count": f"✓ ({random_count})" if random_complete else f"✗ ({random_count})",
        "Complete": "✓ READY" if all_complete else "✗ INCOMPLETE",
        "_sort": all_complete  # for sorting
    })

# Convert to DataFrame
df = pd.DataFrame(piece_status)
df = df.sort_values("_sort", ascending=True)  # incomplete first
df = df.drop(columns=["_sort"])

# Summary
total_pieces = len(pieces)
complete_pieces = len([p for p in piece_status if p["Complete"] == "✓ READY"])
incomplete_pieces = total_pieces - complete_pieces

st.write("---")
st.write("## Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Pieces", total_pieces)
col2.metric("Complete", complete_pieces)
col3.metric("Incomplete", incomplete_pieces)

# Filter
st.write("## Piece Status")
filter_choice = st.radio("Show:", ["All Pieces", "Complete Only", "Incomplete Only"], horizontal=True)

if filter_choice == "Complete Only":
    df = df[df["Complete"] == "✓ READY"]
elif filter_choice == "Incomplete Only":
    df = df[df["Complete"] != "✓ READY"]

st.dataframe(df, use_container_width=True, hide_index=True)

# Detailed breakdown for selected piece
st.write("---")
st.write("## Detailed Breakdown")
selected_piece_name = st.selectbox("Select piece for details:", [p["name"] for p in pieces])
selected_piece = next(p for p in pieces if p["name"] == selected_piece_name)
selected_piece_images = [img for img in mlimages if img.get("piece_id") == selected_piece["id"]]

tab1, tab2, tab3 = st.tabs(["Position Coverage", "Center Combos", "Random Images"])

with tab1:
    pos_rows = []
    for pos_label, pos_value in positions.items():
        count = len([img for img in selected_piece_images if img.get("object_position") == pos_value])
        pos_rows.append({"Position": pos_label, "Count": count, "Status": "✓" if count > 0 else "✗"})
    st.dataframe(pd.DataFrame(pos_rows), use_container_width=True, hide_index=True)

with tab2:
    center_imgs = [img for img in selected_piece_images if img.get("object_position") == "center"]
    combo_rows = []
    for intensity in intensities:
        for temp in color_temps:
            exists = any(img.get("light_intensity") == intensity and img.get("color_temp") == temp 
                        for img in center_imgs)
            combo_rows.append({
                "Intensity": intensity,
                "Temp": temp,
                "Status": "✓" if exists else "✗"
            })
    st.dataframe(pd.DataFrame(combo_rows), use_container_width=True, hide_index=True)

with tab3:
    random_imgs = [img for img in selected_piece_images if img.get("object_position") == "random"]
    st.write(f"**Count:** {len(random_imgs)} (need >3)")
    if random_imgs:
        random_rows = []
        for img in random_imgs:
            random_rows.append({
                "UUID": img.get("uuid"),
                "Temp": img.get("color_temp"),
                "Intensity": img.get("light_intensity"),
                "Rotation": img.get("object_rotation")
            })
        st.dataframe(pd.DataFrame(random_rows), use_container_width=True, hide_index=True)