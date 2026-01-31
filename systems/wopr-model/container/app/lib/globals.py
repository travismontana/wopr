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
APP_DOMAIN = WOPR_CONFIG.get("baseDomain", "wopr.tailandtraillabs.org")
APP_API_URL = WOPR_CONFIG.get("api.internalUrl", "http://wopr-api:8000")
APP_OTEL_HOST = WOPR_CONFIG.get("tracing.hostInternal", "http://wopr-monitoring-tempo")
APP_OTEL_PORT = WOPR_CONFIG.get("tracing.portInternal", 4318)
APP_OTEL_URL = f"{APP_OTEL_HOST}:{APP_OTEL_PORT}"
APP_TRACING_ENABLED = WOPR_CONFIG.get("tracing.enabled", False)
WOPR_API_URL = APP_API_URL + "/api/v1"
LOGFILE = "/tmp/wopr-api.log"

APP_HOST = "0.0.0.0"
APP_PORT = 9000

# Service Configuration
SERVICE_NAME = APP_NAME
SERVICE_HOST = APP_HOST
SERVICE_PORT = int(APP_PORT)

# Storage Paths - Single Source of Truth
# All paths are resolved and absolute to prevent path traversal issues

WOPR_BASE_PATH = Path(WOPR_CONFIG["storage"]["base_path"]).resolve()
BASE_PATH = WOPR_BASE_PATH / "ml"
ARCHIVE_SUBDIR = WOPR_CONFIG["storage"]["archive_subdir"]
INCOMING_SUBDIR = WOPR_CONFIG["storage"]["incoming_subdir"]
LABEL_BASE_SUBDIR = WOPR_CONFIG["storage"]["label_subdir"]
LABEL_BASE_PATH = WOPR_BASE_PATH / LABEL_BASE_SUBDIR
LABEL_SOURCE_SUBDIR = WOPR_CONFIG["storage"]["label_source_subdir"]
LABEL_TARGET_SUBDIR = WOPR_CONFIG["storage"]["label_target_subdir"]

storage_paths = {
    "base_path": BASE_PATH,
    "wopr_base_path": WOPR_BASE_PATH,
    "archive_base_path": (BASE_PATH / ARCHIVE_SUBDIR).resolve(),
    "incoming_path": (BASE_PATH / INCOMING_SUBDIR).resolve(),
    "label_base_path": LABEL_BASE_PATH.resolve(),
    "label_source_path": (LABEL_BASE_PATH / LABEL_SOURCE_SUBDIR).resolve(),
    "label_target_path": (LABEL_BASE_PATH / LABEL_TARGET_SUBDIR).resolve(),
}
