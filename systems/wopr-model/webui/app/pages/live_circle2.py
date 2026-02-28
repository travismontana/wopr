import requests
import streamlit as st
import numpy as np
import cv2
import os
import math
from PIL import Image
from io import BytesIO
import logging
import sys
from pupil_apriltags import Detector


CAMURL = os.getenv("CAMURL", "http://localhost:8080")

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.title("Live CV Work")
min_dec_marg = st.slider(
    "Minimum Decision Margin", 0.0, 50.0, 20.0, key="min_decision_margin"
)
canny_threshold1 = st.slider("Canny Threshold 1", 0, 500, 100, key="canny_threshold1")
canny_threshold2 = st.slider("Canny Threshold 2", 0, 500, 200, key="canny_threshold2")
rho = st.slider("Rho", 1, 10, 1, key="rho")
theta = st.slider("Theta", 0.0, np.pi, np.pi / 180, key="theta")
line_threshold = st.slider("Line Threshold", 0, 500, 100, key="line_threshold")
line_gap = st.slider("Line Gap", 0, 50, 10, key="line_gap")
img_rgb_u8_c950 = None
raw_u8_c950 = None


img_rgb_u8_c960 = None
raw_u8_c960 = None


def setup_logger(logger_name="wopr") -> logging.Logger:
    """
    Configure logging for helper functions.

    Returns:
        Configured logger instance

    Note:
        Only configures once - subsequent calls return existing logger
    """
    file_path = "/tmp/wopr.log"
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger  # Already configured

    logger.setLevel(logging.DEBUG)
    logging.FileHandler(file_path)
    handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    return logger


logger = setup_logger()


@st.cache_data(ttl=30)
def fetch_snapshot(url: str) -> bytes:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    # *** Convert to JPEG before caching — smaller key, faster cache hits ***
    image = Image.open(BytesIO(response.content))
    buf = BytesIO()
    image.convert("RGB").save(buf, format="JPEG", quality=85)
    return buf.getvalue()


