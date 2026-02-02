import os
import logging
import sys
from pathlib import Path

logger = logging.getLogger("Bootup")
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logger.info("WOPR API - Pre Initialization Globals")

APP_NAME = "wopr-api"
APP_TITLE = "WOPR API"
APP_VERSION = "0.1.5-alpha"
APP_DESCRIPTION = "WOPR API application package"
APP_AUTHOR = "Bob Bomar"
APP_AUTHOR_EMAIL = "bob@bomar.us"

LOGFILE = "/tmp/wopr-api.log"

APP_HOST = "0.0.0.0"
APP_PORT = 9000

# Service Configuration
SERVICE_NAME = APP_NAME
SERVICE_HOST = APP_HOST
SERVICE_PORT = int(APP_PORT)

# Storage Paths - Single Source of Truth
# All paths are resolved and absolute to prevent path traversal issues

BASE_PATH = "/remote/wopr"
MODEL_SUBDIR = "models"
MODEL_PATH = Path(BASE_PATH) / MODEL_SUBDIR
ARCHIVE_SUBDIR = "archive"
ARCHIVE_PATH = Path(BASE_PATH) / ARCHIVE_SUBDIR
BACKUPS_SUBDIR = "backups"
BACKUPS_PATH = Path(BASE_PATH) / BACKUPS_SUBDIR
DISTFILES_SUBDIR = "distfiles"
DISTFILES_PATH = Path(BASE_PATH) / DISTFILES_SUBDIR
DOWNLOADS_SUBDIR = "downloads"
DOWNLOADS_PATH = Path(BASE_PATH) / DOWNLOADS_SUBDIR
INCOMING_SUBDIR = "incoming"
INCOMING_PATH = Path(BASE_PATH) / INCOMING_SUBDIR
LABEL_BASE_PATH = Path(BASE_PATH) / "labels"
LABEL_SOURCE_SUBDIR = "source"
LABEL_SOURCE_PATH = Path(LABEL_BASE_PATH) / LABEL_SOURCE_SUBDIR
LABEL_TARGET_SUBDIR = "target"
LABEL_TARGET_PATH = Path(LABEL_BASE_PATH) / LABEL_TARGET_SUBDIR

storage_paths = {
    "base_path": Path(BASE_PATH).resolve(),
    "archive_base_path": (Path(BASE_PATH) / ARCHIVE_SUBDIR).resolve(),
    "incoming_path": (Path(BASE_PATH) / INCOMING_SUBDIR).resolve(),
    "label_base_path": LABEL_BASE_PATH.resolve(),
    "label_source_path": (LABEL_SOURCE_PATH).resolve(),
    "label_target_path": (LABEL_TARGET_PATH).resolve(),
    "model_path": (Path(BASE_PATH) / MODEL_SUBDIR).resolve(),
    "backups_path": (Path(BASE_PATH) / BACKUPS_SUBDIR).resolve(),
    "distfiles_path": (Path(BASE_PATH) / DISTFILES_SUBDIR).resolve(),
    "downloads_path": (Path(BASE_PATH) / DOWNLOADS_SUBDIR).resolve(),
}
WEIGHTS_PATH = "/ultralytics/weights"
DATASETS_PATH = "/ultralytics/datasets"
