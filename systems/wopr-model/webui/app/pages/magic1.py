import streamlit as st
import numpy as np
import cv2 as cv


def find_cells(center, corners, circle_dist, tol=2.0):
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
    cells = []
    for angle, points in radials.items():
        if len(points) >= 2 and all(p[1] < 2 * circle_dist for p in points):
            points = sorted(points, key=lambda p: p[1])  # Sort by distance
            cells.append([p[0] for p in points[:2]])
    return cells


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
    num_circles = len(circles[0, :]) if circles is not None else 0
    if num_circles == 0 or num_circles > 1:
        st.write(f"Found more or less than 1 circle: {num_circles}")
        raise ValueError("Expected exactly one circle in the image.")
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

    corners = cv.goodFeaturesToTrack(canny_color, 100, 0.01, 10)
    corners = np.uint16(np.around(corners))
    reshaped_corners = corners.reshape(-1, 2)
    for corner in corners:
        x, y = corner.ravel()
        cv.circle(cimg, (x, y), 3, (255, 0, 0), -1)
    st.image(cimg, caption="Good Features to Track")

    gray = np.float32(img)
    corner_harris = cv.cornerHarris(gray, 5, 7, 0.06)
    corner_harris = cv.dilate(corner_harris, None)
    cimg[corner_harris > 0.01 * corner_harris.max()] = [0, 0, 255]
    st.image(cimg, caption="Harris Corner Detection")

    x, y, radius = circles[0][0]  # Unpack first circle
    center = (x, y)
    filtered_corners = []
    for corner in reshaped_corners:
        dist = np.hypot(corner[0] - center[0], corner[1] - center[1])
        if dist < radius * 0.95:  # Inside circle, with small margin
            filtered_corners.append(corner)
    filtered_corners = np.array(filtered_corners)
    cells = find_cells(center, filtered_corners, circles[0][0][2])

    st.write(f"Found {len(cells)} cells around the circle.")
    for cell in cells:
        cv.line(cimg, center, tuple(cell[0]), (255, 255, 0), 2)
        cv.line(cimg, center, tuple(cell[1]), (255, 255, 0), 2)
    st.image(cimg, caption="Cells Connected to Circle Center")
