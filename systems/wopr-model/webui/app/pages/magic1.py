import streamlit as st
import numpy as np
import cv2


def find_lines(center, corners, circle_dist, tol=10.0):
    radials = {}

    for corner in corners:
        dx = corner[0] - center[0]
        dy = corner[1] - center[1]
        angle = np.degrees(np.arctan2(dy, dx)) % 360
        dist = np.hypot(dx, dy)
        angle_rounded = round(angle / tol) * tol
        if angle_rounded not in radials:
            radials[angle_rounded] = []
        radials[angle_rounded].append((corner, dist))
    lines = []
    lines = {angle: corners for angle, corners in radials.items() if len(corners) >= 3}
    return lines


st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.title("Magic 1, ")
gray_selected_blur = "Median Blur"
rgb_selected_blur = "Median Blur"
# need a picture to work with.
# let's ask the user to give us one.
uploaded_file = st.file_uploader(
    "Choose a picture to work with", type=["jpg", "jpeg", "png"]
)
if uploaded_file is not None:
    raw_bytes = uploaded_file.read()
    raw_buf_u8 = np.frombuffer(raw_bytes, dtype=np.uint8)
    img_bgr_u8 = cv2.imdecode(raw_buf_u8, cv2.IMREAD_COLOR)

    img_gray_u8 = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2GRAY)
    img_rgb_u8 = cv2.cvtColor(img_bgr_u8, cv2.COLOR_BGR2RGB)

    with st.expander(
        f"Blurs - Gray: {gray_selected_blur} - RGB: {rgb_selected_blur}", expanded=False
    ):
        col_gray, col_rgb = st.columns(2)
        with col_gray:
            st.header("Gray")
            # Selectbox button to select which blur to use in the next steps
            blur_options = ["Gaussian Blur", "Median Blur", "Bilateral Filter"]
            gray_selected_blur = st.selectbox(
                "Select Blur for Next Steps",
                options=blur_options,
                key="gray_blur_select",
            )

            # Median Blue - Gray
            imgu8_mbk = st.slider(
                "Median Blur Kernel Size",
                min_value=1,
                max_value=31,
                value=9,
                step=2,
                key="gray_mbk",
            )
            img_medBlur_gray_u8 = cv2.medianBlur(img_gray_u8, imgu8_mbk)
            st.image(img_medBlur_gray_u8, caption=f"Median Blur {imgu8_mbk}")

            # Gaussian Blur - Gray
            imgu8_gbk = st.slider(
                "Gaussian Blur Kernel Size",
                min_value=1,
                max_value=31,
                value=9,
                step=2,
                key="gray_gbk",
            )
            img_gauBlur_gray_u8 = cv2.GaussianBlur(
                img_gray_u8, (imgu8_gbk, imgu8_gbk), 0
            )
            st.image(img_gauBlur_gray_u8, caption=f"Gaussian Blur {imgu8_gbk}")

            # bilateralFilter - Gray
            imgu8_bf_d = st.slider(
                "Bilateral Filter Diameter",
                min_value=1,
                max_value=31,
                value=9,
                step=2,
                key="gray_bf_d",
            )
            imgu8_bf_sigmaColor = st.slider(
                "Bilateral Filter Sigma Color",
                min_value=1,
                max_value=255,
                value=75,
                step=1,
                key="gray_bf_sc",
            )
            imgu8_bf_sigmaSpace = st.slider(
                "Bilateral Filter Sigma Space",
                min_value=1,
                max_value=255,
                value=75,
                step=1,
                key="gray_bf_ss",
            )
            img_bilateralFilter_gray_u8 = cv2.bilateralFilter(
                img_gray_u8,
                imgu8_bf_d,
                imgu8_bf_sigmaColor,
                imgu8_bf_sigmaSpace,
            )
            st.image(
                img_bilateralFilter_gray_u8,
                caption=f"Bilateral Filter d={imgu8_bf_d} sc={imgu8_bf_sigmaColor} ss={imgu8_bf_sigmaSpace}",
            )

        with col_rgb:
            st.header("RGB")
            rgb_blur_options = ["Gaussian Blur", "Median Blur", "Bilateral Filter"]
            rgb_selected_blur = st.selectbox(
                "Select Blur for Next Steps",
                options=rgb_blur_options,
                key="rgb_blur_select",
            )

            # Median Blur - RGB
            imrgb_mbk = st.slider(
                "Median Blur Kernel Size",
                min_value=1,
                max_value=31,
                value=9,
                step=2,
                key="rgb_mbk",
            )
            img_medBlur_rgb_u8 = cv2.medianBlur(img_rgb_u8, imrgb_mbk)
            st.image(img_medBlur_rgb_u8, caption=f"Median Blur {imrgb_mbk}")

            # Gaussian Blur - RGB
            imrgb_gbk = st.slider(
                "Gaussian Blur Kernel Size",
                min_value=1,
                max_value=31,
                value=9,
                step=2,
                key="rgb_gbk",
            )
            img_gauBlur_rgb_u8 = cv2.GaussianBlur(img_rgb_u8, (imrgb_gbk, imrgb_gbk), 0)
            st.image(img_gauBlur_rgb_u8, caption=f"Gaussian Blur {imrgb_gbk}")

            # bilateralFilter - RGB
            imrgb_bf_d = st.slider(
                "Bilateral Filter Diameter",
                min_value=1,
                max_value=31,
                value=9,
                step=2,
                key="rgb_bf_d",
            )
            imrgb_bf_sigmaColor = st.slider(
                "Bilateral Filter Sigma Color",
                min_value=1,
                max_value=255,
                value=75,
                step=1,
                key="rgb_bf_sc",
            )
            imrgb_bf_sigmaSpace = st.slider(
                "Bilateral Filter Sigma Space",
                min_value=1,
                max_value=255,
                value=75,
                step=1,
                key="rgb_bf_ss",
            )
            img_bilateralFilter_rgb_u8 = cv2.bilateralFilter(
                img_rgb_u8,
                imrgb_bf_d,
                imrgb_bf_sigmaColor,
                imrgb_bf_sigmaSpace,
            )
            st.image(
                img_bilateralFilter_rgb_u8,
                caption=f"Bilateral Filter d={imrgb_bf_d} sc={imrgb_bf_sigmaColor} ss={imrgb_bf_sigmaSpace}",
            )
    match gray_selected_blur:
        case "Gaussian Blur":
            img_blur_gray_u8 = img_gauBlur_gray_u8
        case "Median Blur":
            img_blur_gray_u8 = img_medBlur_gray_u8
        case "Bilateral Filter":
            img_blur_gray_u8 = img_bilateralFilter_gray_u8
    match rgb_selected_blur:
        case "Gaussian Blur":
            img_blur_rgb_u8 = img_gauBlur_rgb_u8
        case "Median Blur":
            img_blur_rgb_u8 = img_medBlur_rgb_u8
        case "Bilateral Filter":
            img_blur_rgb_u8 = img_bilateralFilter_rgb_u8

    with st.expander("Thresholding", expanded=False):
        st.write(
            "Thresholding is a technique used to segment an image by converting it into a binary image based on a specified threshold value."
        )
        col_thres_gray, col_thres_rgb = st.columns(2)

        with col_thres_gray:
            st.header("Gray")

            # Select box none, threshold, threshold - otsu, adaptive
            selectbox_thres_options = [
                "None",
                "Threshold",
                "Otsu's Threshold",
                "Adaptive Threshold",
                "InRange Threshold",
            ]
            selected_thres_option_gray = st.selectbox(
                "Select Thresholding Method",
                options=selectbox_thres_options,
                key="thres_select_gray",
            )
            # Thresholding - Gray
            imgu8_thres = st.slider(
                "Threshold Value",
                min_value=0,
                max_value=255,
                value=127,
                step=1,
                key="thres",
            )
            _, img_thresh_gray_u8 = cv2.threshold(
                img_blur_gray_u8, imgu8_thres, 255, cv2.THRESH_BINARY
            )
            st.image(
                img_thresh_gray_u8, caption=f"Thresholding with value {imgu8_thres}"
            )

            # Thresholding - Otsu's Method - Gray
            _, img_otsu_gray_u8 = cv2.threshold(
                img_blur_gray_u8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            st.image(img_otsu_gray_u8, caption="Otsu's Thresholding")

            # Adaptive Thresholding - Gray
            imgu8_adap_thres_block_size = st.slider(
                "Adaptive Threshold Block Size",
                min_value=3,
                max_value=31,
                value=11,
                step=2,
                key="adap_thres_block_size",
            )
            imgu8_adap_thres_C = st.slider(
                "Adaptive Threshold C",
                min_value=-50,
                max_value=50,
                value=2,
                step=1,
                key="adap_thres_C",
            )
            img_adap_thresh_gray_u8 = cv2.adaptiveThreshold(
                img_blur_gray_u8,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                imgu8_adap_thres_block_size,
                imgu8_adap_thres_C,
            )
            st.image(
                img_adap_thresh_gray_u8,
                caption=f"Adaptive Thresholding with block size {imgu8_adap_thres_block_size} and C {imgu8_adap_thres_C}",
            )

            # inRange Thresholding - Gray
            imgu8_inrange_thres_lower = st.slider(
                "InRange Threshold Lower",
                min_value=0,
                max_value=255,
                value=100,
                step=1,
                key="inrange_thres_lower",
            )
            imgu8_inrange_thres_upper = st.slider(
                "InRange Threshold Upper",
                min_value=0,
                max_value=255,
                value=200,
                step=1,
                key="inrange_thres_upper",
            )
            img_inrange_thresh_gray_u8 = cv2.inRange(
                img_blur_gray_u8, imgu8_inrange_thres_lower, imgu8_inrange_thres_upper
            )
            st.image(
                img_inrange_thresh_gray_u8,
                caption=f"InRange Thresholding with lower {imgu8_inrange_thres_lower} and upper {imgu8_inrange_thres_upper}",
            )

            match selected_thres_option_gray:
                case "None":
                    img_thresh_gray_u8 = img_blur_gray_u8
                case "Threshold":
                    img_thresh_gray_u8 = img_thresh_gray_u8
                case "Otsu's Threshold":
                    img_thresh_gray_u8 = img_otsu_gray_u8
                case "Adaptive Threshold":
                    img_thresh_gray_u8 = img_adap_thresh_gray_u8
                case "InRange Threshold":
                    img_thresh_gray_u8 = img_inrange_thresh_gray_u8
                case _:
                    img_thresh_gray_u8 = img_blur_gray_u8

        with col_thres_rgb:
            st.header("RGB")

            # Select box none, threshold, threshold - otsu, adaptive
            selectbox_thres_options_rgb = [
                "None",
                "Threshold",
                "Otsu's Threshold",
                "Adaptive Threshold",
                "InRange Threshold",
            ]
            selected_thres_option_rgb = st.selectbox(
                "Select Thresholding Method",
                options=selectbox_thres_options_rgb,
                key="thres_select_rgb",
            )
            # Thresholding - RGB
            imrgb_thres = st.slider(
                "Threshold Value",
                min_value=0,
                max_value=255,
                value=127,
                step=1,
                key="thres_rgb",
            )
            _, img_thresh_rgb_u8 = cv2.threshold(
                img_blur_rgb_u8, imrgb_thres, 255, cv2.THRESH_BINARY
            )
            st.image(
                img_thresh_rgb_u8, caption=f"Thresholding with value {imrgb_thres}"
            )

            # Thresholding - Otsu's Method - RGB
            img_blur_rgb_gray_u8_temp = cv2.cvtColor(
                img_blur_rgb_u8, cv2.COLOR_RGB2GRAY
            )
            _, img_otsu_rgb_u8 = cv2.threshold(
                img_blur_rgb_gray_u8_temp, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
            st.image(img_otsu_rgb_u8, caption="Otsu's Thresholding")

            # Adaptive Thresholding - RGB
            imrgb_adap_thres_block_size = st.slider(
                "Adaptive Threshold Block Size",
                min_value=3,
                max_value=31,
                value=11,
                step=2,
                key="adap_thres_block_size_rgb",
            )
            imrgb_adap_thres_C = st.slider(
                "Adaptive Threshold C",
                min_value=-50,
                max_value=50,
                value=2,
                step=1,
                key="adap_thres_C_rgb",
            )
            img_adap_thresh_rgb_u8 = cv2.adaptiveThreshold(
                img_blur_rgb_gray_u8_temp,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                imrgb_adap_thres_block_size,
                imrgb_adap_thres_C,
            )
            st.image(
                img_adap_thresh_rgb_u8,
                caption=f"Adaptive Thresholding with block size {imrgb_adap_thres_block_size} and C {imrgb_adap_thres_C}",
            )

            # inRange Thresholding - RGB
            imrgb_inrange_thres_lower = st.slider(
                "InRange Threshold Lower",
                min_value=0,
                max_value=255,
                value=100,
                step=1,
                key="inrange_thres_lower_rgb",
            )
            imrgb_inrange_thres_upper = st.slider(
                "InRange Threshold Upper",
                min_value=0,
                max_value=255,
                value=200,
                step=1,
                key="inrange_thres_upper_rgb",
            )
            img_inrange_thresh_rgb_u8 = cv2.inRange(
                img_blur_rgb_u8, imrgb_inrange_thres_lower, imrgb_inrange_thres_upper
            )
            st.image(
                img_inrange_thresh_rgb_u8,
                caption=f"InRange Thresholding with lower {imrgb_inrange_thres_lower} and upper {imrgb_inrange_thres_upper}",
            )
            match selected_thres_option_rgb:
                case "None":
                    img_thresh_rgb_u8 = img_blur_rgb_u8
                case "Threshold":
                    img_thresh_rgb_u8 = img_thresh_rgb_u8
                case "Otsu's Threshold":
                    img_thresh_rgb_u8 = img_otsu_rgb_u8
                case "Adaptive Threshold":
                    img_thresh_rgb_u8 = img_adap_thresh_rgb_u8
                case "InRange Threshold":
                    img_thresh_rgb_u8 = img_inrange_thresh_rgb_u8
                case _:
                    img_thresh_rgb_u8 = img_blur_rgb_u8

    with st.expander("Edge Detection", expanded=False):
        st.write(
            "Edge detection is a technique used to identify and locate sharp discontinuities in an image, which typically correspond to object boundaries."
        )
        col_edge_gray, col_edge_rgb = st.columns(2)

        edge_options = [
            "Canny Edge Detection",
            "Sobel Edge Detection",
            "Laplacian Edge Detection",
        ]
        with col_edge_gray:
            st.header("Gray")
            selected_edge_option_gray = st.selectbox(
                "Select Edge Detection Method",
                options=edge_options,
                key="edge_select_gray",
            )

            # Canny Edge Detection - Gray
            imgu8_canny_thres1 = st.slider(
                "Canny Edge Detection Threshold 1",
                min_value=0,
                max_value=255,
                value=100,
                step=1,
                key="canny_thres1_gray",
            )
            imgu8_canny_thres2 = st.slider(
                "Canny Edge Detection Threshold 2",
                min_value=0,
                max_value=255,
                value=200,
                step=1,
                key="canny_thres2_gray",
            )
            img_edges_gray_u8_canny = cv2.Canny(
                img_thresh_gray_u8, imgu8_canny_thres1, imgu8_canny_thres2
            )
            st.image(
                img_edges_gray_u8_canny,
                caption=f"Canny Edge Detection with thresholds {imgu8_canny_thres1} and {imgu8_canny_thres2}",
            )

            # Sobel Edge Detection - Gray
            imgu8_sobel_ksize = st.slider(
                "Sobel Edge Detection Kernel Size",
                min_value=1,
                max_value=31,
                value=5,
                step=2,
                key="sobel_ksize_gray",
            )
            sobelx = cv2.Sobel(
                img_thresh_gray_u8, cv2.CV_64F, 1, 0, ksize=imgu8_sobel_ksize
            )
            sobely = cv2.Sobel(
                img_thresh_gray_u8, cv2.CV_64F, 0, 1, ksize=imgu8_sobel_ksize
            )
            img_edges_gray_u8_sobel = cv2.magnitude(sobelx, sobely)
            st.image(
                img_edges_gray_u8_sobel,
                caption=f"Sobel Edge Detection with kernel size {imgu8_sobel_ksize}",
            )

            # Laplacian Edge Detection - Gray
            img_edges_gray_u8_laplacian = cv2.Laplacian(img_thresh_gray_u8, cv2.CV_64F)
            st.image(img_edges_gray_u8_laplacian, caption="Laplacian Edge Detection")

            match selected_edge_option_gray:
                case "Canny Edge Detection":
                    img_edges_gray_u8 = cv2.Canny(img_thresh_gray_u8, 100, 200)
                case "Sobel Edge Detection":
                    sobelx = cv2.Sobel(img_thresh_gray_u8, cv2.CV_64F, 1, 0, ksize=5)
                    sobely = cv2.Sobel(img_thresh_gray_u8, cv2.CV_64F, 0, 1, ksize=5)
                    img_edges_gray_u8 = cv2.magnitude(sobelx, sobely)
                case "Laplacian Edge Detection":
                    img_edges_gray_u8 = cv2.Laplacian(img_thresh_gray_u8, cv2.CV_64F)
                case _:
                    img_edges_gray_u8 = img_thresh_gray_u8

        with col_edge_rgb:
            st.header("RGB")
            selected_edge_option_rgb = st.selectbox(
                "Select Edge Detection Method",
                options=edge_options,
                key="edge_select_rgb",
            )

            # Canny Edge Detection - RGB
            imrgb_canny_thres1 = st.slider(
                "Canny Edge Detection Threshold 1",
                min_value=0,
                max_value=255,
                value=100,
                step=1,
                key="canny_thres1_rgb",
            )
            imrgb_canny_thres2 = st.slider(
                "Canny Edge Detection Threshold 2",
                min_value=0,
                max_value=255,
                value=200,
                step=1,
                key="canny_thres2_rgb",
            )
            img_edges_rgb_u8_canny = cv2.Canny(
                img_thresh_rgb_u8, imrgb_canny_thres1, imrgb_canny_thres2
            )
            st.image(
                img_edges_rgb_u8_canny,
                caption=f"Canny Edge Detection with thresholds {imrgb_canny_thres1} and {imrgb_canny_thres2}",
            )

            # Sobel Edge Detection - RGB
            imrgb_sobel_ksize = st.slider(
                "Sobel Edge Detection Kernel Size",
                min_value=1,
                max_value=31,
                value=5,
                step=2,
                key="sobel_ksize_rgb",
            )
            sobelx_rgb = cv2.Sobel(
                img_thresh_rgb_u8, cv2.CV_64F, 1, 0, ksize=imrgb_sobel_ksize
            )
            sobely_rgb = cv2.Sobel(
                img_thresh_rgb_u8, cv2.CV_64F, 0, 1, ksize=imrgb_sobel_ksize
            )
            img_edges_rgb_u8_sobel = cv2.magnitude(sobelx_rgb, sobely_rgb)
            st.image(
                img_edges_rgb_u8_sobel,
                caption=f"Sobel Edge Detection with kernel size {imrgb_sobel_ksize}",
            )

            # Laplacian Edge Detection - RGB
            img_edges_rgb_u8_laplacian = cv2.Laplacian(img_thresh_rgb_u8, cv2.CV_64F)
            st.image(img_edges_rgb_u8_laplacian, caption="Laplacian Edge Detection")
            match selected_edge_option_rgb:
                case "Canny Edge Detection":
                    img_edges_rgb_u8 = cv2.Canny(img_thresh_rgb_u8, 100, 200)
                case "Sobel Edge Detection":
                    sobelx = cv2.Sobel(img_thresh_rgb_u8, cv2.CV_64F, 1, 0, ksize=5)
                    sobely = cv2.Sobel(img_thresh_rgb_u8, cv2.CV_64F, 0, 1, ksize=5)
                    img_edges_rgb_u8 = cv2.magnitude(sobelx, sobely)
                case "Laplacian Edge Detection":
                    img_edges_rgb_u8 = cv2.Laplacian(img_thresh_rgb_u8, cv2.CV_64F)
                case _:
                    img_edges_rgb_u8 = img_thresh_rgb_u8
