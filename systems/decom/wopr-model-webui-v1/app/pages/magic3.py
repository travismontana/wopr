import streamlit as st
import numpy as np
import cv2

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
st.title("CV Pipeline")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_file is None:
    st.info("Upload an image to get started.")
    st.stop()

# Decode uploaded image
raw_bytes = uploaded_file.read()
raw_buf_u8 = np.frombuffer(raw_bytes, dtype=np.uint8)
img_bgr_u8 = cv2.imdecode(raw_buf_u8, cv2.IMREAD_COLOR)
img_gray_u8 = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2GRAY)
img_rgb_u8 = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2RGB)


# ---------------------------------------------------------------------------
# Processing functions
# ---------------------------------------------------------------------------


def ensure_gray_u8(img):
    """Guarantee single-channel uint8."""
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    if img.dtype != np.uint8:
        img = cv2.convertScaleAbs(img)
    return img


def apply_blur(img, method, params):
    if method == "None":
        return img
    elif method == "Median Blur":
        return cv2.medianBlur(img, params["kernel"])
    elif method == "Gaussian Blur":
        k = params["kernel"]
        return cv2.GaussianBlur(img, (k, k), 0)
    elif method == "Bilateral Filter":
        return cv2.bilateralFilter(
            img, params["diameter"], params["sigma_color"], params["sigma_space"]
        )
    return img


def apply_threshold(img, method, params):
    if method == "None":
        return img
    gray = ensure_gray_u8(img)
    if method == "Binary Threshold":
        _, result = cv2.threshold(gray, params["value"], 255, cv2.THRESH_BINARY)
        return result
    elif method == "Otsu's Threshold":
        _, result = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return result
    elif method == "Adaptive Threshold":
        return cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            params["block_size"],
            params["C"],
        )
    elif method == "InRange Threshold":
        return cv2.inRange(gray, params["lower"], params["upper"])
    return img


def apply_single_edge(img, method, params):
    """Apply one edge detection method."""
    gray = ensure_gray_u8(img)
    if method == "Canny":
        return cv2.Canny(gray, params["thresh1"], params["thresh2"])
    elif method == "Sobel":
        k = params["kernel"]
        sx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=k)
        sy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=k)
        return cv2.convertScaleAbs(cv2.magnitude(sx, sy))
    elif method == "Laplacian":
        return cv2.convertScaleAbs(cv2.Laplacian(gray, cv2.CV_64F))
    return img


def draw_find_stuff(img_pipeline, img_display, methods, params):
    """
    Run detection on img_pipeline, draw results onto img_display.
    img_display should be a color copy for drawing.
    Returns (annotated_image, results_text list).
    """
    out = img_display.copy()
    gray = ensure_gray_u8(img_pipeline)
    results = []

    if "Contours" in methods:
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(out, contours, -1, (0, 255, 0), 2)
        results.append(f"Contours: {len(contours)}")

    if "Hough Lines" in methods:
        p = params["hough_lines"]
        lines = cv2.HoughLines(gray, p["rho"], np.radians(p["theta"]), p["threshold"])
        if lines is not None:
            for line in lines:
                rho, theta = line[0]
                a, b = np.cos(theta), np.sin(theta)
                x0, y0 = a * rho, b * rho
                pt1 = (int(x0 + 2000 * (-b)), int(y0 + 2000 * a))
                pt2 = (int(x0 - 2000 * (-b)), int(y0 - 2000 * a))
                cv2.line(out, pt1, pt2, (255, 0, 0), 2)
            results.append(f"Hough Lines: {len(lines)}")
        else:
            results.append("Hough Lines: 0")

    if "Hough Circles" in methods:
        p = params["hough_circles"]
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            p["dp"],
            p["min_dist"],
            param1=p["param1"],
            param2=p["param2"],
            minRadius=p["min_radius"],
            maxRadius=p["max_radius"],
        )
        if circles is not None:
            circles_rounded = np.uint16(np.around(circles))
            for c in circles_rounded[0, :]:
                cv2.circle(out, (c[0], c[1]), c[2], (0, 0, 255), 2)
                cv2.circle(out, (c[0], c[1]), 2, (0, 0, 255), 3)
            results.append(f"Hough Circles: {circles.shape[1]}")
        else:
            results.append("Hough Circles: 0")

    if "Chessboard Corners" in methods:
        p = params["chessboard"]
        size = p["pattern_size"]
        ret, corners = cv2.findChessboardCorners(gray, (size, size), None)
        if ret:
            cv2.drawChessboardCorners(out, (size, size), corners, ret)
            results.append(f"Chessboard: found ({size}x{size})")
        else:
            results.append("Chessboard: not found")

    return out, results


