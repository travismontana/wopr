import streamlit as st
import httpx
import os 
import requests

st.title("WOPR ML Image Capture System")
st.write("Welcome to the WOPR ML Image Capture System.")

API_BASE = "https://api.wopr.tailandtraillabs.org"
IMGURL = "https://images.wopr.tailandtraillabs.org/ml/incoming/"
THUMBURL = f"https://imgproxy.wopr.tailandtraillabs.org/300x/{IMGURL}"

"""
We'll get the list of files from the API.
then we'll 

"""

def get_image_list():
    response = httpx.get(f"{API_BASE}/api/v2/images/gameid/4")
    response.raise_for_status()
    #st.write(f"Found: {response.json()}")
    return response.json()


images = []
imgDict = get_image_list()
for img in imgDict:
    #st.write(f"Image Title: {img}")
    id = img['id']
    title = img['id']
    thumbnail_url = f"{THUMBURL}{img['filenames']['fullImageFilename']}"
    full_image_url = f"{IMGURL}{img['filenames']['fullImageFilename']}"
    images.append({
        'id': id,
        'title': title,
        'thumb': thumbnail_url,
        'full': full_image_url
    })
    


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
