import streamlit as st
import httpx
import random
import re
import logging
import sys
from datetime import datetime
from pathlib import Path
from global import *

st.title("10 Round Human vs 2 Bot Predefined Game")
# Load predefined game data
total_rounds = 10

