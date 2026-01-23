import os

import streamlit as st

from lib.helpers import debugit
from lib.wopr_api_client import Client
from lib.wopr_api_client.models.model_create import ModelCreate
from lib.wopr_api_client.api.models import get_all_items_api_v2_models_get
from lib.wopr_api_client.types import Response


def status_display():
    st.header("Status")
    if st.button("Refresh"):
        st.rerun()

    with st.spinner("Spinning the spinner..."):
        if "api_host" not in st.session_state:
            api_host = os.getenv("API_URL", "")
            if not api_host:
                st.error("API_URL environment variable is not set.")
            st.session_state["api_host"] = api_host

        woprclient = Client(base_url=st.session_state["api_host"])

        models: Response[ModelCreate] = get_all_items_api_v2_models_get.sync(
            client=woprclient
        )

        if "models" not in st.session_state:
            st.session_state["models"] = models

        debugit("Startup completed", st.session_state)

    models = st.session_state["models"]

    for model_in in models:
        model = model_in.to_dict()

        if model["model_status"] is None:
            model["active"] = False
            model["version"] = {
                "current_version": 0,
                "note": "New model, no setup done",
                "wopr_version": "0.0.0",
                "previous_versions": [],
            }
            model["operations"] = {
                "task": "created entry",
                "data": {},
                "note": "Initial setup",
                "extradata": {},
                "status": "",
            }
            model["model_status"] = {
                "backup": {},
                "checksum": 0,
                "has_distfile": False,
                "filename": "",
                "active": False,
            }
            return 0
