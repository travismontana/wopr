import streamlit as st
import httpx
import os 
import requests

st.title("WOPR ML Config System")
st.write("Welcome to the WOPR ML Config System.")

# 
# Load WOPR Config from WOPR-API, then display it.
#
API_BASE = "https://api.wopr.tailandtraillabs.org"

def fetch_config():
    response = httpx.get(f"{API_BASE}/api/v2/config/all")
    response.raise_for_status()
    return response.json()


config = fetch_config()

st.header("Current WOPR Configuration")
st.json(config)