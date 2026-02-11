import os
import logging
import sys
import uuid
import requests

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
