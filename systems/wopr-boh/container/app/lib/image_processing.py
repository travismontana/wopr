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
    # Needs to be human re-written.
    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, int(port)))
        self.buf = b""

    def read(self):
        # Feed buffer until we have a complete JPEG
        frames_to_process = st.session_state.knobs["System"]["frames_to_process"][
            "value"
        ]

        # grab the number of frames requested to be processed
        frames = []
        for count in range(frames_to_process):
            # Inner loop: accumulate until we have a complete frame
            while True:
                count += 1
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


def start_process(frames):
    """start processing frames
    Walk through the set, and figure out which is the best by:
    Blur/Sharpness - Laplacian
    Edge clarity - Tenengrad
    Over/under exposed - Histogram analysis
    Shake/motion - FFT

    Save each of the frames with their respective scores and notes

    Then find the best (One, Three, or half the batch - how many to find)
    num_top_frames = st.session_state.knobs["System"]["num_top_frames"]["value"]

    return those

    Args:
        frames (_type_): _description_

    Returns:
        _type_: _description_
    """
    logger.info(f"Starting process for {len(frames)} frames")
    best_frame = None
    notes = {"info": {"frame_shape": None, "scaled_shape": None}}
    scores = []
    scale = st.session_state.knobs["System"]["image_processing_scale"]["value"]

    for frame in frames:
        frame_copy = frame.copy()
        notes["info"]["frame_shape"] = frame_copy.shape

        frame_copy_scaled = scale_image(frame_copy)
        notes["info"]["scaled_shape"] = frame_copy_scaled.shape

        frame_copy_scaled_gray = grayscale(frame_copy_scaled)

        score = score_frame(frame_copy_scaled_gray)
        logger.info(f"Frame score: {score}")
        scores.append(score)

    logger.info(f"Processing complete for {len(frames)} frames")

    ranked_frames = {"rank": None, "frame": None, "score": None, "combined_score": None}
    combined_frames = []
    ratio = st.session_state.knobs["System"]["Laplacian to Tenengrad Ratio"]["value"]
    for frame, score in zip(frames, scores):
        laplacian_score = score["laplacian"]
        tenengrad_score = score["tenengrad"]
        combined_score = laplacian_score * ratio + tenengrad_score * (1 - ratio)
        combined_frames.append(
            {"frame": frame, "score": score, "combined_score": combined_score}
        )

    ranked_frames = sorted(
        combined_frames, key=lambda x: x["combined_score"], reverse=True
    )

    return ranked_frames


def score_frame(frame):
    logger.info("Scoring frame")
    score = {}
    laplacian_score = laplacian(frame)
    tenengrad_score = tenengrad(frame)
    score["laplacian"] = laplacian_score
    score["tenengrad"] = tenengrad_score
    return score


def process_frame(frame):
    logger.info(f"Processing frame")
    notes = {"info": {}, "image": {}}
    notes["info"]["frame_shape"] = frame.shape
    original_image = frame.copy()
    logger.debug("Frame copied for processing")
    circles = []
    markers = []
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

    circle_result = circle(gray_gauss_otsu, height, width)
    logger.info(f"Circle detection results: {circle_result}")
    if "status" in circle_result and circle_result["status"] == "failure":
        notes["status"] = "failed"
        notes["message"] = {
            "error": "No circles detected",
            "circle": circle_result["message"].get("steps", {}).get("circle", {}),
        }
        logger.info(f"Circle detection failed: {notes}")
        return notes
    else:
        notes["info"]["num_circles"] = circle_result["message"].get("num_circles", 0)
        notes["info"]["circles"] = circle_result["message"].get("circles", [])
    logger.info(f"Notes so far: {notes}")

    # Marker time
    marker_result = get_marker(gray)
    logger.info(f"Marker detection results: {marker_result}")
    if "status" in marker_result and marker_result["status"] == "failure":
        notes["status"] = "failed"
        notes["message"] = {
            "error": "No markers detected",
            "circle": circle_result["message"].get("steps", {}).get("circle", {}),
            "marker": marker_result["message"].get("steps", {}).get("marker", {}),
        }
        logger.info(f"Marker detection failed: {notes}")
        return notes
    else:
        notes["info"]["num_markers"] = marker_result["message"].get("num_markers", 0)
        notes["info"]["markers"] = marker_result["message"].get("markers", [])

    # Lines
    # [ x, y]
    marker_center = (
        marker_result["message"]["markers"][0].center
        if marker_result["message"].get("markers")
        else (0, 0)
    )

    # [[[ x y r ]]] needs to be [ x, y ]
    circles = notes["info"]["circles"]
    circle_center = circles[0][0][:2] if circles is not None else (0, 0)
    r = circles[0][0][2] if circles is not None else 0
    logger.info(f"Marker center: {marker_center}, Circle center: {circle_center}")

    lines_result = get_lines(gray, marker_center, circle_center, r)
    notes["info"]["lines"] = lines_result
    # lines_image = lines_result["image"]["lines"]
    roi_masked_image = lines_result["image"]["lines"]["roi_masked"]
    # notes["image"]["lines"] = lines_image
    notes["image"]["roi_masked"] = roi_masked_image
    logger.info(f"Returning notes: {notes}")
    return notes

