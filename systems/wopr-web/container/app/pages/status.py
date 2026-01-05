import streamlit as st
import httpx
import os 
import requests


st.set_page_config(layout="wide")
st.title("WOPR ML Systems Status")
st.write("Welcome to the WOPR ML Systems Status.")

API_BASE = "https://api.wopr.tailandtraillabs.org"


# ---- dummy data ----
things = [
    "example-service",
]

def check_up(name):
    return "...."   # TODO: replace

def check_func(name):
    return "...."   # TODO: replace

def render_row(name):
    col_thing, col_up, col_func, col_time, col_action = st.columns(
        [3, 1, 1, 2, 1]
    )

    with col_thing:
        st.text(name)

    with col_up:
        st.text(f"[ {check_up(name)} ]")

    with col_func:
        st.text(f"[ {check_func(name)} ]")

    with col_time:
        st.text("----")

    with col_action:
        if st.button("REFRESH", key=f"refresh_{name}"):
            pass  # hook per-thing refresh here


# ---- header row ----
h1, h2, h3, h4, h5 = st.columns([3, 1, 1, 2, 1])
h1.text("Thing")
h2.text("UP")
h3.text("FUNC")
h4.text("LAST CHECK")
h5.text("ACTION")

st.divider()

# ---- rows ----
for thing in things:
    render_row(thing)
