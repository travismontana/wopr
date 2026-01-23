import os

import streamlit as st

if "debug" not in st.session_state:
    st.session_state["debug"] = False

st.set_page_config(
    page_title="WOPR Back of House", 
    page_icon=":house:",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("WOPR Back of House")
placeholder = st.empty()

with placeholder.container():
    st.markdown("System Loading...")

placeholder.empty()

with st.sidebar:
    with st.expander("Settings"):
        # Debug toggle
        debug_toggle = st.toggle("Activate debugging", value=st.session_state.debug)
        st.session_state.debug = debug_toggle
        debug = st.session_state.debug
        # Cache control
        if st.button("Clear Cache"):
            st.cache_data.clear()

dashboard = st.Page(
    "displays/dashboard.py",
    title="Dashboard",
    icon=":material/dashboard:",
    default=True,
)

pg = st.navigation([dashboard])
pg.run()
