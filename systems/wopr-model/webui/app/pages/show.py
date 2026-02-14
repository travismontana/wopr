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

# Hough Circle (dp=2, minDist=67, minRadius=107, maxRadius=129)
# Hough Circle (dp=3, minDist=318, param1=100, param2=100, minRadius=24, maxRadius=158)

circle1 = cv2.HoughCircles(
    img_gray_u8,
    cv2.HOUGH_GRADIENT,
    dp=3,
    minDist=318,
    param1=100,
    param2=100,
    minRadius=24,
    maxRadius=158,
)

circle2 = cv2.HoughCircles(
    img_gray_u8,
    cv2.HOUGH_GRADIENT,
    dp=2,
    minDist=67,
    param1=100,
    param2=100,
    minRadius=107,
    maxRadius=129,
)

if circle1 is not None:
    circle1 = np.uint16(np.around(circle1))
    for i in circle1[0, :]:
        # draw the outer circle
        cv2.circle(img_rgb_u8, (i[0], i[1]), i[2], (0, 255, 0), 2)
        # draw the center of the circle
        cv2.circle(img_rgb_u8, (i[0], i[1]), 2, (0, 0, 255), 3)
if circle2 is not None:
    circle2 = np.uint16(np.around(circle2))
    for i in circle2[0, :]:
        # draw the outer circle
        cv2.circle(img_rgb_u8, (i[0], i[1]), i[2], (255, 0, 0), 2)
        # draw the center of the circle
        cv2.circle(img_rgb_u8, (i[0], i[1]), 2, (255, 255, 0), 3)

# lines
# canny(100, 200)
# houghlines(rho=1, theta=1*np.pi/180, threshold=100)
rho = 1
theta = np.radians(1)
threshold = 100
gray = cv2.Canny(img_gray_u8, 100, 200, apertureSize=3)
lines = cv2.HoughLines(gray, rho, theta, threshold)
if lines is not None:
    for line in lines:
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        cv2.line(img_rgb_u8, (x1, y1), (x2, y2), (255, 255, 255), 2)

blurred_gray = cv2.medianBlur(img_rgb_u8, 3)
img_edges_gray_u8 = cv2.Canny(blurred_gray, 50, 150)
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_25h9)
detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
corners, ids, rejected = detector.detectMarkers(img_gray_u8)

st.write(f"Found {len(ids) if ids is not None else 0} ArUco markers in the image.")
if ids is not None:
    for corner in corners:
        corner = corner.astype(int)
        cv2.polylines(img_rgb_u8, [corner], True, (0, 255, 255), 2)

# center of the cicles (let's check if both are the same), then we can use that as the center of the board
# can be within 10 pixels of each other, otherwise we might have detected the wrong circles
center_of_board = None
if circle1 is not None and circle2 is not None:
    center1 = (int(circle1[0][0][0]), int(circle1[0][0][1]))
    center2 = (int(circle2[0][0][0]), int(circle2[0][0][1]))
    if center1 == center2 or (
        abs(center1[0] - center2[0]) <= 10 and abs(center1[1] - center2[1]) <= 10
    ):
        center_of_board = center1
        cv2.circle(img_rgb_u8, center_of_board, 5, (255, 255, 255), -1)
        st.write(f"Center of the board: {center_of_board}")
    else:
        st.warning(
            f"Circle centers do not match: {center1} vs {center2}. Cannot determine the center of the board."
        )
else:
    st.warning(
        "Could not detect circles in the image. Cannot determine the center of the board."
    )


st.subheader("Result")
st.image(img_rgb_u8, caption="Processed Image")
