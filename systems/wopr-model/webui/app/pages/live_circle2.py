import requests
import streamlit as st
import numpy as np
import cv2
import os
from PIL import Image
from io import BytesIO
import logging
import sys
from pupil_apriltags import Detector

CAMURL = os.getenv("CAMURL", "http://localhost:8080")

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.title("Live CV Work")
min_dec_marg = st.slider(
    "Minimum Decision Margin", 0.0, 100.0, 20.0, key="min_decision_margin"
)
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

        return bgr, gray, resulting_image, notes
    gray = gray_otsu
    ratios = get_ratios(markers[0], marker_size_mm)
    notes.append({"ratios": ratios})

    mark_circ_dist = get_distance(markers[0], circles[0])

    if mark_circ_dist is not None:
        logger.info(f"Distance between marker and circle: {mark_circ_dist}px")
        notes.append({"mark_circ_dist_px": mark_circ_dist})
        mcd_mm = mark_circ_dist * ratios[1]
        notes.append({"mark_circ_dist_mm": mcd_mm})
        return bgr, gray, resulting_image, notes

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
    st.image(final_c950, caption="Final C950")
    st.json(notes_c950, expanded=False)
    st.image(raw_c950, caption="Raw C950")
    st.image(bgr_c950, channels="BGR", caption="Camera C950")
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
    st.image(final_c960, caption="Final C960")
    st.json(notes_c960, expanded=False)
    st.image(raw_c960, caption="Raw C960")
    st.image(bgr_c960, channels="BGR", caption="Camera C960")
    st.image(gray_c960, caption="Result C960")
    logger.info(notes_c960)
