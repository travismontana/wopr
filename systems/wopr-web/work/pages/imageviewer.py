import streamlit as st
import httpx
import os 
import requests

st.title("WOPR ML Image Capture System")
st.write("Welcome to the WOPR ML Image Capture System.")

API_BASE = "https://api.wopr.tailandtraillabs.org"

"""
We'll get the list of files from the API.
then we'll 

"""

def get_image_list():
    response = httpx.get(f"{API_BASE}/api/v2/images/gameid/4")
    response.raise_for_status()
    st.write(f"Found: {response.json()}")
    for img in response.json()[0]:
        img['thumb_url'] = f"https://thumbor.wopr.tailandtraillabs.org/unsafe/300x0/ml/incoming/{img['filenames']['thumbImageFilename']}"
        img['full_url'] = f"https://images.wopr.tailandtraillabs.org/ml/incoming/{img['filenames']['fullImageFilename']}"
        img['title'] = f"Piece {img['piece_id']} - Game {img['game_catalog_id']}"
    return img

imgDict = get_image_list()
for img in imgDict:
    images = [
        {"title": img['title'], "thumb": img['thumb_url'], "full": img['full_url']},
    ]

st.set_page_config(layout="wide")
st.title("Image Gallery (click thumbnail opens full-size)")

cols_per_row = 5
for row_start in range(0, len(images), cols_per_row):
    row = images[row_start : row_start + cols_per_row]
    cols = st.columns(cols_per_row)
    for col, img in zip(cols, row):
        with col:
            st.markdown(
                f"""
                <a href="{img['full']}" target="_blank" rel="noopener noreferrer">
                  <img src="{img['thumb']}" style="width:100%; border-radius:8px;" />
                </a>
                <div style="font-size: 0.85rem; opacity: 0.8;">{img.get('title','')}</div>
                """,
                unsafe_allow_html=True,
            )
