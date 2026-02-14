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

marker_center = corners[0][0].mean(axis=0).astype(int)
dx = int(marker_center[0]) - center_of_board[0]
dy = int(marker_center[1]) - center_of_board[1]
marker_angle = np.degrees(np.arctan2(dy, dx)) % 360

# Compute angle difference for every line, sort, take closest 2
line_angles = []
for line in lines:
    rho_val, theta_val = line[0]
    line_angle1 = (np.degrees(theta_val) + 90) % 360
    line_angle2 = (np.degrees(theta_val) - 90) % 360

    diff1 = min(abs(line_angle1 - marker_angle), 360 - abs(line_angle1 - marker_angle))
    diff2 = min(abs(line_angle2 - marker_angle), 360 - abs(line_angle2 - marker_angle))
    best_diff = min(diff1, diff2)
    best_angle = line_angle1 if diff1 < diff2 else line_angle2

    line_angles.append((best_diff, best_angle, rho_val, theta_val))

line_angles.sort(key=lambda x: x[0])

# Take top 2 — but they might be duplicates of the same spoke.
# Deduplicate: skip lines within 5° of one already picked.
cell0_lines = []
for diff, angle, rho_val, theta_val in line_angles:
    if len(cell0_lines) >= 2:
        break
    if any(min(abs(angle - a), 360 - abs(angle - a)) < 5 for _, a, _, _ in cell0_lines):
        continue
    cell0_lines.append((diff, angle, rho_val, theta_val))
    st.write(
        f"Cell 0 boundary: {angle:.1f}° ({diff:.1f}° from marker at {marker_angle:.1f}°)"
    )

# add those lines to the image
for _, _, rho_val, theta_val in cell0_lines:
    a = np.cos(theta_val)
    b = np.sin(theta_val)
    x0 = a * rho_val
    y0 = b * rho_val
    x1 = int(x0 + 1000 * (-b))
    y1 = int(y0 + 1000 * (a))
    x2 = int(x0 - 1000 * (-b))
    y2 = int(y0 - 1000 * (a))
    cv2.line(img_rgb_u8, (x1, y1), (x2, y2), (255, 0, 255), 2)

st.subheader("Result")
st.image(img_rgb_u8, caption="Processed Image")
