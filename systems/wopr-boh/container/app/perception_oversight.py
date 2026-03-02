import streamlit as st
import cv2
import time

from lib.image_processing import (
    process_frame,
    open_camera,
    start_process,
    build_winner,
    MARKER_DETECTION_STEPS,
    CIRCLE_DETECTION_STEPS,
)
import pandas as pd
from lib.helpers import setup_logger
from lib.helpers import wopr_json
logger = setup_logger()


st.title("Perception Oversight")
logger.info("starting out")

# Get the cameras
cameras = wopr_json["camera"]["camDict"]
logger.info(f"Camera configuration: {cameras}")
num_cameras = len(cameras)
num_cols = num_cameras + 1
logger.info(f"Number of cameras: {num_cameras}")

captures = {}
for i in range(num_cameras):
    camera = cameras[str(i)]
    try:
        captures[i] = open_camera(camera["host"], camera["port"])
    except Exception as e:
        logger.error(f"Failed to open camera {i}: {e}")

cols = st.columns(num_cols)
placeholders = [
    [cols[i].empty(), cols[i].empty(), cols[i].empty()] for i in range(num_cameras)
]


def loop():
    loop_start = time.time()
    for i, capture in captures.items():
        logger.info(f"Processing camera {i}")
        frames = capture.read()
        logger.info(f"Captured {len(frames)} frames from camera {i}")
        raw_placeholder, processed_placeholder, info_placeholder = placeholders[i]
        if frames:
            ranked_frames = start_process(frames)
        logger.info(f"Ranked frames: {ranked_frames}")
        top_frames = ranked_frames[
            : st.session_state.knobs["System"]["num_top_frames"]["value"]
        ]
        num_ranked_frames = len(ranked_frames)

        for frame_data in top_frames:
            image = frame_data["frame"]
            # Raw image
            raw_placeholder.image(image, channels="BGR")
            # Process the frames
            resulting_data = process_frame(image)
            # check if circle or marker not found and bail early
            num_markers = resulting_data["info"].get("num_markers", 0)
            num_circles = resulting_data["info"].get("num_circles", 0)
            if num_markers == 0 or num_circles == 0:
                logger.warning(
                    f"Camera {i}: No markers or circles detected, skipping frame"
                )
                continue
            processed_frame, process_results = build_winner(image, resulting_data)
            with processed_placeholder.container():
                st.image(processed_frame, channels="BGR")
            with info_placeholder.container():
                info = resulting_data["info"]
                if process_results["status"] == "success":
                    st.success("Processing successful")
                else:
                    st.warning(
                        f"Processing failed: {process_results.get('message', 'Unknown error')}"
                    )
                # ~~~~~~~~~~~~~~~~~~~ CHANGED: dict-driven table instead of manual st.text() ~~~~~~~~~~~~~~~~~~~
                table_data = {
                    "Metric": [
                        "Original Frame Size",
                        "Resized Frame Size",
                        "Marker Size (mm)",
                        "Marker Size (scaled mm)",
                        "Num Circles",
                        "Circle Center",
                        "Num Markers",
                        "Marker Center",
                    ],
                    "Value": [
                        f"{info.get('frame_shape', ['N/A','N/A'])[0]}x{info.get('frame_shape', ['N/A','N/A'])[1]}",
                        f"{info.get('resized_shape', ['N/A','N/A'])[0]}x{info.get('resized_shape', ['N/A','N/A'])[1]}",
                        info.get("marker_size_mm", "N/A"),
                        info.get("marker_scaled_mm", "N/A"),
                        info.get("num_circles", "N/A"),
                        (
                            str(info["circles"])
                            if info.get("circles") is not None
                            else "N/A"
                        ),
                        info.get("num_markers", "N/A"),
                        str(info["marker"][0].center) if info.get("marker") else "N/A",
                    ],
                }
                df = pd.DataFrame(table_data)
                df["Value"] = df["Value"].astype(
                    str
                )  # force homogeneous types for Arrow
                st.dataframe(df, hide_index=True, width="stretch")
                st.json(process_results, expanded=False)
                st.json(resulting_data["info"], expanded=False)


if "knobs" not in st.session_state:
    st.session_state.knobs = {}
    st.session_state.knobs = {
        "System": {
            "frames_to_process": {
                "key": "frames_to_process",
                "help": "Number of frames to process at a time",
                "default": 1,
                "min": 1,
                "max": 16,
                "type": "slider",
            },
            "num_top_frames": {
                "key": "num_top_frames",
                "help": "Number of top frames to select after processing",
                "default": 1,
                "min": 1,
                "max": 10,
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
            "tolerence": {
                "key": "tolerence",
                "help": "% fudge factor for image processing",
                "default": 10,
                "min": 1,
                "max": 100,
                "type": "slider",
            },
            "Laplacian to Tenengrad Ratio": {
                "key": "laplacian_to_tenengrad_ratio",
                "help": "Ratio of Laplacian to Tenengrad for image processing",
                "default": 70,
                "min": 1,
                "max": 100,
                "step": 1,
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
            "dist_btw_circle_marker_standard": {
                "key": "dist_btw_circle_marker_standard",
                "help": "Standard distance between circle and marker for image processing, in mm",
                "default": 160,
                "min": 1,
                "max": 1000,
                "type": "slider",
            },
            "circle_radius": {
                "key": "circle_radius",
                "help": "Radius of the circle for image processing",
                "default": 160,
                "min": 1,
                "max": 1000,
                "type": "slider",
            },
            "marker_color": {
                "key": "marker_color",
                "help": "Color of the marker for image processing",
                "default": "#00FFAA",
                "type": "color_picker",
            },
            "marker_line_thickness": {
                "key": "marker_line_thickness",
                "help": "Line thickness of the marker for image processing",
                "default": 2,
                "min": 1,
                "max": 10,
                "type": "slider",
            },
            "marker_center_color": {
                "key": "marker_center_color",
                "help": "Color of the marker center for image processing",
                "default": "#0000FF",
                "type": "color_picker",
            },
            "marker_center_size": {
                "key": "marker_center_size",
                "help": "Size of the marker center for image processing",
                "default": 5,
                "min": 1,
                "max": 20,
                "type": "slider",
            },
            "circle_color": {
                "key": "circle_color",
                "help": "Color of the circle for image processing",
                "default": "#FF0000",
                "type": "color_picker",
            },
            "circle_line_thickness": {
                "key": "circle_line_thickness",
                "help": "Line thickness of the circle for image processing",
                "default": 2,
                "min": 1,
                "max": 10,
                "type": "slider",
            },
            "circle_center_color": {
                "key": "circle_center_color",
                "help": "Color of the circle center for image processing",
                "default": "#00FF00",
                "type": "color_picker",
            },
            "circle_center_size": {
                "key": "circle_center_size",
                "help": "Size of the circle center for image processing",
                "default": 5,
                "min": 1,
                "max": 20,
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
    for group in st.session_state.knobs.values():
        for knob in group.values():
            knob["value"] = knob["default"]

# Controls Column
with cols[num_cols - 1]:
    st.subheader("Controls")
    if st.button("Grab Reality"):
        loop()
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
                elif knob_info["type"] == "color_picker":
                    knobs[knob_name]["value"] = st.color_picker(
                        label=f"{knob_info['help']}; default: {knob_info['default']}",
                        value=knob_info["default"],
                        key=knob_info["key"],
                    )