#######################################################################################
def tenengrad(image):
    logger.info(f"Getting Tenengrad variance")
    gx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    tenengrad = float(np.mean(gx**2 + gy**2))
    return tenengrad


def laplacian(image):
    logger.info(f"Getting Laplacian variance")
    return cv2.Laplacian(image, cv2.CV_64F).var()


def scale_image(image):
    scale = st.session_state.knobs["System"]["image_processing_scale"]["value"]
    logger.info(f"Scaling image by factor: {scale}")
    return cv2.resize(image, (0, 0), fx=scale, fy=scale)


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


def circle(image, height, width):
    logger.info(f"Detecting circles")
    results = {"status": "unknown", "message": {"steps": {}}}
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
    results["message"]["steps"]["circle"] = {}
    results["message"]["steps"]["circle"]["gray"] = {
        "step": "initial",
        "num_circles": num_circles,
        "circles": circles,
        "image": image,
    }

    if num_circles != 1:
        logger.info("Number of circles detected is not equal to 1")
        circle_detection_path = st.session_state.knobs["Hough Circles"][
            "hg_circles_path"
        ]["value"]
        for step in circle_detection_path:
            logger.info(f"Circle detection step: {step}")
            step_function = CIRCLE_DETECTION_STEPS.get(step)
            if step_function:
                image = step_function(image)
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
                results["message"]["steps"]["circle"][step] = {
                    "step": step,
                    "num_circles": num_circles,
                    "circles": circles,
                    "image": image,
                }
                if num_circles == 1:
                    break

    if num_circles != 1:
        logger.info("Unable to find the circle")
        results["status"] = "failure"
    else:
        logger.info(
            f"Circle detection successful: {num_circles} circle(s) found at {circles}"
        )
        results["status"] = "success"
        results["message"]["num_circles"] = num_circles
        results["message"]["circles"] = circles
    logger.info(f"Circle detection results: {results}")
    return results


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


def detect_marker(image, detector):
    return detector.detect(image)


def get_marker(
    image,
):
    detect_tag = st.session_state.knobs["Marker"]["marker_type"]["value"]
    detect_nthreads = st.session_state.knobs["Marker"]["nthreads"]["value"]
    detect_quad_decimate = st.session_state.knobs["Marker"]["quad_decimate"]["value"]
    detect_quad_sigma = st.session_state.knobs["Marker"]["quad_sigma"]["value"]
    detect_refine_edges = st.session_state.knobs["Marker"]["quad_refine_edges"]["value"]
    detector = get_detector(
        detect_tag,
        detect_nthreads,
        detect_quad_decimate,
        detect_quad_sigma,
        detect_refine_edges,
    )
    results = {"status": "unknown", "message": {"steps": {}}}
    markers = detect_marker(image, detector)
    num_markers = len(markers) if markers is not None else 0
    logger.info(f"Number of markers detected: {num_markers}")
    results["message"]["steps"] = {}
    results["message"]["steps"]["marker"] = {}
    results["message"]["steps"]["marker"]["gray"] = {
        "step": "initial",
        "num_markers": num_markers,
        "markers": markers,
        "image": image,
    }
    if num_markers != 1:
        logger.info(
            f"Initial marker detection found {num_markers}, entering path retry steps"
        )
        next_img = image
        marker_path = st.session_state.knobs["Marker"]["marker_detection_path"]["value"]
        for step in marker_path:
            logger.info(f"Retrying marker detection with step: {step}")
            step_fn = MARKER_DETECTION_STEPS.get(step)
            if step_fn is None:
                logger.warning(f"Step function not found for step: {step}")
                continue
            logger.info(f"Applying step function: {step}")
            next_img = step_fn(next_img)
            markers = detect_marker(next_img, detector)
            num_markers = len(markers) if markers else 0
            results["message"]["steps"]["marker"][step] = {
                "step": step,
                "num_markers": num_markers,
                "markers": markers,
                "image": next_img,
            }
            if num_markers == 1:
                logger.info(f"Marker found after step '{step}'")
                break

    if num_markers != 1:
        logger.info(f"Markers detected: {num_markers}")
        results["status"] = "failure"
    else:
        logger.info("Marker found")
        results["status"] = "success"
    results["message"]["num_markers"] = num_markers
    results["message"]["markers"] = markers
    logger.info(f"Marker detection results: {results}")
    return results


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


