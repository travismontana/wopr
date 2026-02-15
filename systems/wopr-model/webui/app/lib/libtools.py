import os
import logging
import sys
import uuid
import requests
import math

import numpy as np

from label_studio_sdk import LabelStudio
from label_studio_sdk.converter import Converter
from label_studio_sdk._extensions.label_studio_tools.core.utils.io import get_local_path

RUNS = "/ultralytics/runs"
WEIGHTS = "/ultralytics/weights"
DATASETS = "/ultralytics/datasets"

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")
LABEL_STUDIO_TOKEN = os.getenv("LABEL_STUDIO_TOKEN", "changeme")

LS_CLIENT = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_TOKEN)


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


logger  = setup_logger()

#################################
#
# Start of the new openapi-pyton stuff
#
#################################


def logit(note, data):
    """_summary_

    Args:
        note (_type_): _description_
        data (_type_, optional): _description_. Defaults to None.
    """
    logger = setup_logger()
    logger.info(f"Note: ({note})")
    logger.debug(f"Data: ({data})")


def get_models():
    """Returns a list of available YOLOv8 model weights in the WEIGHTS directory."""
    if not os.path.exists(WEIGHTS):
        return []
    return [f for f in os.listdir(WEIGHTS) if f.endswith(('.pt', '.yaml'))]

def get_projects():
    logger.info(f"Retrieving projects from Label Studio at {LABEL_STUDIO_URL}")
    projects = LS_CLIENT.projects.list()
    logger.info(f"Retrieved projects: {projects}")
    return projects

def export_annotations(project_id):
    dataset_uuid = str(uuid.uuid4())
    payload = {
        "project_id": project_id,
        "dataset_uuid": dataset_uuid,
    }
    logger.info(f"Exporting annotations for project {project_id} with dataset UUID {dataset_uuid}")
    # post payload to http://wopr-model/api/model_ctl
    try:
        response = requests.post(
            "http://wopr-model:9000/api/model_ctl",
            json={
                "payload": {
                    "action": "generate_dataset",
                    "dataset": payload,
                },
            },
            timeout=300,
        )
        logger.info(f"Export request sent: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send export request: {e}")


def where_are_pieces(pieces_list, circle_center, pixel_to_mm):

    OUTER_RING_RHO_MM = 158
    MIDDLE_RING_RHO_MM = 86
    INNER_RING_RHO_MM = 40

    save_list = []
    for piece in pieces_list:
        x1, y1, x2, y2 = piece["x1"], piece["y1"], piece["x2"], piece["y2"]
        polar1_rho_px = piece["polar1"]["rho"]
        polar2_rho_px = piece["polar2"]["rho"]
        cc_x = circle_center[0]
        cc_y = circle_center[1]
        fixed_x1 = x1 - cc_x
        fixed_x2 = x2 - cc_x
        fixed_y1 = y1 - cc_y
        fixed_y2 = y2 - cc_y
        middle_x = np.mean([fixed_x1, fixed_x2]).astype(int)
        middle_y = np.mean([fixed_y1, fixed_y2]).astype(int)
        fixed_x1_mm = fixed_x1 * pixel_to_mm
        fixed_x2_mm = fixed_x2 * pixel_to_mm
        middle_x_mm = middle_x * pixel_to_mm
        fixed_y1_mm = fixed_y1 * pixel_to_mm
        fixed_y2_mm = fixed_y2 * pixel_to_mm
        middle_y_mm = middle_y * pixel_to_mm
        piece_s1_rho = math.isqrt(int(fixed_x1_mm**2) + int(fixed_y1_mm**2))
        piece_s2_rho = math.isqrt(int(fixed_x2_mm**2) + int(fixed_y2_mm**2))
        piece_mid_rho = math.isqrt(int(middle_x_mm**2) + int(middle_y_mm**2))
        piece_s1_theta_deg = math.degrees(math.atan2(fixed_y1_mm, fixed_x1_mm))
        piece_s2_theta_deg = math.degrees(math.atan2(fixed_y2_mm, fixed_x2_mm))
        piece_mid_theta_deg = math.degrees(math.atan2(middle_y_mm, middle_x_mm))
        piece_s1_theta_rad = math.radians(piece_s1_theta_deg)
        piece_s2_theta_rad = math.radians(piece_s2_theta_deg)
        piece_mid_theta_rad = math.radians(piece_mid_theta_deg)
        pclass = piece["class"]
        is_inner = piece_mid_rho < INNER_RING_RHO_MM
        sector = int(piece_mid_theta_deg // 30)
        save_list.append(
            {
                "class": pclass,
                "s1_rho": piece_s1_rho,
                "s2_rho": piece_s2_rho,
                "mid_rho": piece_mid_rho,
                "s1_theta_deg": piece_s1_theta_deg,
                "s2_theta_deg": piece_s2_theta_deg,
                "mid_theta_deg": piece_mid_theta_deg,
                "s1_theta_rad": piece_s1_theta_rad,
                "s2_theta_rad": piece_s2_theta_rad,
                "mid_theta_rad": piece_mid_theta_rad,
                "is_inner_ring": is_inner,
                "sector": sector,
                "cell": (sector + 12) if is_inner else sector,
            }
        )

    return save_list
