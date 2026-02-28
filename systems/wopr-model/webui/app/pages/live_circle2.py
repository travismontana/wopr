import requests
import streamlit as st
import numpy as np
import cv2
import os
from PIL import Image
from io import BytesIO
import logging
import sys

CAMURL = os.getenv("CAMURL", "http://localhost:8080")

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.title("Live CV Work")

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


@st.cache_data
def process_image(raw: bytes):
    logger.info(f"Processing image of size: {len(raw)} bytes")
    image = Image.open(BytesIO(raw))
    rgb_normal = np.array(image)
    scale = 0.25
    rgb = cv2.resize(rgb_normal, (0, 0), fx=scale, fy=scale)
    logger.info(f"Image shape: {rgb.shape}")
    height, width, c_chan = rgb.shape

    bgr = rgb_bgr(rgb)
    gray = grayscale(rgb)

    gray_gauss = gauss(gray)

    gray_otsu = otsu(gray_gauss)

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

    gray_circle = circle(gray_otsu, dp, minDist, param1, param2, minRadius, maxRadius)

    gray = gray_circle

    return bgr, gray

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


def circle(image, dp, minDist, param1, param2, minRadius, maxRadius):
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
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        logger.info(f"Found {len(circles)} circles")
        for x, y, r in circles:
            cv2.circle(image, (x, y), r, (0, 255, 0), 4)
    return image


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

bgr_c950, gray_c950 = process_image(raw_c950)
logger.info(f"Processed images: C950={bgr_c950.shape}, C960={bgr_c950.shape}")
bgr_c960, gray_c960 = process_image(raw_c960)
logger.info(f"Processed images: C960={bgr_c960.shape}, C960={bgr_c960.shape}")

c950, c960 = st.columns(2)
with c950:
    st.image(raw_c950, caption="Raw C950")
    st.image(bgr_c950, channels="BGR", caption="Camera C950")
    st.image(gray_c950, caption="Result C950")
with c960:
    st.image(raw_c960, caption="Raw C960")
    st.image(bgr_c960, channels="BGR", caption="Camera C960")
    st.image(gray_c960, caption="Result C960")