def build_winner(image, resulting_data):
    logger.info(f"Building image with resulting data: {resulting_data}")
    results = {"status": "unknown", "message": {}}
    scale = st.session_state.knobs["System"]["image_processing_scale"]["value"]
    marker_mm = st.session_state.knobs["System"]["image_processing_marker_size_mm"][
        "value"
    ]

    inv_scale = 1.0 / scale
    # Markers
    markers = resulting_data["info"]["markers"]
    color_marker_rgb_tuple = st.session_state.knobs["System"]["marker_color"]["value"]
    color_marker = hex_to_bgr(color_marker_rgb_tuple)
    logger.info(f"Marker color: {color_marker}")
    marker_line_thickness = st.session_state.knobs["System"]["marker_line_thickness"][
        "value"
    ]
    marker_center_color_rgb_tuple = st.session_state.knobs["System"][
        "marker_center_color"
    ]["value"]
    marker_center_color = hex_to_bgr(marker_center_color_rgb_tuple)
    logger.info(f"Marker center color: {marker_center_color}")
    marker_center_size = st.session_state.knobs["System"]["marker_center_size"]["value"]
    for marker in markers:
        scaled_corners = (marker.corners * inv_scale).astype(int)
        cv2.polylines(
            image, [scaled_corners], True, color_marker, marker_line_thickness
        )
        # Put a dot at the center
        cv2.circle(
            image,
            (int(marker.center[0] * inv_scale), int(marker.center[1] * inv_scale)),
            marker_center_size,
            marker_center_color,
            -1,
        )
    marker_side_length_px = np.linalg.norm(
        (inv_scale * marker.corners[0]) - (inv_scale * marker.corners[1])
    )
    px_per_mm = marker_side_length_px / marker_mm
    # Circles
    circles = resulting_data["info"]["circles"]
    color_circle_rgb_tuple = st.session_state.knobs["System"]["circle_color"]["value"]
    color_circle = hex_to_bgr(color_circle_rgb_tuple)
    circle_line_thickness = st.session_state.knobs["System"]["circle_line_thickness"][
        "value"
    ]
    circle_center_color_rgb_tuple = st.session_state.knobs["System"][
        "circle_center_color"
    ]["value"]
    circle_center_color = hex_to_bgr(circle_center_color_rgb_tuple)
    circle_center_size = st.session_state.knobs["System"]["circle_center_size"]["value"]
    x, y, r = np.round(circles[0, 0, :]).astype("int")
    x = int(x * inv_scale)
    y = int(y * inv_scale)
    r = int(r * inv_scale)
    cv2.circle(image, (x, y), r, color_circle, circle_line_thickness)
    cv2.circle(image, (x, y), circle_center_size, circle_center_color, -1)

    circle_center_xy = (x, y)
    marker_center_xy = (
        int(markers[0].center[0] * inv_scale),
        int(markers[0].center[1] * inv_scale),
    )

    dist_btw_circle_marker_px = np.linalg.norm(
        np.array(circle_center_xy) - np.array(marker_center_xy)
    )
    dist_btw_circle_marker_mm = dist_btw_circle_marker_px / px_per_mm

    logger.info(
        f"Distance between circle and marker: {dist_btw_circle_marker_px}px ({dist_btw_circle_marker_mm}mm)"
    )
    results["dist_btw_circle_marker_px"] = dist_btw_circle_marker_px
    results["dist_btw_circle_marker_mm"] = dist_btw_circle_marker_mm

    dist_btw_circle_marker_standard = st.session_state.knobs["System"][
        "dist_btw_circle_marker_standard"
    ]["value"]

    circle_radius = st.session_state.knobs["System"]["circle_radius"]["value"]
    # fudge_factor is the percentage to allow deviation from the standard distance
    fudge_factor = st.session_state.knobs["System"]["tolerence"]["value"]
    diff_mark_stand = abs(dist_btw_circle_marker_mm - dist_btw_circle_marker_standard)
    fud_m_s = dist_btw_circle_marker_standard * fudge_factor / 100
    if diff_mark_stand > fud_m_s:
        logger.warning("Distance between circle and marker is out of tolerance")
        results["status"] = "error"
        results["message"] = (
            f"Distance between circle and marker is out of tolerance: | "
            f"Detected distance: {dist_btw_circle_marker_mm:.2f}mm | "
            f"Defined distance: {dist_btw_circle_marker_standard}mm | "
            f"Difference: {diff_mark_stand:.2f} | "
            f"Max deviation: {fud_m_s:.2f}"
        )
    else:
        r_mm = r / px_per_mm
        diff_r_circ = abs(r_mm - circle_radius)
        fud_r_cir = circle_radius * fudge_factor / 100
        if diff_r_circ > fud_r_cir:
            logger.warning("Circle radius is out of tolerance")
            results["status"] = "error"
            results["message"] = (
                f"Circle radius is out of tolerance: |r: {r_mm} |c: {circle_radius} |d: {diff_r_circ} |f: {fud_r_cir}"
            )
        else:
            logger.info("Circle radius is within tolerance")
            results["status"] = "success"

    results["circle"] = {"radius": r, "radius_mm": r_mm, "center": (x, y)}
    results["marker"] = {
        "center": (
            int(markers[0].center[0] * inv_scale),
            int(markers[0].center[1] * inv_scale),
        )
    }
    lines_data = resulting_data["info"]["lines"]["message"]["lines"]["good_lines"]
    # lines
    for line in lines_data:
        x1, y1, x2, y2 = map(int, line)
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 25)
    return image, results


