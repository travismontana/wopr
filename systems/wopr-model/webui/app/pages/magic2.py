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


def apply_blur(img, method, params, is_gray):
    """Apply selected blur method. Returns blurred image."""
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


def apply_threshold(img, method, params, is_gray):
    """Apply selected threshold method. Returns thresholded image."""
    if method == "None":
        return img

    # Some threshold methods need grayscale input
    if not is_gray and img.ndim == 3:
        gray_input = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        gray_input = img

    if method == "Binary Threshold":
        _, result = cv2.threshold(gray_input, params["value"], 255, cv2.THRESH_BINARY)
        return result
    elif method == "Otsu's Threshold":
        _, result = cv2.threshold(
            gray_input, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return result
    elif method == "Adaptive Threshold":
        result = cv2.adaptiveThreshold(
            gray_input,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            params["block_size"],
            params["C"],
        )
        return result
    elif method == "InRange Threshold":
        result = cv2.inRange(gray_input, params["lower"], params["upper"])
        return result
    return img


def apply_edge(img, method, params):
    """Apply selected edge detection method. Returns edge image."""
    if method == "None":
        return img

    # Edge detection needs single-channel uint8
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    if img.dtype != np.uint8:
        img = cv2.convertScaleAbs(img)

    if method == "Canny":
        return cv2.Canny(img, params["thresh1"], params["thresh2"])
    elif method == "Sobel":
        k = params["kernel"]
        sx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=k)
        sy = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=k)
        return cv2.convertScaleAbs(cv2.magnitude(sx, sy))
    elif method == "Laplacian":
        return cv2.convertScaleAbs(cv2.Laplacian(img, cv2.CV_64F))
    return img


def render_pipeline(col, label, base_img, is_gray):
    """Render one side of the pipeline with controls and final image."""
    prefix = "gray" if is_gray else "rgb"

    with col:
        st.header(label)
        st.subheader("Result")
        st.image(img, caption=caption, use_container_width=True)
        # --- Blur ---
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

        img = apply_blur(base_img, blur_method, blur_params, is_gray)

        st.divider()

        # --- Threshold ---
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

        img = apply_threshold(img, thresh_method, thresh_params, is_gray)

        st.divider()

        # --- Edge Detection ---
        edge_method = st.selectbox(
            "Edge Detection",
            ["None", "Canny", "Sobel", "Laplacian"],
            key=f"{prefix}_edge",
        )
        edge_params = {}
        if edge_method == "Canny":
            edge_params["thresh1"] = st.slider(
                "Threshold 1", 0, 255, 100, key=f"{prefix}_canny_t1"
            )
            edge_params["thresh2"] = st.slider(
                "Threshold 2", 0, 255, 200, key=f"{prefix}_canny_t2"
            )
        elif edge_method == "Sobel":
            edge_params["kernel"] = st.slider(
                "Kernel Size", 1, 31, 5, step=2, key=f"{prefix}_sobel_k"
            )

        img = apply_edge(img, edge_method, edge_params)

        st.divider()

        # --- Final Result ---
        # Build a summary of what's applied
        steps = []
        if blur_method != "None":
            steps.append(blur_method)
        if thresh_method != "None":
            steps.append(thresh_method)
        if edge_method != "None":
            steps.append(edge_method)
        caption = " → ".join(steps) if steps else "Original"


# --- Layout ---
col_gray, col_rgb = st.columns(2)
render_pipeline(col_gray, "Gray", img_gray_u8, is_gray=True)
render_pipeline(col_rgb, "RGB", img_rgb_u8, is_gray=False)
