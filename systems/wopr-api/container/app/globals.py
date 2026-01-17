# Copyright 2026 Bob Bomar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# app/globals.py
"""
Global constants and configuration for WOPR API.
Single source of truth for all static values.
"""
import os
import logging
import sys
from pathlib import Path

logger = logging.getLogger("Bootup")
logging.basicConfig(filename="/var/log/wopr-api.log", level="DEBUG")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logger.info("WOPR API - Pre Initialization Globals")

# These env variables are required:
#   WOPR_VERSION: "v0.1.5-alpha"
#   WOPR_ENVIRONMENT: "production"
#
# If not set, the app will exit during startup.

DIRECTUS_HOST = "http://wopr-directus"
ENVIRONMENT = os.getenv('WOPR_ENVIRONMENT', 'development')

if ENVIRONMENT != 'production':
    DIRECTUS_HOST += f"-{ENVIRONMENT}"

DIRECTUS_URL = f"{DIRECTUS_HOST}:8055"

# Get DIRECTUS_TOKEN from environment, no fallbacks.
DIRECTUS_TOKEN = os.getenv('DIRECTUS_TOKEN')

# Set up Directus authentication headers
if DIRECTUS_TOKEN:
    DIRECTUS_HEADERS = {
        "Authorization": f"Bearer {DIRECTUS_TOKEN}"
    }
else:
    DIRECTUS_HEADERS = {}

DIRECTUS_CONFIG_ENDPOINT = f"{DIRECTUS_URL}/items/woprconfig?environment={ENVIRONMENT}"

def get_directus_config():
    """Fetch configuration from Directus CMS."""
    import requests
    try:
        response = requests.get(DIRECTUS_CONFIG_ENDPOINT, headers=DIRECTUS_HEADERS)
        response.raise_for_status()
        config_data = response.json()
        return config_data.get('data', [])
    except requests.RequestException as e:
        print(f"Error fetching config from Directus: {e}")
        exit(1)

WOPR_CONFIG = get_directus_config()[0]['data']
logger.info("WOPR_CONFIG: %s", WOPR_CONFIG)

if WOPR_CONFIG['nelson'] != "haha":
    logger.info("WOPR_CONFIG fetch failed or is invalid. Exiting.")
    exit(1)

APP_NAME = "wopr-api"
APP_TITLE = "WOPR API"
APP_VERSION = "0.1.5-alpha"
APP_DESCRIPTION = "WOPR API application package"
APP_AUTHOR = "Bob Bomar"
APP_AUTHOR_EMAIL = "bob@bomar.us"
APP_DOMAIN = WOPR_CONFIG.get('baseDomain', "wopr.tailandtraillabs.org")
APP_API_URL = WOPR_CONFIG.get('api.internalUrl', "http://wopr-api:8000")
APP_OTEL_HOST = WOPR_CONFIG.get('tracing.hostInternal', "http://wopr-monitoring-tempo")
APP_OTEL_PORT = WOPR_CONFIG.get('tracing.portInternal', 4318)
APP_OTEL_URL = f"{APP_OTEL_HOST}:{APP_OTEL_PORT}"
APP_TRACING_ENABLED = WOPR_CONFIG.get('tracing.enabled', False)
WOPR_API_URL = APP_API_URL + "/api/v1"
DATABASE_URL = (
    'postgresql://' + 
    os.getenv('DBUSER') + ":" + 
    os.getenv('DBPASSWORD') + "@" + 
    os.getenv('DBHOST') + ":" + 
    os.getenv('DBPORT') + "/" + 
    os.getenv('DBNAME')
)

HOMEASSISTANT_URL = WOPR_CONFIG.get('homeAssistant.host', "http://homeassistant.local:8123")
HOMEASSISTANT_TOKEN = os.getenv("HOMEASSISTANT_TOKEN", "")

APP_HOST = "0.0.0.0"
APP_PORT = 8000

# Service Configuration
SERVICE_NAME = APP_NAME
SERVICE_HOST = APP_HOST
SERVICE_PORT = int(APP_PORT)

# Storage Paths - Single Source of Truth
# All paths are resolved and absolute to prevent path traversal issues
BASE_PATH = Path(WOPR_CONFIG['storage']['base_path']).resolve()
ARCHIVE_SUBDIR = WOPR_CONFIG['storage']['archive_subdir']
INCOMING_SUBDIR = WOPR_CONFIG['storage']['incoming_subdir']
VISION_BASE_SUBDIR = WOPR_CONFIG['vision']['base_path']
VISION_SOURCE_SUBDIR = WOPR_CONFIG['vision']['source_path']
VISION_TARGET_SUBDIR = WOPR_CONFIG['vision']['target_path']

storage_paths = {
    "base_path": BASE_PATH,
    "archive_base_path": (BASE_PATH / ARCHIVE_SUBDIR).resolve(),
    "incoming_path": (BASE_PATH / INCOMING_SUBDIR).resolve(),
    "vision_base_path": (BASE_PATH / VISION_BASE_SUBDIR).resolve(),
    "labelstudio_base_path": (BASE_PATH / VISION_BASE_SUBDIR).resolve(),
    "labelstudio_source_path": (BASE_PATH / VISION_SOURCE_SUBDIR).resolve(),
    "labelstudio_target_path": (BASE_PATH / VISION_TARGET_SUBDIR).resolve(),
}