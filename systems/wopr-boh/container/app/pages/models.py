import streamlit as st

from displays.ml_models_editor import render_models_editor
from displays.ml_models_status import render_models_status
from displays.ml_model_controls import render_models_controls

from lib.helpers import render_sidebar

render_sidebar()

# Models editor section
st.subheader("Models")
_results = render_models_editor()

st.subheader("Model Status")
_results = render_models_status()

st.subheader("Model Controls")
_results = render_models_controls()
