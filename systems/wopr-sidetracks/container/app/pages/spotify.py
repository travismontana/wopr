import streamlit as st
import httpx
import os 
import requests
import pandas as pd
import re

# Get the token from the env var SPOTIFY_API_TOKEN
SPOTIFY_API_TOKEN = os.getenv("SPOTIFY_API_TOKEN")
if not SPOTIFY_API_TOKEN:
    raise ValueError("SPOTIFY_API_TOKEN environment variable is not set")
else: 
    logger.info("Got SPOTIFY_API_TOKEN")

LINE_RE = re.compile(
    r"""^\s*
        (?:\d+\)\s*)?              # optional "1) "
        (?P<artist>.+?)\s*         # artist
        [–—-]\s*                   # dash (en/em/hyphen)
        (?P<title>.+?)\s*          # title
        $""",
    re.VERBOSE,
)

def parse_tracklist(text: str):
    rows = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        m = LINE_RE.match(line)
        if m:
            rows.append({"artist": m.group("artist").strip(),
                         "title": m.group("title").strip()})
        else:
            rows.append({"artist": "", "title": line})
    return rows


# ---
# Spotify stuff
# ---

st.title("Spotify Actions")
st.write("Welcome to the Spotify Actions page.")

st.divider()

text = st.text_area("Paste your list here", height=260)

if text:
    rows = parse_tracklist(text)
    df = pd.DataFrame(rows)
    edited_df = st.data_editor(
        df, 
        width="stretch",
        num_rows="dynamic",
        )
    st.write("Edited data:")
    st.dataframe(edited_df)
    st.download_button(
        "Download CSV",
        edited_df.to_csv(index=False).encode("utf-8"),
        file_name="tracklist.csv",
        mime="text/csv",
    )
