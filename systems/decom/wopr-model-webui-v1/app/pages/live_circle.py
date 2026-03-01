import requests
import streamlit as st
import numpy as np
import cv2
import os
from PIL import Image
from io import BytesIO

CAMURL = os.getenv("CAMURL", "http://localhost:8080")

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.title("Live CV Work")

@st.cache_data(ttl=30)
def fetch_snapshot(url: str) -> bytes:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.content

def get_images(url):
    try:
        raw = fetch_snapshot(url)
        image = Image.open(BytesIO(raw))
        return image, raw
    except Exception as e:
        st.error(f"Failed to fetch snapshot: {e}")
        st.stop()

cam_options = [
    {"name": "c950", "endpoint": f"{CAMURL}:5101/snapshot"},
    {"name": "c960", "endpoint": f"{CAMURL}:5100/snapshot"},
    {"name": "rPi", "endpoint": f"{CAMURL}:5102/snapshot"},
]

img_rgb_u8_c950, raw_u8_c950 = get_images(f"{CAMURL}:5101/snapshot")
img_rgb_u8_c960, raw_u8_c960 = get_images(f"{CAMURL}:5100/snapshot")


img_bgr_u8_c950 = cv2.cvtColor(np.array(img_rgb_u8_c950), cv2.COLOR_RGB2BGR)
img_bgr_u8_c960 = cv2.cvtColor(np.array(img_rgb_u8_c960), cv2.COLOR_RGB2BGR)

img_gry_u8_c950 = cv2.cvtColor(np.array(img_rgb_u8_c950), cv2.COLOR_RGB2GRAY)
img_gry_u8_c960 = cv2.cvtColor(np.array(img_rgb_u8_c960), cv2.COLOR_RGB2GRAY)

gaus_c950 = cv2.GaussianBlur(img_gry_u8_c950, (5, 5), 0)
gaus_c960 = cv2.GaussianBlur(img_gry_u8_c960, (5, 5), 0)

ret_c950, otsu_c950 = cv2.threshold(gaus_c950, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
ret_c960, otsu_c960 = cv2.threshold(gaus_c960, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

canny_c950 = cv2.Canny(otsu_c950, 20, 255)
canny_c960 = cv2.Canny(otsu_c960, 20, 255)

kernel = np.ones((7,7), np.uint8)

dila_c950 = cv2.dilate(canny_c950, kernel, iterations=1)
dila_c960 = cv2.dilate(canny_c960, kernel, iterations=1)

lines_c950 = cv2.HoughLinesP(dila_c950, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
lines_c960 = cv2.HoughLinesP(dila_c960, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)

if lines_c950 is not None:
    for i, line in enumerate(lines_c950):
        x1, y1, x2, y2 = line[0]
        cv2.line(img_bgr_u8_c950, (x1, y1), (x2, y2), (0, 255, 0), 2)

if lines_c960 is not None:
    for j, line in enumerate(lines_c960):
        x1, y1, x2, y2 = line[0]
        cv2.line(img_bgr_u8_c960, (x1, y1), (x2, y2), (0, 255, 0), 2)

kernel2 = np.ones((3,3), np.uint8)

dila2_c950 = cv2.dilate(canny_c950, kernel2, iterations=1)
dila2_c960 = cv2.dilate(canny_c960, kernel2, iterations=1)

c950, c960 = st.columns(2)
with c950:
    st.image(img_bgr_u8_c950, channels="BGR", caption="Camera C950")
    st.image(dila2_c950, caption="Dilated C950")

with c960:
    st.image(img_bgr_u8_c960, channels="BGR", caption="Camera C960")
    st.image(dila2_c960, caption="Dilated C960")