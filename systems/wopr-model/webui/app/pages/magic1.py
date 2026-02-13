import streamlit as st
import numpy as np
import cv2


def find_lines(center, corners, circle_dist, tol=10.0):
    radials = {}

    for corner in corners:
        dx = corner[0] - center[0]
        dy = corner[1] - center[1]
        angle = np.degrees(np.arctan2(dy, dx)) % 360
        dist = np.hypot(dx, dy)
        angle_rounded = round(angle / tol) * tol
        if angle_rounded not in radials:
            radials[angle_rounded] = []
        radials[angle_rounded].append((corner, dist))
    lines = []
    lines = {angle: corners for angle, corners in radials.items() if len(corners) >= 3}
    return lines


st.title("Magic 1, ")
st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed",
)

# need a picture to work with.
# let's ask the user to give us one.
uploaded_file = st.file_uploader(
    "Choose a picture to work with", type=["jpg", "jpeg", "png"]
)

col_gray, col_rgb = st.columns(2)


if uploaded_file is not None:
    raw_bytes = uploaded_file.read()
    raw_buf_u8 = np.frombuffer(raw_bytes, dtype=np.uint8)
    img_bgr_u8 = cv2.imdecode(raw_buf_u8, cv2.IMREAD_COLOR)

    img_gray_u8 = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2GRAY)
    img_rgb_u8 = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2RGB)
    img_medBlur_gray_u8 = cv2.medianBlur(img_gray_u8, 9)
    img_medBlur_rgb_u8 = cv2.medianBlur(img_rgb_u8, 9)

    with col_gray:
        st.header("Gray")
        st.image(img_medBlur_gray_u8, caption="Median Blur 9")

    with col_rgb:
        st.header("RGB")
        st.image(img_medBlur_rgb_u8, caption="Median Blur 9")
