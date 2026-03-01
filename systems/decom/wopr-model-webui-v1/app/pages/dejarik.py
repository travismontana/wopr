import os

import streamlit as st
from ultralytics import YOLO

from lib.libtools import (
    WEIGHTS,
    get_models,
    get_projects,
    export_annotations,
)


st.title("Dejarik: YOLOv8 Object Detection")
model = None
# which model?
MODEL_LIST = get_models()
model_name = st.selectbox("Select a model", MODEL_LIST)
model = YOLO(os.path.join(WEIGHTS, model_name))


PROJECT_LIST = list(get_projects())
# I need PROJECT_LIST["results"][X]["id"] and ["title"] to get the project ID, and I want to display the project name in the dropdown
projects = {proj.id: proj.title for proj in get_projects()}
project_id = None
project_id = st.selectbox("Select a Label Studio project", projects.keys(), format_func=lambda x: projects[x])

if model is not None:
    st.success(f"Selected model: {model_name}")
if project_id is not None:
    st.success(f"Selected project ID: {project_id}")

if model is not None and project_id is not None:
    # Export
    st.info("Exporting annotations from Label Studio...")
    export_result = st.button("Export annotations")
    if export_result:
        st.write("Exporting...")
        result = export_annotations(project_id)
        st.write(f"Export result: {result}")