# @st.cache_data
def process_image(raw: bytes):
    logger.info(f"Processing image of size: {len(raw)} bytes")
    notes = []
    scale = 0.25
    msmm_org = 35
    marker_size_mm = msmm_org * scale
    image = Image.open(BytesIO(raw))
    org_image_size = image.size
    notes.append({"original_size": org_image_size})

    rgb_normal = np.array(image)
    rgb = cv2.resize(rgb_normal, (0, 0), fx=scale, fy=scale)
    scale_size = rgb.shape
    logger.info(f"Image shape: {rgb.shape}")
    notes.append({"scaled_size": scale_size})
    height, width, c_chan = rgb.shape

    # Width of the histogram bars 1-2
    dp = 1.75
    # minDist, min distance between the center of the circles 0-sizeofimage
    minDist = max(height, width)
    # param1, higher, stronger the edge has to be, 50-100-200,
    param1 = 50
    # param2, if not ALT, confidence level 0-circumfrence in pixels, if ALT, roundness, 0-1, .8-.95 normal
    param2 = 30
    # minRadius, minimum radius of the circles, in pixels
    minRadius = int(height / 5)
    # maxRadius, maximum radius of the circles, in pixels
    maxRadius = int(height / 2)

    bgr = rgb_bgr(rgb)
    gray = grayscale(rgb)

    gray_gauss = gauss(gray)
    # gray = gray_gauss

    gray_otsu = otsu(gray_gauss)

    circle_result, circles = circle(
        gray_otsu, dp, minDist, param1, param2, minRadius, maxRadius, bgr
    )
    resulting_image = circle_result
    num_circles = len(circles) if circles is not None else 0
    notes.append({"num_circles": num_circles, "circles": circles})
    if circles is not None and num_circles != 1:
        logger.info(f"Number of circles detected is not 1: {num_circles}")
        resulting_image = circle_result
        return bgr, gray, resulting_image, notes

    # detect_tag, type of tag to detect
    detect_tag = "tag36h11"
    # detect_nthreads, number of threads for detect
    detect_nthreads = 4
    # detect_quad_decimage, downsampling factor used before searching for tag quads, more makes it a smaller image
    detect_quad_decimate = 1.0
    # detect_refine_edges, sharp (1) or weak (0) corners,
    detect_refine_edges = 1

    marker_result, markers = get_marker(
        gray_gauss,
        detect_tag,
        detect_nthreads,
        detect_quad_decimate,
        detect_refine_edges,
        bgr,
    )
    num_markers = len(markers) if markers is not None else 0
    notes.append({"num_markers": num_markers, "markers": markers})
    if markers is not None and num_markers != 1:
        logger.info(f"Number of markers detected is not 1: {num_markers}")
        logger.info(f"First retry")
        next_img = gauss(gray)
        marker_result, markers = get_marker(
            next_img,
            detect_tag,
            detect_nthreads,
            detect_quad_decimate,
            detect_refine_edges,
            bgr,
        )
        num_markers = len(markers) if markers is not None else 0
        notes.append({"num_markers": num_markers, "markers": markers})
        if markers is not None and num_markers != 1:
            logger.info(f"Second retry")
            next2_img = clahe(next_img)
            marker_result, markers = get_marker(
                next2_img,
                detect_tag,
                detect_nthreads,
                detect_quad_decimate,
                detect_refine_edges,
                bgr,
            )
            num_markers = len(markers) if markers is not None else 0
            notes.append({"num_markers": num_markers, "markers": markers})
            if markers is not None and num_markers != 1:
                logger.info("Third retry")
                next3_img = filter2d(next2_img)
                marker_result, markers = get_marker(
                    next3_img,
                    detect_tag,
                    detect_nthreads,
                    detect_quad_decimate,
                    detect_refine_edges,
                    bgr,
                )
                num_markers = len(markers) if markers is not None else 0
                notes.append({"num_markers": num_markers, "markers": markers})
                if markers is not None and num_markers != 1:
                    return bgr, gray, resulting_image, notes

    ratios = get_ratios(markers[0], marker_size_mm)
    notes.append({"ratios": ratios})

    mark_circ_dist = get_distance(markers[0], circles[0])
    resulting_image = marker_result
    if mark_circ_dist is not None:
        logger.info(f"Distance between marker and circle: {mark_circ_dist}px")
        notes.append({"mark_circ_dist_px": mark_circ_dist})
        mcd_mm = mark_circ_dist * ratios[1]
        notes.append({"mark_circ_dist_mm": mcd_mm})
    else:
        return bgr, gray, resulting_image, notes

    mark_x = markers[0].center[0]
    mark_y = markers[0].center[1]
    circle_x = circles[0][0]
    circle_y = circles[0][1]
    mark_circle_rho = mark_circ_dist
    mark_circle_theta = math.atan2(circle_y - mark_y, circle_x - mark_x)
    notes.append(
        {"mark_circle_rho": mark_circle_rho, "mark_circle_theta": mark_circle_theta}
    )
    base_line = {"start": (mark_x, mark_y), "end": (circle_x, circle_y)}
    cv2.line(
        resulting_image,
        (int(mark_x), int(mark_y)),
        (int(circle_x), int(circle_y)),
        (0, 255, 0),
        2,
    )

    gray_canny = canny(gray)

    resulting_image, lines = get_lines(
        gray_canny, mark_circ_dist, resulting_image, base_line
    )
    logger.info(f"Number of lines detected: {len(lines) if lines is not None else 0}")
    notes.append({"lines": lines})

    gray = gray_canny

    return bgr, gray, resulting_image, notes

def grayscale(image):
    logger.info(f"Converting image to grayscale")
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def rgb_bgr(image):
    logger.info(f"Converting image from RGB to BGR")
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

def bgr_rgb(image):
    logger.info(f"Converting image from BGR to RGB")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def gauss(image):
    logger.info(f"Applying Gaussian blur")
    return cv2.GaussianBlur(image, (5, 5), 0)

def otsu(image):
    logger.info(f"Applying Otsu's thresholding")
    ret, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def circle(image, dp, minDist, param1, param2, minRadius, maxRadius, bgr):
    logger.info(f"Detecting circles")
    circles = cv2.HoughCircles(
        image,
        cv2.HOUGH_GRADIENT,
        dp=dp,
        minDist=minDist,
        param1=param1,
        param2=param2,
        minRadius=minRadius,
        maxRadius=maxRadius,
    )

    num_circles = len(circles) if circles is not None else 0
    logger.info(f"Number of circles detected: {num_circles}")
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for x, y, r in circles:
            cv2.circle(bgr, (x, y), r, (0, 255, 0), 4)

    return bgr, circles


