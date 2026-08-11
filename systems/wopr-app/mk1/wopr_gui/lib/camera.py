from pathlib import Path
import re

import cv2

def list_attached_cameras() -> dict[int, str]:
    """
    List all attached cameras and return a dictionary of camera:
    - key: camera index (int)
    - name: camera name (str)
    - path: camera path (str)
    - make: camera manufacturer (str)
    - model: camera model (str)
    - capabilities: camera capabilities (dict)
    """
    camera_dict = {}
    for index in _attached_video_indices():  # Check attached video indices
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            # Get camera name and capabilities
            name = f"Camera {index}"
            path = f"/dev/video{index}"  # Assuming Linux device paths
            capabilities = {
                "frame_width": cap.get(cv2.CAP_PROP_FRAME_WIDTH),
                "frame_height": cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
                "fps": cap.get(cv2.CAP_PROP_FPS),
            }
            camera_dict[index] = {
                "name": name,
                "path": path,
                "make": "Unknown",  # Placeholder for camera manufacturer
                "model": "Unknown",  # Placeholder for camera model
                "capabilities": capabilities,
            }
        cap.release()
    return camera_dict

def _attached_video_indices() -> list[int]:
    indices = []
    for entry in Path("/sys/class/video4linux").glob("video*"):
        m = re.fullmatch(r"video(\d+)", entry.name)
        if m:
            indices.append(int(m.group(1)))
    return sorted(indices)

def get_camera_info(index: int) -> dict:
    cameras = list_attached_cameras()
    return cameras.get(index, None)

def is_camera_connected(index: int) -> bool:
    cam = cv2.VideoCapture(index)
    connected = cam.isOpened()
    if connected:
        cam.release()
    return connected and fps > 0