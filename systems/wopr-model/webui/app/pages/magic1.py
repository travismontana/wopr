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

if uploaded_file is not None:
    raw_bytes = uploaded_file.read()
    raw_buf_u8 = np.frombuffer(raw_bytes, dtype=np.uint8)
    img_bgr_u8 = cv2.imdecode(raw_buf_u8, cv2.IMREAD_COLOR)

    img_gray_u8 = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2GRAY)
    img_rgb_u8 = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2RGB)

with st.expander("Blurs", expanded=False):
    col_gray, col_rgb = st.columns(2)
    with col_gray:
        st.header("Gray")
        col_gray_medBlur, col_gray_gauBlur = st.columns(2)

        # Median Blue - Gray
        imgu8_mbk = st.slider(
            "Median Blur Kernel Size",
            min_value=1,
            max_value=31,
            value=9,
            step=2,
            key="gray_mbk",
        )
        img_medBlur_gray_u8 = cv2.medianBlur(img_gray_u8, imgu8_mbk)
        st.image(img_medBlur_gray_u8, caption=f"Median Blur {imgu8_mbk}")

        # Gaussian Blur - Gray
        imgu8_gbk = st.slider(
            "Gaussian Blur Kernel Size",
            min_value=1,
            max_value=31,
            value=9,
            step=2,
            key="gray_gbk",
        )
        img_gauBlur_gray_u8 = cv2.GaussianBlur(img_gray_u8, (imgu8_gbk, imgu8_gbk), 0)
        st.image(img_gauBlur_gray_u8, caption=f"Gaussian Blur {imgu8_gbk}")

        # bilateralFilter - Gray
        imgu8_bf_d = st.slider(
            "Bilateral Filter Diameter",
            min_value=1,
            max_value=31,
            value=9,
            step=2,
            key="gray_bf_d",
        )
        imgu8_bf_sigmaColor = st.slider(
            "Bilateral Filter Sigma Color",
            min_value=1,
            max_value=255,
            value=75,
            step=1,
            key="gray_bf_sc",
        )
        imgu8_bf_sigmaSpace = st.slider(
            "Bilateral Filter Sigma Space",
            min_value=1,
            max_value=255,
            value=75,
            step=1,
            key="gray_bf_ss",
        )
        img_bilateralFilter_gray_u8 = cv2.bilateralFilter(
            img_gray_u8,
            imgu8_bf_d,
            imgu8_bf_sigmaColor,
            imgu8_bf_sigmaSpace,
        )
        st.image(
            img_bilateralFilter_gray_u8,
            caption=f"Bilateral Filter d={imgu8_bf_d} sc={imgu8_bf_sigmaColor} ss={imgu8_bf_sigmaSpace}",
        )

    with col_rgb:
        st.header("RGB")

        # Median Blur - RGB
        imrgb_mbk = st.slider(
            "Median Blur Kernel Size",
            min_value=1,
            max_value=31,
            value=9,
            step=2,
            key="rgb_mbk",
        )
        img_medBlur_rgb_u8 = cv2.medianBlur(img_rgb_u8, imrgb_mbk)
        st.image(img_medBlur_rgb_u8, caption=f"Median Blur {imrgb_mbk}")

        # Gaussian Blur - RGB
        imrgb_gbk = st.slider(
            "Gaussian Blur Kernel Size",
            min_value=1,
            max_value=31,
            value=9,
            step=2,
            key="rgb_gbk",
        )
        img_gauBlur_rgb_u8 = cv2.GaussianBlur(img_rgb_u8, (imrgb_gbk, imrgb_gbk), 0)
        st.image(img_gauBlur_rgb_u8, caption=f"Gaussian Blur {imrgb_gbk}")

        # bilateralFilter - RGB
        imrgb_bf_d = st.slider(
            "Bilateral Filter Diameter",
            min_value=1,
            max_value=31,
            value=9,
            step=2,
            key="rgb_bf_d",
        )
        imrgb_bf_sigmaColor = st.slider(
            "Bilateral Filter Sigma Color",
            min_value=1,
            max_value=255,
            value=75,
            step=1,
            key="rgb_bf_sc",
        )
        imrgb_bf_sigmaSpace = st.slider(
            "Bilateral Filter Sigma Space",
            min_value=1,
            max_value=255,
            value=75,
            step=1,
            key="rgb_bf_ss",
        )
        img_bilateralFilter_rgb_u8 = cv2.bilateralFilter(
            img_rgb_u8,
            imrgb_bf_d,
            imrgb_bf_sigmaColor,
            imrgb_bf_sigmaSpace,
        )
        st.image(
            img_bilateralFilter_rgb_u8,
            caption=f"Bilateral Filter d={imrgb_bf_d} sc={imrgb_bf_sigmaColor} ss={imrgb_bf_sigmaSpace}",
        )
