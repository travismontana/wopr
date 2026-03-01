import streamlit as st
import cv2
import sys
import numpy as np
import math
import socket

from pupil_apriltags import Detector

from lib.helpers import setup_logger
from lib.helpers import wopr_json

logger = setup_logger()


def open_camera(host, port):
    return MJPEGStream(host, port)


class MJPEGStream:
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, int(port)))
        self.buf = b""

    def read(self):
        # Feed buffer until we have a complete JPEG
        if "frames_to_process" in st.session_state.knobs["System"]:
            frames_to_process = st.session_state.knobs["System"]["frames_to_process"][
                "value"
            ]
        else:
            frames_to_process = 10

        # grab the number of frames requested to be processed
        frames = []
        for count in range(frames_to_process):
            # Inner loop: accumulate until we have a complete frame
            while True:
                self.buf += self.sock.recv(65536)
                start = self.buf.find(b"\xff\xd8")
                end = self.buf.find(b"\xff\xd9")
                # FIX: circuit breaker - bail if buffer grows without a valid frame
                if len(self.buf) > 10_000_000:
                    logger.warning(
                        f"Buffer overflow without valid frame on frame {count}, flushing buffer"
                    )
                    self.buf = b""
                    break
                if start != -1 and end != -1 and end > start:
                    logger.debug(
                        f"Frame {count}: complete JPEG found at [{start}:{end+2}], buf size={len(self.buf)}"
                    )
                    break  # got a complete frame
                else:
                    logger.debug(
                        f"Frame {count}: incomplete JPEG in buffer, accumulating (buf size={len(self.buf)})"
                    )

            jpg = self.buf[start : end + 2]
            self.buf = self.buf[end + 2 :]
            frame = cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)
            if frame is not None:
                logger.debug(
                    f"Frame {count}: decoded successfully, shape={frame.shape}"
                )
                frames.append(frame)
            else:
                logger.warning(f"Frame {count}: cv2.imdecode returned None, skipping")

        logger.info(f"Read complete: {len(frames)}/{frames_to_process} frames captured")
        return frames

    def release(self):
        self.sock.close()


def process_frame(frame):
    logger.info(f"Processing frame: {frame.shape}")
    notes = {"info": {}, "image": {}}
    notes["info"]["frame_shape"] = frame.shape

    original_image = frame.copy()
    logger.debug("Frame copied for processing")

    # Scaling
    scale = st.session_state.knobs["System"]["image_processing_scale"]["value"]
    logger.info(f"Image processing scale: {scale}")
    resized_image = cv2.resize(original_image, (0, 0), fx=scale, fy=scale)
    notes["info"]["resized_shape"] = resized_image.shape

    # Marker
    marker_mm = st.session_state.knobs["System"]["image_processing_marker_size_mm"][
        "value"
    ]
    logger.info(f"Marker size (mm): {marker_mm}")
    notes["info"]["marker_size_mm"] = marker_mm
    marker_scaled_mm = marker_mm * scale
    logger.info(f"Marker size (scaled mm): {marker_scaled_mm}")
    notes["info"]["marker_scaled_mm"] = marker_scaled_mm

    # Normalizing
    rgb_normal = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
    notes["info"]["rgb_normal_shape"] = rgb_normal.shape
    height, width, color_channels = rgb_normal.shape

    bgr = rgb_bgr(rgb_normal)
    gray = grayscale(bgr)
    gray_gauss = gaussian_blur(gray)
    gray_gauss_otsu = otsu(gray_gauss)
    notes["image"]["processed_gray"] = gray_gauss_otsu

    dp = st.session_state.knobs["Hough Circles"]["hg_circles_dp"]["value"]
    param1 = st.session_state.knobs["Hough Circles"]["hg_circles_param1"]["value"]
    param2 = st.session_state.knobs["Hough Circles"]["hg_circles_param2"]["value"]
    minRadius = int(
        height
        / st.session_state.knobs["Hough Circles"]["hg_circles_minRadius"]["value"]
    )
    maxRadius = int(
        height
        / st.session_state.knobs["Hough Circles"]["hg_circles_maxRadius"]["value"]
    )
    minDist = max(height, width)

    circle_result, circles = circle(
        gray_gauss_otsu, dp, minDist, param1, param2, minRadius, maxRadius, bgr
    )
    num_circles = len(circles) if circles is not None else 0
    if num_circles == 1:
        resulting_image = circle_result
        notes["info"]["num_circles"] = num_circles
        notes["info"]["circles"] = circles
        notes["image"]["resulting_image"] = resulting_image
    else:
        circle_path = st.session_state.knobs["Hough Circles"]["hg_circles_path"][
            "value"
        ]
        next_img = gray_gauss_otsu
        for step in circle_path:

            logger.info(f"Retrying circle detection with step: {step}")
            step_fn = CIRCLE_DETECTION_STEPS.get(step)
            if step_fn is None:
                logger.warning(f"Step function not found for step: {step}")
                continue
            logger.info(f"Applying step function: {step}")
            next_img = step_fn(next_img)
            circle_result, circles = circle(
                next_img, dp, minDist, param1, param2, minRadius, maxRadius, bgr
            )
            num_circles = len(circles) if circles is not None else 0
            if num_circles == 1:
                notes["info"]["num_circles"] = num_circles
                notes["image"]["resulting_image"] = circle_result
                break
        else:
            logger.warning(
                "Circle detection exhausted all path steps without finding a circle"
            )
            notes["status"] = "failed"
            notes["message"] = "No circles detected"
            return notes

    detect_tag = st.session_state.knobs["Marker"]["marker_type"]["value"]
    detect_nthreads = st.session_state.knobs["Marker"]["nthreads"]["value"]
    detect_quad_decimate = st.session_state.knobs["Marker"]["quad_decimate"]["value"]
    detect_quad_sigma = st.session_state.knobs["Marker"]["quad_sigma"]["value"]
    detect_refine_edges = st.session_state.knobs["Marker"]["quad_refine_edges"]["value"]

    marker_result, marker = get_marker(
        gray,
        detect_tag,
        detect_nthreads,
        detect_quad_decimate,
        detect_quad_sigma,
        detect_refine_edges,
        bgr,
    )

    num_markers = len(marker) if marker else 0
    notes["info"]["num_markers"] = num_markers
    notes["info"]["markers"] = marker

    marker_path = st.session_state.knobs["Marker"]["marker_detection_path"]["value"]

    if num_markers == 1:
        logger.info("Marker found on initial detection, skipping path retry")
        notes["info"]["num_markers"] = num_markers
        notes["image"]["resulting_image"] = marker_result
    else:
        logger.info(
            f"Initial marker detection found {num_markers}, entering path retry with {len(marker_path)} steps"
        )
        next_img = gray
        for step in marker_path:
            logger.info(f"Retrying marker detection with step: {step}")
            step_fn = MARKER_DETECTION_STEPS.get(step)
            if step_fn is None:
                logger.warning(f"Step function not found for step: {step}")
                continue
            logger.info(f"Applying step function: {step}")
            next_img = step_fn(next_img)
            marker_result, markers = get_marker(
                next_img,
                detect_tag,
                detect_nthreads,
                detect_quad_decimate,
                detect_quad_sigma,
                detect_refine_edges,
                bgr,
            )
            num_markers = len(markers) if markers else 0
            notes["info"]["num_markers"] = num_markers
            notes["info"]["markers"] = markers
            if num_markers == 1:
                logger.info(f"Marker found after step '{step}'")
                notes["image"]["resulting_image"] = marker_result
                break
        else:
            logger.warning(
                "Marker detection exhausted all path steps without finding a marker"
            )
            notes["status"] = "failed"
            notes["message"] = "No markers detected"
            return notes

    return notes


