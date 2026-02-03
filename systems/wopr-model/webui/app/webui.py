import streamlit as st
import glob, os
from ultralytics import YOLO, solutions

st.set_page_config(layout="wide", page_title="WOPR Model Interface")
st.title("WOPR Models")

RUNS_PATH = "/ultralytics/runs"

# Initialize session state
if "selected_model_path" not in st.session_state:
    st.session_state["selected_model_path"] = None

# MODEL SELECTION SECTION - only show if no model selected
if st.session_state["selected_model_path"] is None:
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

        if st.button("Select this model"):
            st.session_state["selected_model_path"] = selected_path
            st.rerun()  # Force immediate rerun to show inference UI

# INFERENCE SECTION - only show if model selected
else:
    model_path = st.session_state["selected_model_path"]

    # Show what's loaded with option to change
    col1, col2 = st.columns([4, 1])
    with col1:
        st.info(f"Model: {model_path}")
    with col2:
        if st.button("Change Model"):
            st.session_state["selected_model_path"] = None
            st.rerun()

    # Load model (cache it so it doesn't reload on every interaction)
    @st.cache_resource
    def load_model(path):
        return YOLO(path)

    model = load_model(model_path)

    # NOW do inference UI here
    st.subheader("Inference Configuration")

    source = st.selectbox("Source", ["webcam", "image", "video"])
    conf_threshold = st.slider("Confidence", 0.0, 1.0, 0.25)
    iou_threshold = st.slider("IoU", 0.0, 1.0, 0.45)

    inf = solutions.Inference(
        model=model_path, source=source, conf=conf_threshold, iou=iou_threshold
    )
    inf.inference()
