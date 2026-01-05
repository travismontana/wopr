import streamlit as st
import httpx
import os 
import requests

st.title("WOPR ML Image Capture System")
st.write("Welcome to the WOPR ML Image Capture System.")

API_BASE = "https://api.wopr.tailandtraillabs.org"