def hex_to_bgr(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    r, g, b = [int(hex_color[i : i + 2], 16) for i in (0, 2, 4)]
    return (b, g, r)


def get_lines(image, marker_center, circle_center, circle_radius):
    logger.info(
        f"Marker center: {marker_center}, Circle center: {circle_center}, Circle radius: {circle_radius}"
    )
    results = {
        "status": "unknown",
        "message": {
            "marker_center": None,
            "circle_center": None,
            "circle_radius": None,
            "fudge": None,
        },
        "image": {"lines": {}},
    }
    results["message"]["marker_center"] = marker_center
    results["message"]["circle_center"] = circle_center
    results["message"]["circle_radius"] = circle_radius
    working_image = image
    x, y, r = int(circle_center[0]), int(circle_center[1]), int(circle_radius)
    fudge = int(r * (st.session_state.knobs["System"]["tolerence"]["value"] / 100))
    results["message"]["fudge"] = fudge

    # Crop the image around the circle with a margin defined by the fudge factor

    h, w = working_image.shape[:2]
    x0 = max(0, x - r)
    y0 = max(0, y - r)
    x1 = min(w, x + r)
    y1 = min(h, y + r)
    cropped_image = working_image[y0:y1, x0:x1]

    # round the corners to remove some more.
    mask = np.zeros(cropped_image.shape[:2], dtype=np.uint8)
    cv2.circle(mask, (r, r), r, 255, -1)  # center is now (r,r) in the cropped space
    roi_masked = cv2.bitwise_and(cropped_image, cropped_image, mask=mask)
    results["image"]["lines"]["roi_masked"] = roi_masked

    canny_image = canny(roi_masked)
    results["image"]["lines"]["canny"] = canny_image

    lines = hough(canny_image)
    results["image"]["lines"]["hough"] = lines

    # Initialize the dictionary to hold line data
    results["message"]["lines"] = {
        "raw_lines": lines,
        "good_lines": [],
        "num_good_lines": 0,
    }

    if lines is None:
        results["status"] = "error"
        results["message"]["error"] = "No lines detected"
    else:
        results["status"] = "success"
        good_lines = []
        center = (r, r)

        for i in range(len(lines)):
            working_line = lines[i][0]
            if check_point(center, working_line, r):
                logger.info("Center is on the line")
                good_lines.append(working_line)
            logger.info(f"Processing line {working_line}")

        # Correctly assign to the dictionary keys
        results["message"]["lines"]["good_lines"] = good_lines
        results["message"]["lines"]["num_good_lines"] = len(good_lines)

    return results


def check_point(point, line, circle_radius):
    percent = st.session_state.knobs["System"]["tolerence"]["value"]
    x, y = point
    x1, y1, x2, y2 = line
    # Distance from point to infinite line through (x1,y1)-(x2,y2)
    num = abs((y2 - y1) * x - (x2 - x1) * y + x2 * y1 - y2 * x1)
    den = np.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
    if den == 0:
        return False
    tolerance = circle_radius * (percent / 100)
    return (num / den) <= tolerance


def hough(image):
    logger.info("Performing Hough transform")
    # Placeholder for Hough transform implementation
    rho = st.session_state.knobs["Hough Lines P"]["hlp_rho"]["value"]
    theta = st.session_state.knobs["Hough Lines P"]["hlp_theta"]["value"]
    threshold = st.session_state.knobs["Hough Lines P"]["hlp_threshold"]["value"]
    min_line_length = st.session_state.knobs["Hough Lines P"]["hlp_min_line_length"][
        "value"
    ]
    max_line_gap = st.session_state.knobs["Hough Lines P"]["hlp_max_line_gap"]["value"]
    lines = cv2.HoughLinesP(
        image,
        rho,
        theta / 180 * np.pi,
        threshold,
        minLineLength=min_line_length,
        maxLineGap=max_line_gap,
    )
    logger.info(f"Hough lines: {lines}")
    return lines
