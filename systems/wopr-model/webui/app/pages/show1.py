import streamlit as st
import numpy as np
import cv2

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.title("CV Pipeline")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
if uploaded_file is None:
    st.info("Upload an image to get started.")
    st.stop()

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
    est_cx, est_cy = cx - 180, cy - 30  # <-- tweak for your physical placement
else:
    est_cx, est_cy = W // 2, H // 2

roi_half = 420  # px; keep it big enough to include the whole board
x0, y0 = max(0, est_cx - roi_half), max(0, est_cy - roi_half)
x1, y1 = min(W, est_cx + roi_half), min(H, est_cy + roi_half)
roi_gray = img_gray_u8[y0:y1, x0:x1]

# --- Preprocess on GRAYSCALE (this is the big bugfix) ---
# roi_blur = cv2.GaussianBlur(roi_gray, (9, 9), 1.5)
roi_blur = cv2.MedianBlur(roi_gray, 9)  # median can be better for sharp edges and noise
roi_edges = cv2.Canny(roi_blur, 20, 80)  # raise thresholds vs 10/50

# --- Hough on edges (single-channel) ---
circles = cv2.HoughCircles(
    roi_edges,
    cv2.HOUGH_GRADIENT_ALT,
    dp=1.2,
    minDist=300,  # >= expected board diameter/2
    param1=60,  # internal Canny high threshold used by Hough
    param2=0,  # HIGHER => fewer false positives
    minRadius=210,  # tighten to your board
    maxRadius=260,
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
else:
    st.warning("No circles detected. Try adjusting the Hough parameters or thresholds.")

st.image(img_rgb_u8)
