import streamlit as st
import math

st.set_page_config(layout="wide")  # MUST be first Streamlit call

from ultralytics import YOLO
import cv2
import os
from PIL import Image
import numpy as np
from lib.libtools import where_are_pieces

st.title("WOPR Object Detection")

RUNS_PATH = "/ultralytics/runs"
CLASS_COLORS = {
    "board": (128, 128, 128),  # gray
    "ghhhk": (255, 0, 0),  # red
    "houjix": (0, 255, 0),  # green
    "kintan_strider": (0, 0, 255),  # blue
    "klorslug": (255, 255, 0),  # yellow
    "mantellian_savrip": (255, 0, 255),  # magenta
    "molator": (0, 255, 255),  # cyan
    "monnok": (255, 128, 0),  # orange
    "ngok": (128, 0, 255),  # purple
}

@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)


# --- Model Selection ---
pt_files = []
for root, dirs, files in os.walk(RUNS_PATH):
    for file in files:
        if file.endswith(".pt"):
            pt_files.append(os.path.join(root, file))

if len(pt_files) == 0:
    st.warning("No model files found in runs directory.")
    st.stop()

selected_path = st.selectbox("Select model file", options=sorted(pt_files))
st.code(selected_path, language="text")

# --- Load Model ---
model = load_model(selected_path)

# --- Inference Controls ---
conf = st.slider("Confidence", 0.0, 1.0, 0.25)
iou = st.slider("IoU", 0.0, 1.0, 0.45)

