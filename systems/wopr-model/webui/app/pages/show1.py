import streamlit as st
import numpy as np
import cv2

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.title("CV Pipeline")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_file is None:
    st.info("Upload an image to get started.")
    st.stop()

# Decode uploaded image
raw_bytes = uploaded_file.read()
raw_buf_u8 = np.frombuffer(raw_bytes, dtype=np.uint8)
img_bgr_u8 = cv2.imdecode(raw_buf_u8, cv2.IMREAD_COLOR)
img_gray_u8 = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2GRAY)
img_rgb_u8 = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2RGB)

# Find the marker first.

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_25h9)
detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
corners, ids, rejected = detector.detectMarkers(img_gray_u8)

st.write(f"Found {len(ids) if ids is not None else 0} ArUco markers in the image.")
if ids is not None:
    for corner in corners:
        corner = corner.astype(int)
        cv2.polylines(img_rgb_u8, [corner], True, (0, 255, 255), 2)

marker_center = None
marker_center = np.mean(corners[0][0], axis=0)

# Median blur and Canny edge detection
blurred_gray = cv2.medianBlur(img_rgb_u8, 5)
img_edges_gray_u8 = cv2.Canny(blurred_gray, 10, 50)
# Circle detection
circle1 = cv2.HoughCircles(
    img_edges_gray_u8,
    cv2.HOUGH_GRADIENT,
    dp=1.2,
    minDist=400,
    param1=80,
    param2=70,
    minRadius=220,
    maxRadius=270,
)


if circle1 is not None:
    circle1 = np.uint16(np.around(circle1))
    for i in circle1[0, :]:
        # draw the outer circle
        cv2.circle(img_rgb_u8, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # draw the center of the circle
        cv2.circle(img_rgb_u8, (i[0], i[1]), 2, (0, 0, 255), 3)

st.image(img_rgb_u8)
