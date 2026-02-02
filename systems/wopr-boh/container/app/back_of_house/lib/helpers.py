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
    ls = os.getenv("LABEL_STUDIO_URL")
    if not ls:
        config_path = Path("/config/wopr.config.yaml")

        if not config_path.exists():
            logger.error(f"Config file not found: {config_path}")
            raise FileNotFoundError(f"Config file not found: {config_path}")

        if not config_path.is_file():
            logger.error(f"Config path is not a file: {config_path}")
            raise ValueError(f"Config path is not a file: {config_path}")

        try:
            with config_path.open("r") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
        except PermissionError as e:
            logger.error(f"Permission denied reading config file: {e}")
            raise

        if not isinstance(config, dict):
            logger.error(f"Config is not a dict, got {type(config)}")
            raise ValueError(f"Config must be a dict, got {type(config)}")

        logger.info(f"Loaded config from {config_path}")
    else:
        config = {
            "vision": {
                "label_studio_url": ls,
            },
        }
    return config


def call_model_control(payload, url=None):
    url = os.getenv("MODEL_URL") or get_config()["api"]["models_url"]
    logger.info(f"Calling model_ctl at {url} with payload: {payload}")
    try:
        response = requests.post(
            f"{url}/api/model_ctl",
            json={"payload": payload},
            timeout=300,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        logger.error("model_ctl timed out after 5s | payload=%s", payload)
        return {"status": "timeout"}

    except requests.exceptions.ConnectionError:
        logger.error("model_ctl unreachable at %s | payload=%s", url, payload)
        return {"status": "unreachable"}

    except requests.exceptions.HTTPError as e:
        logger.error(
            "model_ctl returned %s | payload=%s | detail=%s",
            e.response.status_code,
            payload,
            e.response.text,
        )
        return {"status": "http_error", "detail": e.response.text}
