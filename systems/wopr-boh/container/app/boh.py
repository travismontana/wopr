import streamlit as st

st.set_page_config(layout="wide")

# OpenCV parameter fiddling
# Camera Adjuments <---
# Train models
# Control Models
# Logical Systems Controls <---

pages = {
    "Logical Systems Controls": [
        st.Page("cognition_oversight.py", title="Congnition Oversight")
    ],
    "Reality Controls": [
        st.Page("perception_oversight.py", title="Persception Oversight")
    ],
}
pg = st.navigation(pages)
pg.run()
