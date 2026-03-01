import streamlit as st
import cv2
import time

from lib.image_processing import (
    process_frame,
    open_camera,
    MARKER_DETECTION_STEPS,
    CIRCLE_DETECTION_STEPS,
)

from lib.helpers import setup_logger
from lib.helpers import wopr_json
logger = setup_logger()


st.title("Perception Oversight")

# Get the cameras
cameras = wopr_json["camera"]["camDict"]
num_cameras = len(cameras)
num_cols = num_cameras + 1
logger.info(f"Number of cameras: {num_cameras}")

cols = st.columns(num_cols)
placeholders = [[cols[i].empty(), cols[i].empty(), cols[i].empty()] for i in range(num_cameras)]

if "knobs" not in st.session_state:
    st.session_state.knobs = {}
    st.session_state.knobs = {
        "System": {
            "stream_snap": {
                "key": "stream_snap",
                "help": "Stream or Snapshot (False is snapshot, True is stream)",
                "default": False,
                "type": "checkbox",
            },
            "target_fps": {
                "key": "target_fps",
                "help": "Target frames per second for the video stream",
                "default": 1,
                "min": 1,
                "max": 6,
                "type": "slider",
            },
            "frames_to_process": {
                "key": "frames_to_process",
                "help": "Number of frames to process at a time",
                "default": 1,
                "min": 1,
                "max": 100,
                "type": "slider",
            },
            "image_processing_scale": {
                "key": "img_proc_scale",
                "help": "Scale factor for image processing",
                "default": 0.25,
                "min": 0.1,
                "max": 5.0,
                "type": "slider",
            },
            "image_processing_marker_size_mm": {
                "key": "img_proc_marker_size_mm",
                "help": "Marker size in millimeters for image processing",
                "default": 35,
                "min": 1,
                "max": 100,
                "type": "slider",
            },
        },
        "Hough Circles": {
            "hg_circles_dp": {
                "group": "Hough Circles",
                "key": "hg_circles_dp",
                "help": "Hough Circles DP - (width of the histogram bars) Inverse ratio of the accumulator resolution to the image resolution",
                "default": 1,
                "min": 1,
                "max": 10,
                "type": "slider",
            },
            "hg_circles_param1": {
                "group": "Hough Circles",
                "key": "hg_circles_param1",
                "help": "Hough Circles Param1 - How strong the edge has to be, higher values mean stronger edges",
                "default": 50,
                "min": 1,
                "max": 500,
                "type": "slider",
            },
            "hg_circles_param2": {
                "group": "Hough Circles",
                "key": "hg_circles_param2",
                "help": "Hough Circles Param2 - if not ALT, confidence level 0-circumfrence in pixels, if ALT, roundness, 0-1, .8-.95 normal",
                "default": 30,
                "min": 1,
                "max": 500,
                "type": "slider",
            },
            "hg_circles_minRadius": {
                "group": "Hough Circles",
                "key": "hg_circles_minRadius",
                "help": "Hough Circles Min Radius Ratio - not the actual hg curcles minRadius, this is the ratio relative to the image height",
                "default": 5,
                "min": 1,
                "max": 32,
                "type": "slider",
            },
            "hg_circles_maxRadius": {
                "group": "Hough Circles",
                "key": "hg_circles_maxRadius",
                "help": "Hough Circles Max Radius Ratio - not the actual hg curcles maxRadius, this is the ratio relative to the image height",
                "default": 2,
                "min": 1,
                "max": 32,
                "type": "slider",
            },
            "hg_circles_path": {
                "group": "Hough Circles",
                "key": "hg_circles_path",
                "help": "Path for Hough circle detection",
                "default": list(CIRCLE_DETECTION_STEPS.keys()),
                "options": list(CIRCLE_DETECTION_STEPS.keys()),
                "type": "multiselect",
            },
        },
        "Marker": {
            "nthreads": {
                "group": "Marker",
                "key": "nthreads",
                "help": "Number of threads for marker detection",
                "default": 4,
                "min": 1,
                "max": 16,
                "type": "slider",
            },
            "quad_decimate": {
                "group": "Marker",
                "key": "quad_decimate",
                "help": "Decimation factor for marker detection",
                "default": 1.0,
                "min": 0.1,
                "max": 2.0,
                "type": "slider",
            },
            "quad_sigma": {
                "group": "Marker",
                "key": "quad_sigma",
                "help": "Sigma value for marker detection",
                "default": 0.8,
                "min": 0.1,
                "max": 2.0,
                "type": "slider",
            },
            "quad_refine_edges": {
                "group": "Marker",
                "key": "quad_refine_edges",
                "help": "Refine edges for marker detection",
                "default": True,
                "min": 0,
                "max": 1,
                "type": "slider",
            },
            "marker_type": {
                "group": "Marker",
                "key": "marker_type",
                "help": "Type of marker",
                "default": "tag36h11",
                "options": ["tag36h11", "tag36h10"],
                "type": "selectbox",
            },
            "marker_detection_path": {
                "group": "Marker",
                "key": "marker_detection_path",
                "help": "Path for marker detection",
                "default": list(MARKER_DETECTION_STEPS.keys()),
                "options": list(MARKER_DETECTION_STEPS.keys()),
                "type": "multiselect",
            },
            "min_decision_margin": {
                "group": "Marker",
                "key": "min_decision_margin",
                "help": "Minimum decision margin for marker detection",
                "default": 20.0,
                "min": 0.0,
                "max": 100.0,
                "type": "slider",
            },
        },
        "Canny": {
            "canny_threshold1": {
                "group": "Canny",
                "key": "canny_threshold1",
                "help": "Canny edge detection threshold1",
                "default": 100,
                "min": 0,
                "max": 255,
                "type": "slider",
            },
            "canny_threshold2": {
                "group": "Canny",
                "key": "canny_threshold2",
                "help": "Canny edge detection threshold2",
                "default": 200,
                "min": 0,
                "max": 255,
                "type": "slider",
            },
        },
    }

