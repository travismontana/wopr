import os
import sys
import json
import logging
import requests
from pathlib import Path

LOGGER_NAME = "wopr_boh"


def setup_logger() -> logging.Logger:
    """
    Configure logging for helper functions.

    Returns:
        Configured logger instance

    Note:
        Only configures once - subsequent calls return existing logger
    """
    file_path = "/tmp/wopr.log"
    logger = logging.getLogger(LOGGER_NAME)
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


logger = setup_logger()


def get_config() -> dict:
    """
    Load configuration from a JSON file.

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: Config file not found
        json.JSONDecodeError: Invalid JSON in config file
        PermissionError: Cannot read config file
    """
    logger = logging.getLogger(__name__)
    config_path = Path("/config/wopr.config.yaml")
    config = {}
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")

    if not config_path.is_file():
        logger.error(f"Config path is not a file: {config_path}")

    try:
        with config_path.open("r") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
    except PermissionError as e:
        logger.error(f"Permission denied reading config file: {e}")
    except FileNotFoundError as e:
        config = {
            "storage": {
                "base_path": os.getenv("BASE_PATH", "/tmp"),
                "images_subdir": "images",
                "incoming_subdir": "incoming",
                "archive_subdir": "archive",
                "backups_subdir": "backup",
                "label_subdir": "labelstudio",
                "label_source_subdir": "source",
                "label_target_subdir": "target",
                "models_subdir": "models",
                "weights_subdir": "weights",
                "runs_subdir": "runs",
                "distfiles_subdir": "distfiles",
            },
            "api": {
                "images_url": os.getenv("IMAGES_URL", "https://images"),
                "thumbs_url": os.getenv("THUMB_URL", "https://imgproxy"),
                "labels_url": os.getenv("LABEL_STUDIO_URL", "http://localhost:8080"),
            },
            "camera": {
                "camDict": {
                    "0": {
                        "host": os.getenv("CAMERA_HOST", "localhost"),
                        "port": os.getenv("CAMERA_PORT", 8000),
                        "width": int(os.getenv("CAMERA_WIDTH", 3840)),
                        "height": int(os.getenv("CAMERA_HEIGHT", 2160)),
                    }
                }
            },
        }
    return config
