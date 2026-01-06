import streamlit as st
import httpx
import os 
import requests
#import streamlit_imagegrid
from streamlit_image_gallery import streamlit_image_gallery

st.title("WOPR ML Image Capture System")
st.write("Welcome to the WOPR ML Image Capture System.")

API_BASE = "https://api.wopr.tailandtraillabs.org"
IMGURL = "https://images.wopr.tailandtraillabs.org/ml/incoming/"
THUMBURL = f"https://imgproxy.wopr.tailandtraillabs.org/insecure/resize:fit:300/plain/{IMGURL}"

def get_image_list():
    response = httpx.get(f"{API_BASE}/api/v2/images/gameid/names/4")
    response.raise_for_status()
    #st.write(f"Found: {response.json()}")
    return response.json()


images = []
urls = []
imgDict = get_image_list()
for img in imgDict:
    #st.write(f"Image Title: {img}")
    id = img['id']
    title = f"P:{img['piece_id']['name']} G:{img['game_catalog_id']} {img['light_intensity']}%@{img['color_temp']}"
    thumbnail_url = f"{THUMBURL}{img['filenames']['fullImageFilename']}"
    full_image_url = f"{IMGURL}{img['filenames']['fullImageFilename']}"
    images.append({
        'id': id,
        'title': title,
        'thumb': thumbnail_url,
        'full': full_image_url
    })
    urls.append(full_image_url)
    


st.set_page_config(layout="wide")
st.title("Image Gallery (click thumbnail opens full-size)")

#selected = streamlit_imagegrid.streamlit_imagegrid("visualization1", urls, 4, key='foo')
#t.write(f"Selected item: {selected}")
streamlit_image_gallery(images=urls)
#cols_per_row = 5
#for row_start in range(0, len(images), cols_per_row):
#    row = images[row_start : row_start + cols_per_row]
#    cols = st.columns(cols_per_row)
#    for col, img in zip(cols, row):
#        with col:
#            st.markdown(
#                f"""
#                <a href="{img['full']}" target="_blank" rel="noopener noreferrer">
#                  <img src="{img['thumb']}" style="width:100%; border-radius:8px;" />
#                </a>
#                <div style="font-size: 0.85rem; opacity: 0.8;">{img.get('title','')}</div>
#                """,
#                unsafe_allow_html=True,
#            )