def get_marker(
    image,
    detect_tag,
    detect_nthreads,
    detect_quad_decimate,
    detect_refine_edges,
    bgr,
):
    detector = Detector(
        families=detect_tag,
        nthreads=detect_nthreads,
        quad_decimate=detect_quad_decimate,
        refine_edges=detect_refine_edges,
    )
    tags = detector.detect(image)
    num_tags = len(tags) if tags is not None else 0
    logger.info(f"Number of tags detected: {num_tags}")
    # MIN_DECISION_MARGIN = 20.0  # tune this threshold

    if tags is not None and num_tags > 0:
        # *** filter out low-confidence detections ***
        tags = [t for t in tags if t.decision_margin >= min_dec_marg]
        num_tags = len(tags)
        logger.info(f"Tags after confidence filter: {num_tags}")
        for tag in tags:
            cv2.polylines(bgr, [tag.corners.astype(int)], True, (0, 255, 0), 2)

    return bgr, tags


def canny(image, threshold1=canny_threshold1, threshold2=canny_threshold2):
    logger.info(
        f"Applying Canny edge detection with thresholds: {threshold1}, {threshold2}"
    )
    return cv2.Canny(image, threshold1, threshold2)


def get_lines(image, dist, bgr, base_line):
    logger.info("Detecting lines")
    lines = cv2.HoughLinesP(
        image, rho, theta, line_threshold, minLineLength=dist * 0.4, maxLineGap=line_gap
    )
    if lines is not None:
        good_lines = []
        for x1, y1, x2, y2 in lines[:, 0]:
            line_start = np.array([x1, y1])
            line_end = np.array([x2, y2])
            base_start = np.array(base_line["start"])
            base_end = np.array(base_line["end"])
            line_theta = math.atan2(y2 - y1, x2 - x1)
            base_theta = math.atan2(
                base_end[1] - base_start[1], base_end[0] - base_start[0]
            )
            diff = (line_theta - base_theta) % math.pi
            logger.info(f"Line angle difference: {math.degrees(diff)} degrees")
            thirtydeg = math.radians(30)
            tol = math.radians(15)
            nearest = round(diff / thirtydeg) * thirtydeg
            delta = abs(diff - nearest)
            delta = min(delta, math.pi - delta)
            logger.info(f"Line angle delta: {math.degrees(delta)} degrees")
            if delta <= tol:
                good_lines.append((x1, y1, x2, y2))
                cv2.line(bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
    logger.info(f"Number of good lines detected: {len(good_lines)}")
    return bgr, good_lines


def get_ratios(markers, marker_size_mm):
    corners = markers.corners
    marker_side_length_pixels = np.linalg.norm(corners[0] - corners[1])

    pixels_to_mm_ratio = marker_side_length_pixels / marker_size_mm
    mm_to_pixels_ratio = marker_size_mm / marker_side_length_pixels

    return (pixels_to_mm_ratio, mm_to_pixels_ratio)


def get_distance(markers, circles):
    circle_x, circle_y, radius = circles
    marker_center = markers.center

    dist_between = np.linalg.norm(
        np.array([circle_x, circle_y]) - np.array(marker_center)
    )
    return dist_between


def clahe(image):
    logger.info("Applying CLAHE")
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)


def filter2d(image):
    logger.info("Applying 2D filter")
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(image, -1, kernel)


def get_images(url):
    try:
        raw = fetch_snapshot(url)
        image = Image.open(BytesIO(raw))
        return image, raw
    except Exception as e:
        st.error(f"Failed to fetch snapshot: {e}")
        st.stop()

def build_images():
    global img_rgb_u8_c950, raw_u8_c950, img_rgb_u8_c960, raw_u8_c960
    img_rgb_u8_c950, raw_u8_c950 = get_images(f"{CAMURL}:5101/snapshot")
    img_rgb_u8_c960, raw_u8_c960 = get_images(f"{CAMURL}:5100/snapshot")


