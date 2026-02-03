import streamlit as st
from ultralytics import YOLO
import cv2
import os
from PIL import Image
import tempfile

st.title("WOPR Object Detection")
st.set_page_config(layout="wide")

RUNS_PATH = "/ultralytics/runs"

# Model selection (with caching)
@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)


# Session state for model path
if "model_path" not in st.session_state:
    st.session_state.model_path = None

# Model selection section
if st.session_state.model_path is None:
    pt_files = []
    for root, dirs, files in os.walk(RUNS_PATH):
        for file in files:
            if file.endswith(".pt"):
                pt_files.append(os.path.join(root, file))

    if len(pt_files) == 0:
        st.warning("No model files found in runs directory.")
    else:
        selected_path = st.selectbox("Select model file", options=sorted(pt_files))
        st.code(selected_path, language="text")
    if st.button("Select Model"):
        st.session_state.model_path = selected_path
        st.rerun()
else:
    # Model loaded - show inference controls
    model = load_model(st.session_state.model_path)

    # Confidence/IoU sliders
    conf = st.slider("Confidence", 0.0, 1.0, 0.25)
    iou = st.slider("IoU", 0.0, 1.0, 0.45)

    # Source selection
    source_type = st.radio("Source", ["Image Upload", "Video Upload", "Webcam"])

    if source_type == "Image Upload":
        uploaded = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        if uploaded:
            img = Image.open(uploaded)

            # Run detection
            results = model.predict(source=img, conf=conf, iou=iou)

            # Display annotated image
            annotated = results[0].plot()
            st.image(annotated, caption="Detections")

            # Show detection details
            st.write(f"Detected {len(results[0].boxes)} objects")
            for box in results[0].boxes:
                cls = model.names[int(box.cls[0])]
                conf_score = float(box.conf[0])
                st.write(f"- {cls}: {conf_score:.2f}")

    # Change model button
    if st.button("Change Model"):
        st.session_state.model_path = None
        st.rerun()
