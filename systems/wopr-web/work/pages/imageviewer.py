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
    response = httpx.get(f"{API_BASE}/api/v2/images")
    response.raise_for_status()
    return response.json()

images = [
    {"title": "Board State 001", "thumb": "https://example.com/thumbs/1.jpg", "full": "https://example.com/full/1.jpg"},
    {"title": "Board State 002", "thumb": "https://example.com/thumbs/2.jpg", "full": "https://example.com/full/2.jpg"},
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
