import streamlit as st
import glob, os
import ultralytics as ua
from ultralytics import solutions

st.set_page_config(layout="wide", page_title="WOPR Model Interface")
st.title("WOPR Models")

WEIGHTS_PATH = "/ultralytics/weights"
RUNS_PATH = "/ultralytics/runs"
DATASETS_PATH = "/ultralytics/datasets"
YOLO_EXPORTS_PATH = "/ultralytics/yolo_exports"

# Find all .pt files recursively
# os.chdir(RUNS_PATH)
pt_files = []
for root, dirs, files in os.walk(RUNS_PATH):
    for file in files:
        if file.endswith(".pt"):
            full_path = os.path.join(root, file)
            pt_files.append(full_path)
if len(pt_files) == 0:
    st.warning("No model files found in runs directory.")

else:
    # Build display names with parent/grandparent context
    file_options = {}
    for pt_file in sorted(pt_files):
        file_options[pt_file] = pt_file
    # Selectbox with descriptive names
    selected_display = st.selectbox(
        "Select model file", options=sorted(file_options.keys())
    )

    # Get the actual relative path
    selected_path = file_options[selected_display]

    st.code(selected_path, language="text")

    # Store in session state or variable
    if st.button("Select this model"):
        st.session_state["selected_model_path"] = selected_path
        st.success(f"Selected: {selected_path}")

if st.session_state.get("selected_model_path"):
    model_path = st.session_state["selected_model_path"]
    st.write(f"Loading model from: {model_path}")

    # Load the model
    model = ua.YOLO(model_path)

    st.success("Model loaded successfully!")

    # Display model info
    st.subheader("Model Information")
    st.json(model, expanded=False)

    # Example inference on a sample image
    st.subheader("Example Inference")
    sample_image = ua.data.load_image(
        "https://images.wopr.tailandtraillabs.org/ml/incoming/game-e5c50e50-37a1-4c43-82dc-5a2fbb7f2866-round1-bpfx-play1.jpg"
    )
    results = model(sample_image)

    # Display results
    st.image(results.render()[0], caption="Inference Result", use_column_width=True)
