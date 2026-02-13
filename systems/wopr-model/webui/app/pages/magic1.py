import streamlit as st
import numpy as np
import cv2 as cv

st.title("Magic 1, ")

# need a picture to work with.
# let's ask the user to give us one.
uploaded_file = st.file_uploader(
    "Choose a picture to work with", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    file_bytes = np.frombuffer(uploaded_file.read(), dtype=np.uint8)
    img = cv.imdecode(file_bytes, cv.IMREAD_GRAYSCALE)
    img_reg = cv.imdecode(file_bytes, cv.IMREAD_COLOR)
    img = cv.medianBlur(img, 5)
    cimg = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    circles = cv.HoughCircles(
        img, cv.HOUGH_GRADIENT, 1, 50, param1=50, param2=30, minRadius=100, maxRadius=0
    )
    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        cv.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
        cv.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)
    st.image(cimg, caption="Processed Image with Detected Circles")

    dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_25h9)
    detectorParams = cv.aruco.DetectorParameters()
    detector = cv.aruco.ArucoDetector(dictionary, detectorParams)
    marker_corners, marker_ids, rejected_candidates = detector.detectMarkers(img_reg)
    st.write(f"Found Aruco Markers: {len(marker_ids) if marker_ids is not None else 0}")
    if marker_ids is not None:
        for corners, marker_id in zip(marker_corners, marker_ids):
            st.write(f"Marker ID: {marker_id[0]}, Corners: {corners[0]}")

    canny_color = cv.Canny(img, 100, 200)
    st.image(canny_color, caption="Canny Edge Detection")

    chess_ret, chess_corners = cv.findChessboardCorners(img, (6, 6), None)

    chess_corners2 = cv.cornerSubPix(img, chess_corners, (11, 11), (-1, -1), criteria)
    img_chess = cv.drawChessboardCorners(
        img_reg.copy(), (6, 6), chess_corners2, chess_ret
    )
    st.image(img_chess, caption="Chessboard Corners Detected")
