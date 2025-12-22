# app/globals.py
"""
Global constants and configuration for WOPR API.
Single source of truth for all static values.
"""
import os

# Application Identity
APP_NAME = "wopr-api"
APP_TITLE = "WOPR API"
APP_VERSION = "0.1.3-beta"
APP_DESCRIPTION = "WOPR API application package"
APP_AUTHOR = "Bob Bomar"
APP_AUTHOR_EMAIL = "bob@bomar.us"
APP_DOMAIN = "studio.abode.tailandtraillabs.org"
APP_CONFIG_URL = "http://wopr-config." + APP_DOMAIN

APP_HOST = "0.0.0.0"
APP_PORT = 8000

# Service Configuration
SERVICE_NAME = os.getenv("SERVICE_NAME", APP_NAME)
SERVICE_HOST = os.getenv("SERVICE_HOST", APP_HOST)
SERVICE_PORT = int(os.getenv("SERVICE_PORT", APP_PORT))

# External Services
CONFIG_SERVICE_URL = os.getenv("CONFIG_SERVICE_URL", APP_CONFIG_URL)

HACK_CAMERA_DICT = {
    "1": {
        "id": "1",
        "name": "wopr-cam",
        "url": "http://wopr-cam.hangar.bpfx.org",
        "port": 5000,
        "capabilities": [ "games", "ml"]
    }
}