# Controls Column
with cols[num_cols - 1]:
    st.subheader("Controls")
    # each knob has a group that it needs to be sorted by
    for group, knobs in st.session_state.knobs.items():
        with st.expander(group):
            for knob_name, knob_info in knobs.items():
                if knob_info["type"] == "slider":
                    knobs[knob_name]["value"] = st.slider(
                        label=f"{knob_info['help']}; default: {knob_info['default']}",
                        min_value=knob_info["min"],
                        max_value=knob_info["max"],
                        value=knob_info["default"],
                        key=knob_info["key"],
                    )
                elif knob_info["type"] == "selectbox":
                    knobs[knob_name]["value"] = st.selectbox(
                        label=f"{knob_info['help']}; default: {knob_info['default']}",
                        options=knob_info["options"],
                        index=knob_info["options"].index(knob_info["default"]),
                        key=knob_info["key"],
                    )
                elif knob_info["type"] == "multiselect":
                    knobs[knob_name]["value"] = st.multiselect(
                        label=f"{knob_info['help']}; default: {knob_info['default']}",
                        options=knob_info["options"],
                        default=knob_info["default"],
                        key=knob_info["key"],
                    )
                elif knob_info["type"] == "checkbox":
                    knobs[knob_name]["value"] = st.checkbox(
                        label=f"{knob_info['help']}; default: {knob_info['default']}",
                        value=knob_info["default"],
                        key=knob_info["key"],
                    )

captures = {}
for i in range(num_cameras):
    camera = cameras[str(i)]
    try:
        captures[i] = open_camera(camera['host'], camera['port'])
    except Exception as e:
        logger.error(f"Failed to open camera {i}: {e}")


while True:
    loop_start = time.time()
    for i,capture in captures.items():
        ret, frame = capture.read()

        raw_placeholder, processed_placeholder, info_placeholder = placeholders[i]

        if ret:
            raw_placeholder.image(frame, channels="BGR")
        else:
            raw_placeholder.text("Camera disconnected")
            continue

        resulting_data = process_frame(frame)
        logger.info(f"Received: {resulting_data}")

        if "status" in resulting_data and resulting_data["status"] == "failed":
            processed_placeholder.text(f"Message: {resulting_data.get('message', 'No message')}")
            logger.info(f"Camera {i} frame process return: status: failed")
            logger.info(f"Camera {i} frame process return: message: {resulting_data.get('message', 'No message')}")
        else:
            processed_placeholder.image(
                resulting_data["image"]["resulting_image"], channels="BGR"
            )

        if "info" in resulting_data:
            logger.info(f"Camera {i} info: {resulting_data['info']}")
            with info_placeholder.container():
                st.text("info:") 
                frame_shape_x = resulting_data["info"]["frame_shape"][0] if "frame_shape" in resulting_data["info"] else "N/A"
                frame_shape_y = resulting_data["info"]["frame_shape"][1] if "frame_shape" in resulting_data["info"] else "N/A"
                resized_shape_x = resulting_data["info"]["resized_shape"][0] if "resized_shape" in resulting_data["info"] else "N/A"
                resized_shape_y = resulting_data["info"]["resized_shape"][1] if "resized_shape" in resulting_data["info"] else "N/A"
                marker_size_org_mm = resulting_data["info"]["marker_size_mm"] if "marker_size_mm" in resulting_data["info"] else "N/A"
                marker_size_scaled_mm = resulting_data["info"]["marker_scaled_mm"] if "marker_scaled_mm" in resulting_data["info"] else "N/A"
                num_circles = resulting_data["info"]["num_circles"] if "num_circles" in resulting_data["info"] else "N/A"
                circle_center = resulting_data["info"]["circles"][0][:2] if "circles" in resulting_data["info"] and resulting_data["info"]["circles"] is not None else "N/A"
                num_marker = resulting_data["info"]["num_markers"] if "num_markers" in resulting_data["info"] else "N/A"
                marker_center = resulting_data["info"]["marker"][0].center if "marker" in resulting_data["info"] and resulting_data["info"]["marker"] else "N/A"
                
                st.text(f"Original Frame Size: {frame_shape_x}x{frame_shape_y}")
                st.text(f"Resized Frame Size: {resized_shape_x}x{resized_shape_y}")
                st.text(f"Marker Size (mm): {marker_size_org_mm}")
                st.text(f"Marker Size (scaled mm): {marker_size_scaled_mm}")
                st.text(f"Number of Circles: {num_circles}")
                st.text(f"Circle Center: {circle_center}")
                st.text(f"Number of Markers: {num_marker}")
                st.text(f"Marker Center: {marker_center}")
                st.json(resulting_data["info"], expanded=False)

    target_fps = st.session_state.knobs["System"]["target_fps"]["value"]
    elapsed = time.time() - loop_start
    sleep_time = max(0, 1 / target_fps - elapsed)
    time.sleep(sleep_time)
