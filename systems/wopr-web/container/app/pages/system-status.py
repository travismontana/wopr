# Copyright 2026 Bob Bomar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import httpx
import os 
import requests


st.set_page_config(layout="wide")
st.title("WOPR ML Systems Status")
st.write("Welcome to the WOPR ML Systems Status.")

API_BASE = "https://api.wopr.tailandtraillabs.org"

# https://github.com/travismontana/wopr/actions/workflows/build-wopr-api.yaml/badge.svg
# https://github.com/travismontana/wopr/actions/workflows/build-wopr-api.yaml
# ---- dummy data ----
things = [
    "example-service",
    "build-wopr-api",
]

def check_up(name):
    if name == "build-wopr-api":
        return f"https://github.com/{GITHUB_REPO}/actions/workflows/{name}.yaml/badge.svg"
    else: 
        return "...."   # TODO: replace

def check_func(name):
    if name == "build-wopr-api":
        try:
            url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/.github/workflows/{name}.yaml"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.text
            return f"Failed to fetch: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    else:
        return "...."   # TODO: replace

def render_row(name):
    col_thing, col_up, col_func, col_time, col_action = st.columns(
        [3, 1, 1, 2, 1]
    )

    with col_thing:
        st.text(name)

    with col_up:
        badge_url = check_up(name)
        st.markdown(f'<img src="{badge_url}" alt="status">', unsafe_allow_html=True)

    with col_func:
        with st.expander("YAML"):
            yaml_content = check_func(name)
            st.code(yaml_content, language="yaml")

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
