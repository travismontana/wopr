#
#
# WOPR - Single Page Interface
# -------------------------
# idea: a single page interface that can interact with the WOPR API
# -------------------------

import streamlit as st
import httpx
import random
import re
import logging
import sys
from datetime import datetime
from pathlib import Path
from helpers import *

# -------------------------
# Logging
# -------------------------


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
	"I was friend of Jamis",
	"Fear is the mind killer",
	"There is no escape",
	"You're worm food",
	"Hasta la vista wormy"
]

# ------------------------
# UI - Single Page - Logic
# -------------------------

def get_random_phrase() -> str:
    return random.choice(PLAYPHRASES)

# -------------------------
#  UI - Single Page - Interface
# -------------------------

st.header("Single Page Interface")
mainselection = ["Sessions", "Plays", "Games", "Pieces", "Players"]
mainselection_dict = {
    "Sessions": "sessions",
    "Plays": "plays",
    "Games": "games",
    "Pieces": "pieces",
    "Players": "players"
}
mainsection = st.selectbox("Select Section", mainselection)
selected_noun = mainselection_dict[mainsection]
data = get_all(selected_noun)
st.json(data, expanded=False)

edited_data = st.data_editor(
    data, 
    num_rows="dynamic",
    key="data_editor_1"
)

#st.data_editor(data, height=300)

if st.button("Save Changes"):
    st.write("Saving changes...")
    for row in edited_data:
        item_id = row.get("id")
        if item_id:
            # existing item, update it
            update_item(selected_noun, item_id, row)
        else:
            # new item, create it
            create_new(selected_noun, row)
    st.success("Changes saved!")