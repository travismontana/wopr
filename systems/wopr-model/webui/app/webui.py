import streamlit as st
from ultralytics import YOLO
import cv2
import os
from PIL import Image
import tempfile
import numpy as np

st.title("WOPR Object Detection")
st.set_page_config(layout="wide")

RUNS_PATH = "/ultralytics/runs"

# Model selection (with caching)
@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)


# Session state for model path
if "model_path" not in st.session_state:
    st.session_state.model_path = None

# Model selection section
if st.session_state.model_path is None:
    pt_files = []
    for root, dirs, files in os.walk(RUNS_PATH):
        for file in files:
            if file.endswith(".pt"):
                pt_files.append(os.path.join(root, file))

    if len(pt_files) == 0:
        st.warning("No model files found in runs directory.")
    else:
        selected_path = st.selectbox("Select model file", options=sorted(pt_files))
        st.code(selected_path, language="text")
    if st.button("Select Model"):
        st.session_state.model_path = selected_path
        st.rerun()
else:
    # Model loaded - show inference controls
    model = load_model(st.session_state.model_path)

    # Confidence/IoU sliders
    conf = st.slider("Confidence", 0.0, 1.0, 0.25)
    iou = st.slider("IoU", 0.0, 1.0, 0.45)

    # Source selection
    source_type = st.radio("Source", ["Image Upload", "Video Upload", "Webcam"])

    if source_type == "Image Upload":
        uploaded = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        if uploaded:
            img = Image.open(uploaded)

            # Run detection
            results = model.predict(source=img, conf=conf, iou=iou)

            # Display annotated image
            annotated = results[0].plot(pil=True)
            st.image(annotated, caption="Detections")

            # Show detection details
            st.write(f"Detected {len(results[0].boxes)} objects")
            for box in results[0].boxes:
                cls = model.names[int(box.cls[0])]
                conf_score = float(box.conf[0])
                st.write(f"- {cls}: {conf_score:.2f}")

    # Change model button
    if st.button("Change Model"):
        st.session_state.model_path = None
        st.rerun()

if uploaded:
    uploaded_file = uploaded
    raw_bytes = uploaded_file.read()
    raw_buf_u8 = np.frombuffer(raw_bytes, dtype=np.uint8)
    img_bgr_u8 = cv2.imdecode(raw_buf_u8, cv2.IMREAD_COLOR)
    img_gray_u8 = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2GRAY)
    img_rgb_u8 = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2RGB)

    # --- Detect AprilTag (grayscale is correct here) ---
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_25h9)
    detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
    corners, ids, rejected = detector.detectMarkers(img_gray_u8)

    st.write(f"Found {len(ids) if ids is not None else 0} markers.")
    marker_center = None
    if ids is not None and len(corners) > 0:
        for c in corners:
            c_int = c.astype(int)
            cv2.polylines(img_rgb_u8, [c_int], True, (0, 255, 255), 2)
        marker_center = np.mean(corners[0][0], axis=0).astype(int)

    H, W = img_gray_u8.shape[:2]

    # --- ROI: if you have a marker, search near it; else search middle-ish ---
    if marker_center is not None:
        cx, cy = int(marker_center[0]), int(marker_center[1])
        # board center is offset from tag; adjust these once you measure it
        est_cx, est_cy = cx - 400, cy - 200  # <-- tweak for your physical placement
    else:
        est_cx, est_cy = W // 2, H // 2

    roi_half = 600  # px; keep it big enough to include the whole board
    x0, y0 = max(0, est_cx - roi_half), max(0, est_cy - roi_half)
    x1, y1 = min(W, est_cx + roi_half), min(H, est_cy + roi_half)
    roi_gray = img_gray_u8[y0:y1, x0:x1]

    # --- Preprocess on GRAYSCALE (this is the big bugfix) ---
    # roi_blur = cv2.GaussianBlur(roi_gray, (9, 9), 1.5)
    roi_blur = cv2.medianBlur(
        roi_gray, 9
    )  # median can be better for sharp edges and noise
    roi_edges = cv2.Canny(roi_blur, 20, 80)  # raise thresholds vs 10/50

    # --- Hough on edges (single-channel) ---
    circles = cv2.HoughCircles(
        roi_blur,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=250,  # >= expected board diameter/2
        param1=140,  # internal Canny high threshold used by Hough
        param2=28,  # HIGHER => fewer false positives
        minRadius=300,  # tighten to your board
        maxRadius=500,
    )

    # --- Post-filter: keep only circles near estimated center ---
    if circles is not None:
        circles = np.uint16(np.around(circles))[0]
        kept = []
        for x, y, r in circles:
            gx, gy = int(x + x0), int(y + y0)  # back to global coords
            # center proximity filter (tune 60..150)
            if (gx - est_cx) ** 2 + (gy - est_cy) ** 2 <= (120**2):
                kept.append((gx, gy, int(r)))

        # draw best (largest radius is usually the outer rim)
        kept.sort(key=lambda t: t[2], reverse=True)
        for gx, gy, r in kept[:1]:
            cv2.circle(img_rgb_u8, (gx, gy), r, (0, 255, 0), 2)
            cv2.circle(img_rgb_u8, (gx, gy), 2, (0, 0, 255), 3)

        circle_center = (gx, gy)
        st.write(f"Detected circle center at: {circle_center} with radius {r}")
        marker_to_circle = np.sqrt(
            (circle_center[0] - est_cx) ** 2 + (circle_center[1] - est_cy) ** 2
        )
        st.write(f"Distance from estimated center: {marker_to_circle:.2f} pixels")
        # convert pixel distance to real-world units if you know the scale (e.g., mm/px)
        # the marker is 35mm in real life, so you can use that to estimate scale if you measure its pixel size

    else:
        st.warning(
            "No circles detected. Try adjusting the Hough parameters or thresholds."
        )
    cv2.rectangle(img_rgb_u8, (x0, y0), (x1, y1), (255, 255, 0), 2)
    cv2.circle(img_rgb_u8, (est_cx, est_cy), 6, (255, 255, 0), -1)
    st.image(img_rgb_u8)
