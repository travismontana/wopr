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

# Build coverage matrix
required_temps = ["warm", "neutral", "cool"]
required_intensity = 70
positions = config["object"]["positions"]

rows = []

for piece in pieces:
    piece_id = piece["id"]
    piece_name = piece["name"]
    
    # Get all images for this piece
    piece_images = [img for img in mlimages if img.get("piece_id") == piece_id]
    
    for pos_label, pos_value in positions.items():
        # Check each required color temp at 70% intensity
        coverage = {}
        for temp in required_temps:
            matching = [
                img for img in piece_images 
                if img.get("object_position") == pos_value 
                and img.get("color_temp") == temp 
                and img.get("light_intensity") == required_intensity
            ]
            coverage[temp] = len(matching) > 0
        
        # Determine status
        all_present = all(coverage.values())
        missing_temps = [t for t, present in coverage.items() if not present]
        
        status = "✓ OK" if all_present else f"✗ MISSING: {', '.join(missing_temps)}"
        
        rows.append({
            "Piece": piece_name,
            "Position": pos_label,
            "Warm": "✓" if coverage["warm"] else "✗",
            "Neutral": "✓" if coverage["neutral"] else "✗",
            "Cool": "✓" if coverage["cool"] else "✗",
            "Status": status
        })

# Convert to DataFrame
df = pd.DataFrame(rows)

# Summary stats
total_checks = len(rows)
complete = len([r for r in rows if "✓ OK" in r["Status"]])
incomplete = total_checks - complete

st.metric("Total Position Checks", total_checks)
col1, col2 = st.columns(2)
col1.metric("Complete", complete, delta=None)
col2.metric("Incomplete", incomplete, delta=None)

# Filter options
st.write("## Coverage Details")
filter_status = st.radio("Filter:", ["All", "Complete Only", "Incomplete Only"], horizontal=True)

if filter_status == "Complete Only":
    df = df[df["Status"] == "✓ OK"]
elif filter_status == "Incomplete Only":
    df = df[df["Status"] != "✓ OK"]

st.dataframe(df, use_container_width=True, hide_index=True)