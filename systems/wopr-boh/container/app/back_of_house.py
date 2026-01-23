import streamlit as st

from wopr.logging import setup_logging

from lib.wopr_api_client.api.models import (
    get_all_items_api_v2_models_get,
)


logger = setup_logging("wopr-boh", log_file="/var/log/wopr-boh.log")

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

with st.spinner("Spinning the spinner..."):
    models = get_all_items_api_v2_models_get()
    if "models" not in st.session_state:
        st.session_state["models"] = models

    if "debug" not in st.session_state:
        st.session_state["debug"] = False

placeholder.empty()

dashboard = st.Page(
    "displays/dashboard.py", title="Dashboard", icon=":material:dashboard", default=True
)