def grayscale(image):
    logger.info(f"Converting image to grayscale")
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def rgb_bgr(image):
    logger.info(f"Converting image from RGB to BGR")
    return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


def bgr_rgb(image):
    logger.info(f"Converting image from BGR to RGB")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def gaussian_blur(image):
    logger.info(f"Applying Gaussian blur")
    return cv2.GaussianBlur(image, (5, 5), 0)


def otsu(image):
    logger.info(f"Applying Otsu's thresholding")
    ret, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def clahe(image):
    logger.info("Applying CLAHE")
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)


def filter2d(image):
    logger.info("Applying 2D filter")
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    return cv2.filter2D(image, -1, kernel)


def canny(image):
    threshold1 = st.session_state.knobs["Canny"]["canny_threshold1"]["value"]
    threshold2 = st.session_state.knobs["Canny"]["canny_threshold2"]["value"]
    logger.info(
        f"Applying Canny edge detection with thresholds: {threshold1}, {threshold2}"
    )
    return cv2.Canny(image, threshold1, threshold2)


def circle(image, dp, minDist, param1, param2, minRadius, maxRadius, bgr):
    logger.info(f"Detecting circles")
    bgr_out = bgr.copy()
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
            cv2.circle(bgr_out, (x, y), r, (0, 255, 0), 4)

    return bgr_out, circles


@st.cache_resource
def get_detector(families, nthreads, quad_decimate, quad_sigma, refine_edges):
    logger.info(
        f"Creating detector: families={families}, nthreads={nthreads}, quad_decimate={quad_decimate}, quad_sigma={quad_sigma}, refine_edges={refine_edges}"
    )
    return Detector(
        families=families,
        nthreads=nthreads,
        quad_decimate=quad_decimate,
        quad_sigma=quad_sigma,
        refine_edges=refine_edges,
    )


def get_marker(
    image,
    detect_tag,
    detect_nthreads,
    detect_quad_decimate,
    detect_quad_sigma,
    detect_refine_edges,
    bgr,
):
    bgr_out = bgr.copy()
    detector = get_detector(
        detect_tag,
        detect_nthreads,
        detect_quad_decimate,
        detect_quad_sigma,
        detect_refine_edges,
    )
    tags = detector.detect(image)
    num_tags = len(tags) if tags is not None else 0
    logger.info(f"Number of tags detected: {num_tags}")

    if tags is not None and num_tags > 0:
        # *** filter out low-confidence detections ***
        min_decision_margin = st.session_state.knobs["Marker"]["min_decision_margin"][
            "value"
        ]
        tags = [t for t in tags if t.decision_margin >= min_decision_margin]
        num_tags = len(tags)
        logger.info(
            f"Tags after confidence filter (min_margin={min_decision_margin}): {num_tags}"
        )
        for tag in tags:
            cv2.polylines(bgr_out, [tag.corners.astype(int)], True, (0, 255, 0), 2)

    return bgr_out, tags


MARKER_DETECTION_STEPS = {
    "clahe": clahe,
    "gaussian_blur": gaussian_blur,
    "filter2d": filter2d,
    "otsu": otsu,
    "canny": canny,
}

CIRCLE_DETECTION_STEPS = {
    "clahe": clahe,
    "gaussian_blur": gaussian_blur,
    "filter2d": filter2d,
    "canny": canny,
}
