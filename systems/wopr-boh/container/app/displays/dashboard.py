import streamlit as st

from displays.status import status_display

from lib.models import activate_model

st.header("Dashboard")

DEBUG = st.session_state["debug"]


def dbitj(message, json):
    if DEBUG:
        st.write(message)
        st.json(json, expanded=False)


with st.expander("Model Status"):
    status_display()

models = st.session_state["models"]
for model_in in models:
    model = model_in.to_dict()
    dbitj("Model data", model)

    if "active" in model:
        data_column, status_column, action_column = st.columns(3)
        with data_column:
            st.write(model["name"])
            st.caption(model["description"])

        with status_column:
            swhat_col, sval_col = st.columns(2)
            with swhat_col:
                st.write("Is active:")
                st.write("Has backups:")
                st.write("Has checksum:")
                st.write("Has distfile:")

            with sval_col:
                if model["active"] or model["active"] is not None:
                    st.badge("Active", color="green")

                if "backup" in model["model_status"]:
                    if model["model_status"]["backup"] is not None:
                        st.badge("Yes", color="green")
                else:
                    st.badge("No", color="red")

                if "checksum" in model["model_status"]:
                    if model["model_status"]["checksum"] is not None:
                        st.write(model["model_status"]["checksum"])
                else:
                    st.badge("No checksum", color="red")

                if "distfile" in model["model_status"]:
                    if model["model_status"]["distfile"]:
                        st.badge("Yes", color="green")
                    else:
                        st.badge("No", color="red")
                else:
                    st.badge("Inactive", color="red")
    else:
        st.write(f"Model {model['name']} is not active")
        if st.button("Activate"):
            st.write("Yes")
            results = activate_model(model)
