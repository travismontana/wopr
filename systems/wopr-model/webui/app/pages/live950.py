import streamlit as st
import math
import requests
from io import BytesIO  # ← ADDED: BytesIO was used but never imported

st.set_page_config(layout="wide")

from ultralytics import YOLO
import cv2
import os
from PIL import Image
import numpy as np
from lib.libtools import where_are_pieces

st.title("WOPR Object Detection")

RUNS_PATH = "/ultralytics/runs"
CLASS_COLORS = {
    "board": (128, 128, 128),
    "ghhhk": (255, 0, 0),
    "houjix": (0, 255, 0),
    "kintan_strider": (0, 0, 255),
    "klorslug": (255, 255, 0),
    "mantellian_savrip": (255, 0, 255),
    "molator": (0, 255, 255),
    "monnok": (255, 128, 0),
    "ngok": (128, 0, 255),
}


@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)


# --- Model Selection ---
pt_files = []
for root, dirs, files in os.walk(RUNS_PATH):
    for file in files:
        if file.endswith(".pt"):
            pt_files.append(os.path.join(root, file))

if len(pt_files) == 0:
    st.warning("No model files found in runs directory.")
    st.stop()

selected_path = st.selectbox("Select model file", options=sorted(pt_files))
st.code(selected_path, language="text")

# --- Load Model ---
model = load_model(selected_path)

# --- Inference Controls ---
conf = st.slider("Confidence", 0.0, 1.0, 0.25)
iou = st.slider("IoU", 0.0, 1.0, 0.45)

cam_options = [
    {"name": "c950", "endpoint": "http://wopr-cam.hangar.bpfx.org:5001/snapshot"},
    {"name": "c960", "endpoint": "http://wopr-cam.hangar.bpfx.org:5000/snapshot"},
    {"name": "rPi", "endpoint": "http://wopr-cam.hangar.bpfx.org:5002/snapshot"},
]

selected_cam = st.selectbox(
    "Select camera", options=cam_options, format_func=lambda cam: cam["name"]
)

image_url = selected_cam["endpoint"]

# ← CHANGED: wrapped in try/except so a dead camera doesn't blow up the UI
try:
    response = requests.get(image_url, timeout=5)
    response.raise_for_status()
    image = Image.open(BytesIO(response.content))
except Exception as e:
    st.error(f"Failed to fetch snapshot from {image_url}: {e}")
    st.stop()

if image:
    st.subheader("YOLO Detection")
    results = model.predict(source=image, conf=conf, iou=iou)  # ← CHANGED: img → image
    annotated = results[0].plot(pil=True)
    st.image(annotated, caption="YOLO Detections")

    detection_count = len(results[0].boxes)
    st.write(f"Detected {detection_count} objects")
