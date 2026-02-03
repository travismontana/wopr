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
        relative_path = pt_file.relative_to(RUNS_PATH)

        # Build display string: "grandparent/parent/filename.pt"
        parts = relative_path.parts
        if len(parts) >= 3:
            display_name = f"{parts[-3]}/{parts[-2]}/{parts[-1]}"
        elif len(parts) == 2:
            display_name = f"{parts[-2]}/{parts[-1]}"
        else:
            display_name = str(relative_path)

        # Store mapping: display name -> relative path
        file_options[display_name] = f"/{relative_path}"

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