# --- Image Upload ---
uploaded = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded:
    # Read raw bytes first, before anything consumes the buffer
    raw_bytes = uploaded.read()
    uploaded.seek(0)  # rewind for PIL

    img = Image.open(uploaded)

    # === YOLO Detection ===
    st.subheader("YOLO Detection")
    results = model.predict(source=img, conf=conf, iou=iou)
    annotated = results[0].plot(pil=True)
    st.image(annotated, caption="YOLO Detections")

    detection_count = len(results[0].boxes)
    st.write(f"Detected {detection_count} objects")
    pieces_list = []
    board_coor = None
    board_rho = None
    board_theta_rad = None
    for box in results[0].boxes:
        cls_name = model.names[int(box.cls[0])]
        if cls_name == "board":
            board_coor = box.xyxy[0].int().tolist()
            board_center = [
                (board_coor[0] + board_coor[2]) // 2,
                (board_coor[1] + board_coor[3]) // 2,
            ]
            board_rho = math.isqrt(board_center[0] ** 2 + board_center[1] ** 2)
            board_theta_rad = math.atan2(board_center[1], board_center[0])
        conf_score = float(box.conf[0])
        coordinates = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
        st.write(f"- {cls_name}: {conf_score:.2f}, Coordinates: {coordinates}")
        x1, y1, x2, y2 = box.xyxy[0].int().tolist()
        polar1_rho = math.isqrt(x1**2 + y1**2)
        polar1_theta_deg = math.degrees(math.atan2(y1, x1))
        polar1_theta_rad = math.radians(polar1_theta_deg)
        polar2_rho = math.isqrt(x2**2 + y2**2)
        polar2_theta_deg = math.degrees(math.atan2(y2, x2))
        polar2_theta_rad = math.radians(polar2_theta_deg)
        pieces_list.append(
            {
                "class": cls_name,
                "confidence": conf_score,
                "coordinates": coordinates,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "polar1": {
                    "rho": polar1_rho,
                    "theta_deg": polar1_theta_deg,
                    "theta_rad": polar1_theta_rad,
                },
                "polar2": {
                    "rho": polar2_rho,
                    "theta_deg": polar2_theta_deg,
                    "theta_rad": polar2_theta_rad,
                },
            }
        )

    # === AprilTag + Hough Circle Detection ===
    st.subheader("Board Detection (AprilTag + Hough)")

    raw_buf_u8 = np.frombuffer(raw_bytes, dtype=np.uint8)
    img_bgr_u8 = cv2.imdecode(raw_buf_u8, cv2.IMREAD_COLOR)
    img_gray_u8 = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2GRAY)
    img_rgb_u8 = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2RGB)

    # --- AprilTag detection ---
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
    detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
    corners, ids, rejected = detector.detectMarkers(img_gray_u8)

    st.write(f"Found {len(ids) if ids is not None else 0} markers.")
    marker_center = None
    if ids is not None and len(corners) > 0:
        for c in corners:
            c_int = c.astype(int)
            cv2.polylines(img_rgb_u8, [c_int], True, (0, 255, 255), 2)
        marker_center = np.mean(corners[0][0], axis=0).astype(int)
        # distance between the corners is the size of the marker
        tag_side_length = np.linalg.norm(corners[0][0][0] - corners[0][0][1])
        tag_size = 35
        pixel_to_mm = tag_size / tag_side_length

    H, W = img_gray_u8.shape[:2]

    # --- ROI estimation ---
    if marker_center is not None:
        cx, cy = int(marker_center[0]), int(marker_center[1])
        est_cx, est_cy = cx - 400, cy - 200  # tweak for physical placement
    else:
        est_cx, est_cy = W // 2, H // 2

    roi_half = 600
    x0, y0 = max(0, est_cx - roi_half), max(0, est_cy - roi_half)
    x1, y1 = min(W, est_cx + roi_half), min(H, est_cy + roi_half)
    roi_gray = img_gray_u8[y0:y1, x0:x1]

    # --- Preprocess + Hough ---
    roi_blur = cv2.medianBlur(roi_gray, 9)
    roi_edge = cv2.Canny(roi_blur, 30, 80)

    circles = cv2.HoughCircles(
        roi_edge,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=250,
        param1=140,
        param2=28,
        minRadius=300,
        maxRadius=500,
    )
    circle_center = None
    # --- Post-filter: keep circles near estimated center ---
    if circles is not None:
        circles = np.uint16(np.around(circles))[0]
        kept = []
        for x, y, r in circles:
            gx, gy = int(x + x0), int(y + y0)
            if (gx - est_cx) ** 2 + (gy - est_cy) ** 2 <= (120**2):
                kept.append((gx, gy, int(r)))

        kept.sort(key=lambda t: t[2], reverse=True)
        if kept:
            for gx, gy, r in kept[:1]:
                cv2.circle(img_rgb_u8, (gx, gy), r, (0, 255, 0), 2)
                cv2.circle(img_rgb_u8, (gx, gy), 2, (0, 0, 255), 3)

            circle_center = (kept[0][0], kept[0][1])
            circle_rho = math.isqrt(
                int((circle_center[0] ** 2 + (circle_center[1] ** 2)))
            )
            circle_rho_mm = circle_rho * pixel_to_mm
            circle_theta_deg = math.degrees(
                math.atan2(circle_center[1], circle_center[0])
            )
            r = kept[0][2]
            st.write(
                f"Detected circle center at: {circle_center} with radius {r} pixels {r * pixel_to_mm:.2f} mm"
            )
            st.write(
                f"Circle center polar coordinates: rho={circle_rho} pixels ({circle_rho_mm:.2f} mm), theta={circle_theta_deg} degrees, pixels_to_mm={pixel_to_mm:.2f}"
            )
            st.write(
                f"Board center polar coordinates: rho={board_rho} pixels ({board_rho * pixel_to_mm:.2f} mm), theta={math.degrees(board_theta_rad)} degrees"
            )
            marker_to_circle = np.sqrt(
                (circle_center[0] - est_cx) ** 2 + (circle_center[1] - est_cy) ** 2
            )
            st.write(
                f"Marker to circle center: {marker_to_circle:.2f} pixels {marker_to_circle * pixel_to_mm:.2f} mm"
            )
    else:
        st.warning(
            "No circles detected. Try adjusting the Hough parameters or thresholds."
        )

    for piece in pieces_list:
        cls_name = piece["class"]
        color = CLASS_COLORS[cls_name]
        x1, y1, x2, y2 = piece["x1"], piece["y1"], piece["x2"], piece["y2"]
        cv2.rectangle(img_rgb_u8, (x1, y1), (x2, y2), color, 2)
        st.write(f"Found {cls_name} at ({piece['polar1']}, {piece['polar2']})")

    cv2.rectangle(img_rgb_u8, (x0, y0), (x1, y1), (255, 255, 0), 2)
    cv2.circle(img_rgb_u8, (est_cx, est_cy), 6, (255, 255, 0), -1)
    st.image(img_rgb_u8, caption="Board Detection")

    results = where_are_pieces(pieces_list, board_center, pixel_to_mm)

    for result in results:
        piece = result["class"]
        cell = result["cell"]
        st.write(
            f"Piece {piece} is in cell {cell} inner {result['is_inner_ring']} rho {result['piece_mid_rho']}"
        )
