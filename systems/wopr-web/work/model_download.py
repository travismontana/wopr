import streamlit as st
from ultralytics import YOLO
import os
from pathlib import Path

def model_download():
    # Curated model registry based on ultralytics documentation
    # Updated as of January 2025
    MODEL_REGISTRY = {
        "YOLO26 - Detection (Latest, NMS-free)": {
            "yolo26n.pt": "Nano - Fast, minimal accuracy hit",
            "yolo26s.pt": "Small - Balanced speed/accuracy",
            "yolo26m.pt": "Medium - Better accuracy, slower",
            "yolo26l.pt": "Large - High accuracy",
            "yolo26x.pt": "Extra Large - Maximum accuracy, slowest",
        },
        "YOLO11 - Detection": {
            "yolo11n.pt": "Nano - Lightweight",
            "yolo11s.pt": "Small - Balanced",
            "yolo11m.pt": "Medium - Solid performer",
            "yolo11l.pt": "Large - Heavy hitter",
            "yolo11x.pt": "Extra Large - Top tier",
        },
        "YOLOv8 - Detection": {
            "yolov8n.pt": "Nano - Classic lightweight",
            "yolov8s.pt": "Small - Workhorse",
            "yolov8m.pt": "Medium - Balanced",
            "yolov8l.pt": "Large - High accuracy",
            "yolov8x.pt": "Extra Large - Maximum performance",
        },
        "YOLO26 - Segmentation": {
            "yolo26n-seg.pt": "Nano - Instance segmentation",
            "yolo26s-seg.pt": "Small - Instance segmentation",
            "yolo26m-seg.pt": "Medium - Instance segmentation",
            "yolo26l-seg.pt": "Large - Instance segmentation",
            "yolo26x-seg.pt": "Extra Large - Instance segmentation",
        },
        "YOLO11 - Segmentation": {
            "yolo11n-seg.pt": "Nano - Instance segmentation",
            "yolo11s-seg.pt": "Small - Instance segmentation",
            "yolo11m-seg.pt": "Medium - Instance segmentation",
            "yolo11l-seg.pt": "Large - Instance segmentation",
            "yolo11x-seg.pt": "Extra Large - Instance segmentation",
        },
        "YOLO26 - Pose Estimation": {
            "yolo26n-pose.pt": "Nano - Keypoint detection",
            "yolo26s-pose.pt": "Small - Keypoint detection",
            "yolo26m-pose.pt": "Medium - Keypoint detection",
            "yolo26l-pose.pt": "Large - Keypoint detection",
            "yolo26x-pose.pt": "Extra Large - Keypoint detection",
        },
        "YOLO11 - Classification": {
            "yolo11n-cls.pt": "Nano - Image classification",
            "yolo11s-cls.pt": "Small - Image classification",
            "yolo11m-cls.pt": "Medium - Image classification",
            "yolo11l-cls.pt": "Large - Image classification",
            "yolo11x-cls.pt": "Extra Large - Image classification",
        },
    }

    # Sidebar for model info
    with st.sidebar:
        st.header("📊 Model Info")
        st.markdown("""
        **Cache Location:**  
        `~/.ultralytics/`
        
        **Model Sizes:**
        - **n** (nano): ~3-6 MB
        - **s** (small): ~11-22 MB  
        - **m** (medium): ~25-50 MB
        - **l** (large): ~43-87 MB
        - **x** (extra): ~68-136 MB
        
        *Sizes vary by task type*
        """)

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        # Model family selection
        selected_family = st.selectbox(
            "Select Model Family",
            options=list(MODEL_REGISTRY.keys()),
            help="Choose the model family and task type"
        )
        
        # Model variant selection
        models_in_family = MODEL_REGISTRY[selected_family]
        
        # Create formatted options for selectbox
        model_options = [
            f"{model} - {desc}" 
            for model, desc in models_in_family.items()
        ]
        
        selected_option = st.selectbox(
            "Select Model Variant",
            options=model_options,
            help="Smaller models = faster inference, lower accuracy"
        )
        
        # Extract actual model name from selection
        selected_model = selected_option.split(" - ")[0]
        
        st.info(f"**Selected:** `{selected_model}`")

    with col2:
        st.markdown("### Quick Guide")
        st.markdown("""
        **Detection:** Bounding boxes  
        **Segmentation:** Pixel masks  
        **Pose:** Keypoint estimation  
        **Classification:** Image labels
        """)

    # Download section
    st.divider()

    col_btn, col_status = st.columns([1, 3])

    with col_btn:
        download_btn = st.button(
            "⬇️ Download Model", 
            type="primary",
            use_container_width=True
        )

    with col_status:
        status_placeholder = st.empty()

    if download_btn:
        with st.spinner(f"Downloading {selected_model}... (initiating download sequence)"):
            try:
                # Download the model
                model = YOLO(selected_model)
                
                # Get model path - handle different attribute names
                if hasattr(model, 'model_path'):
                    model_path = model.model_path
                elif hasattr(model, 'ckpt_path'):
                    model_path = model.ckpt_path
                else:
                    # Fallback to default location
                    model_path = Path.home() / ".ultralytics" / selected_model
                
                status_placeholder.success(f"✅ Download complete!")
                
                # Display model details
                st.divider()
                
                detail_cols = st.columns(3)
                
                with detail_cols[0]:
                    if os.path.exists(str(model_path)):
                        file_size = os.path.getsize(str(model_path)) / (1024 * 1024)
                        st.metric("Model Size", f"{file_size:.2f} MB")
                    else:
                        st.metric("Model Size", "N/A")
                
                with detail_cols[1]:
                    st.metric("Status", "Ready")
                
                with detail_cols[2]:
                    st.metric("Task", selected_family.split(" - ")[1] if " - " in selected_family else "Detection")
                
                # Show path
                st.code(f"Cache location: {model_path}", language="bash")
                
                # Model info if available
                try:
                    with st.expander("📋 Model Details", expanded=False):
                        st.write("**Model Type:**", type(model).__name__)
                        if hasattr(model, 'names'):
                            st.write("**Classes:**", len(model.names) if model.names else "N/A")
                        st.write("**Path:**", str(model_path))
                except Exception as e:
                    st.caption(f"Could not retrieve detailed info: {e}")
                    
            except Exception as e:
                status_placeholder.error(f"❌ Download failed: {e}")
                st.write("**Error Details:**")
                st.code(str(e))

    # Footer
    st.divider()
    st.caption("""
    💡 **Tip:** Models download once and cache locally. Subsequent loads are instant.  
    🔄 **Update:** Run `pip install -U ultralytics` to get the latest models.
    """)