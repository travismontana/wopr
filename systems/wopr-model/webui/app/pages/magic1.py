import streamlit as st
import numpy as np
import cv2 as cv


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

# need a picture to work with.
# let's ask the user to give us one.
uploaded_file = st.file_uploader(
    "Choose a picture to work with", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    file_bytes = np.frombuffer(uploaded_file.read(), dtype=np.uint8)
    orig_img = cv.imdecode(file_bytes, cv.IMREAD_GRAYSCALE)
    img_reg = cv.imdecode(file_bytes, cv.IMREAD_COLOR)
    img = cv.medianBlur(orig_img, 9)

    # Circle detection
    circles = cv.HoughCircles(
        img, cv.HOUGH_GRADIENT, 1, 50, param1=50, param2=30, minRadius=100, maxRadius=0
    )
    circles = np.uint16(np.around(circles))

    if len(circles[0, :]) != 1:
        st.error(f"Expected 1 circle, found {len(circles[0, :])}")
        st.stop()

    x, y, radius = circles[0][0]
    center = (x, y)

    # Show circle detection
    vis_circles = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
    cv.circle(vis_circles, center, radius, (0, 255, 0), 2)
    cv.circle(vis_circles, center, 2, (0, 0, 255), 3)
    st.image(vis_circles, caption="Detected Circle")

    # ArUco detection
    dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_APRILTAG_25h9)
    detector = cv.aruco.ArucoDetector(dictionary, cv.aruco.DetectorParameters())
    marker_corners, marker_ids, _ = detector.detectMarkers(img_reg)
    st.write(f"ArUco Markers: {len(marker_ids) if marker_ids is not None else 0}")

    # Edge detection
    otsu_ret, otsu_binary = cv.threshold(img, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    canny = cv.Canny(img, 100, 200)
    st.image(canny, caption="Canny Edges")

    # Corner detection
    corners = cv.goodFeaturesToTrack(canny, 100, 0.01, 10)
    corners = np.uint16(np.around(corners)).reshape(-1, 2)

    # Filter to circle interior
    filtered_corners = []
    for corner in corners:
        dist = np.hypot(corner[0] - center[0], corner[1] - center[1])
        if dist < radius * 0.95:
            filtered_corners.append(corner)
    filtered_corners = np.array(filtered_corners)

    # Find radial lines
    lines = find_lines(center, filtered_corners, radius)
    st.write(f"Found {len(lines)} radial boundaries")

    # FRESH IMAGE for final visualization - no stacking
    final_vis = cv.cvtColor(orig_img, cv.COLOR_GRAY2BGR)
    cv.circle(final_vis, center, radius, (0, 255, 0), 1)  # Faint circle

    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
        (128, 128, 0),
        (128, 0, 128),
    ]

    for idx, (angle, corner_list) in enumerate(lines.items()):
        color = colors[idx % len(colors)]

        for corner, dist in corner_list:
            cv.circle(final_vis, tuple(corner), 5, color, -1)

        if corner_list:
            farthest = max(corner_list, key=lambda x: x[1])[0]
            cv.line(final_vis, center, tuple(farthest), color, 2)

    st.image(final_vis, caption="Detected Radial Boundaries")