# ---------------------------------------------------------------------------
# UI for one pipeline column
# ---------------------------------------------------------------------------


def render_pipeline(col, label, base_img, is_gray, result_container):
    """Render controls in col, final image in result_container."""
    prefix = "gray" if is_gray else "rgb"

    with col:
        st.header(label)

        # ---- Blur ----
        blur_method = st.selectbox(
            "Blur",
            ["None", "Median Blur", "Gaussian Blur", "Bilateral Filter"],
            key=f"{prefix}_blur",
        )
        blur_params = {}
        if blur_method in ("Median Blur", "Gaussian Blur"):
            blur_params["kernel"] = st.slider(
                "Kernel Size", 1, 31, 9, step=2, key=f"{prefix}_blur_k"
            )
        elif blur_method == "Bilateral Filter":
            blur_params["diameter"] = st.slider(
                "Diameter", 1, 31, 9, step=2, key=f"{prefix}_bf_d"
            )
            blur_params["sigma_color"] = st.slider(
                "Sigma Color", 1, 255, 75, key=f"{prefix}_bf_sc"
            )
            blur_params["sigma_space"] = st.slider(
                "Sigma Space", 1, 255, 75, key=f"{prefix}_bf_ss"
            )

        img = apply_blur(base_img, blur_method, blur_params)
        st.divider()

        # ---- Threshold ----
        thresh_method = st.selectbox(
            "Threshold",
            [
                "None",
                "Binary Threshold",
                "Otsu's Threshold",
                "Adaptive Threshold",
                "InRange Threshold",
            ],
            key=f"{prefix}_thresh",
        )
        thresh_params = {}
        if thresh_method == "Binary Threshold":
            thresh_params["value"] = st.slider(
                "Threshold Value", 0, 255, 127, key=f"{prefix}_thresh_v"
            )
        elif thresh_method == "Adaptive Threshold":
            thresh_params["block_size"] = st.slider(
                "Block Size", 3, 31, 11, step=2, key=f"{prefix}_at_bs"
            )
            thresh_params["C"] = st.slider("C", -50, 50, 2, key=f"{prefix}_at_c")
        elif thresh_method == "InRange Threshold":
            thresh_params["lower"] = st.slider(
                "Lower", 0, 255, 100, key=f"{prefix}_ir_lo"
            )
            thresh_params["upper"] = st.slider(
                "Upper", 0, 255, 200, key=f"{prefix}_ir_hi"
            )

        img = apply_threshold(img, thresh_method, thresh_params)
        st.divider()

        # ---- Edge Detection Chain ----
        st.subheader("Edge Detection Chain")
        st.caption(
            "Selection order = processing order. Output of each feeds into the next."
        )

        edge_methods = ["Canny", "Sobel", "Laplacian"]
        selected_edges = st.multiselect(
            "Edge Detectors (ordered)",
            edge_methods,
            key=f"{prefix}_edge_chain",
        )

        # Collect params per selected edge detector
        edge_params_list = []
        for i, method in enumerate(selected_edges):
            st.markdown(f"**Step {i + 1}: {method}**")
            params = {}
            if method == "Canny":
                c1, c2 = st.columns(2)
                with c1:
                    params["thresh1"] = st.slider(
                        "Thresh 1", 0, 255, 100, key=f"{prefix}_canny_t1_{i}"
                    )
                with c2:
                    params["thresh2"] = st.slider(
                        "Thresh 2", 0, 255, 200, key=f"{prefix}_canny_t2_{i}"
                    )
            elif method == "Sobel":
                params["kernel"] = st.slider(
                    "Kernel Size", 1, 31, 5, step=2, key=f"{prefix}_sobel_k_{i}"
                )
            # Laplacian: no params
            edge_params_list.append((method, params))

        # Apply edge chain sequentially
        for method, params in edge_params_list:
            img = apply_single_edge(img, method, params)

        st.divider()

        # ---- Find Stuff ----
        st.subheader("Find Stuff")
        find_options = [
            "Contours",
            "Hough Lines",
            "Hough Circles",
            "Chessboard Corners",
        ]
        selected_finds = st.multiselect("Detectors", find_options, key=f"{prefix}_find")

        find_params = {}

        if "Hough Lines" in selected_finds:
            st.markdown("**Hough Lines**")
            hl_c1, hl_c2, hl_c3 = st.columns(3)
            with hl_c1:
                hl_rho = st.slider("Rho", 1, 10, 1, key=f"{prefix}_hl_rho")
            with hl_c2:
                hl_theta = st.slider("Theta (°)", 1, 180, 1, key=f"{prefix}_hl_theta")
            with hl_c3:
                hl_thresh = st.slider(
                    "Threshold", 1, 500, 100, key=f"{prefix}_hl_thresh"
                )
            find_params["hough_lines"] = {
                "rho": hl_rho,
                "theta": hl_theta,
                "threshold": hl_thresh,
            }

        if "Hough Circles" in selected_finds:
            st.markdown("**Hough Circles**")
            hc_c1, hc_c2 = st.columns(2)
            with hc_c1:
                hc_dp = st.slider("DP", 1, 10, 1, key=f"{prefix}_hc_dp")
                hc_min_dist = st.slider("Min Dist", 1, 500, 20, key=f"{prefix}_hc_md")
                hc_p1 = st.slider("Param1", 1, 500, 100, key=f"{prefix}_hc_p1")
            with hc_c2:
                hc_p2 = st.slider("Param2", 1, 500, 100, key=f"{prefix}_hc_p2")
                hc_min_r = st.slider("Min Radius", 0, 500, 0, key=f"{prefix}_hc_minr")
                hc_max_r = st.slider("Max Radius", 0, 500, 0, key=f"{prefix}_hc_maxr")
            find_params["hough_circles"] = {
                "dp": hc_dp,
                "min_dist": hc_min_dist,
                "param1": hc_p1,
                "param2": hc_p2,
                "min_radius": hc_min_r,
                "max_radius": hc_max_r,
            }

        if "Chessboard Corners" in selected_finds:
            st.markdown("**Chessboard Corners**")
            find_params["chessboard"] = {
                "pattern_size": st.slider(
                    "Pattern Size", 1, 20, 7, key=f"{prefix}_cb_ps"
                )
            }

        # ---- Build final display ----
        pipeline_img = img

        # Caption: pipeline steps
        steps = []
        if blur_method != "None":
            steps.append(blur_method)
        if thresh_method != "None":
            steps.append(thresh_method)
        for method, _ in edge_params_list:
            steps.append(method)

        if selected_finds:
            # Draw detections on color copy of original so overlays are visible
            display_base = (
                img_rgb_u8.copy()
                if not is_gray
                else cv2.cvtColor(img_gray_u8, cv2.COLOR_GRAY2RGB)
            )
            annotated, find_results = draw_find_stuff(
                pipeline_img, display_base, selected_finds, find_params
            )
            steps.extend([f"[{f}]" for f in selected_finds])
            caption = f"{label}: " + (" → ".join(steps) if steps else "Original")

            with result_container.container():
                tab_pipeline, tab_annotated = st.tabs(["Pipeline", "Detections"])
                with tab_pipeline:
                    st.image(pipeline_img, caption=caption, use_container_width=True)
                with tab_annotated:
                    st.image(
                        annotated,
                        caption=f"{label}: Detections",
                        use_container_width=True,
                    )
                    for r in find_results:
                        st.text(r)
        else:
            caption = f"{label}: " + (" → ".join(steps) if steps else "Original")
            result_container.image(
                pipeline_img, caption=caption, use_container_width=True
            )


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

st.subheader("Result")
result_col_gray, result_col_rgb = st.columns(2)
gray_result_container = result_col_gray.empty()
rgb_result_container = result_col_rgb.empty()

col_gray, col_rgb = st.columns(2)
render_pipeline(
    col_gray, "Gray", img_gray_u8, is_gray=True, result_container=gray_result_container
)
render_pipeline(
    col_rgb, "RGB", img_rgb_u8, is_gray=False, result_container=rgb_result_container
)
