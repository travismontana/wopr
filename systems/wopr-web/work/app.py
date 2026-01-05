import streamlit as st

st.title("WOPR Back of House")
st.write("If you can read this, Streamlit is working.")

# This is the key difference from Flask/FastAPI:
# Every interaction re-runs the entire script top-to-bottom
if st.button("Click me"):
    st.write("Button was clicked!")