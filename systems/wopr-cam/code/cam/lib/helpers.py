"""
WOPR Frontend Helpers
Utility functions for Streamlit UI interactions with WOPR API.
"""

import httpx
import re
import logging
import sys
from datetime import datetime
from pathlib import Path

LOGGER_NAME = "helpers"

# ------------------------
# Logging Setup
# ------------------------

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


log = setup_logger()

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