cam_options = [
    {"name": "c950", "endpoint": f"{CAMURL}:5101/snapshot"},
    {"name": "c960", "endpoint": f"{CAMURL}:5100/snapshot"},
    {"name": "rPi", "endpoint": f"{CAMURL}:5102/snapshot"},
]

st.button("Refresh", on_click=fetch_snapshot.clear)  # *** bust the cache on click ***

raw_c950 = fetch_snapshot(f"{CAMURL}:5101/snapshot")
raw_c960 = fetch_snapshot(f"{CAMURL}:5100/snapshot")
logger.info(f"Fetched snapshots: C950={len(raw_c950)} bytes, C960={len(raw_c960)} bytes")

bgr_c950, gray_c950, final_c950, notes_c950 = process_image(raw_c950)
logger.info(f"Processed images: C950={bgr_c950.shape}, C960={bgr_c950.shape}")

bgr_c960, gray_c960, final_c960, notes_c960 = process_image(raw_c960)
logger.info(f"Processed images: C960={bgr_c960.shape}, C960={bgr_c960.shape}")

c950_lines = next((n["lines"] for n in notes_c950 if "lines" in n), None)
c960_lines = next((n["lines"] for n in notes_c960 if "lines" in n), None)

c950_mark_circ_dist_mm = next(
    (n["mark_circ_dist_mm"] for n in notes_c950 if "mark_circ_dist_mm" in n), None
)
c960_mark_circ_dist_mm = next(
    (n["mark_circ_dist_mm"] for n in notes_c960 if "mark_circ_dist_mm" in n), None
)

c950_mark_circ_dist_px = next(
    (n["mark_circ_dist_px"] for n in notes_c950 if "mark_circ_dist_px" in n), None
)
c960_mark_circ_dist_px = next(
    (n["mark_circ_dist_px"] for n in notes_c960 if "mark_circ_dist_px" in n), None
)

if c950_mark_circ_dist_mm is not None and c960_mark_circ_dist_mm is not None:
    percent_difference = (
        abs(c950_mark_circ_dist_mm - c960_mark_circ_dist_mm)
        / ((c950_mark_circ_dist_mm + c960_mark_circ_dist_mm) / 2)
        * 100
    )
    st.write(f"Percent difference: {percent_difference:.2f}%")
c950, c960 = st.columns(2)
with c950:
    if c950_mark_circ_dist_mm is not None:
        st.write(
            f"Marker-Circle Distance (mm)(scaled): {c950_mark_circ_dist_mm:.2f} | {c950_mark_circ_dist_mm/.25:.2f}"
        )
        st.write(f"Marker-Circle Distance (px): {c950_mark_circ_dist_px}")
    else:
        st.warning("C950: Distance not computed — check detection results")
    if c950_lines is not None:
        st.write("Lines:")
        for c950_line in c950_lines:
            st.write(c950_line)
    st.image(final_c950, channels="BGR", caption="Final C950")
    st.json(notes_c950, expanded=False)
    st.json(c950_lines, expanded=False)
    # st.image(raw_c950, caption="Raw C950")
    # st.image(bgr_c950, channels="BGR", caption="Camera C950")
    st.image(gray_c950, caption="Result C950")
    logger.info(notes_c950)
with c960:
    if c960_mark_circ_dist_mm is not None:
        st.write(
            f"Marker-Circle Distance (mm)(scaled): {c960_mark_circ_dist_mm:.2f} | {c960_mark_circ_dist_mm/.25:.2f}"
        )
        st.write(f"Marker-Circle Distance (px): {c960_mark_circ_dist_px}")
    else:
        st.warning("C960: Distance not computed — check detection results")
    if c960_lines is not None:
        st.write("Lines:")
        for c960_line in c960_lines:
            st.write(c960_line)
    st.image(final_c960, channels="BGR", caption="Final C960")
    st.json(notes_c960, expanded=False)
    st.json(c960_lines, expanded=False)
    # st.image(raw_c960, caption="Raw C960")
    # st.image(bgr_c960, channels="BGR", caption="Camera C960")
    st.image(gray_c960, caption="Result C960")
    logger.info(notes_c960)
