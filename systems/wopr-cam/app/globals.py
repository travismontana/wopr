# app/globals.py
"""
Global constants and configuration for WOPR API.
Single source of truth for all static values.
"""
import os

# Application Identity
APP_NAME = "wopr-cam"
APP_TITLE = "WOPR Camera API"
APP_VERSION = "0.1.5-alpha"
APP_DESCRIPTION = "WOPR Camera API application package"
APP_AUTHOR = "Bob Bomar"
APP_AUTHOR_EMAIL = "bob@bomar.us"
APP_DOMAIN = "wopr.tailandtraillabs.org"
APP_API_URL = "https://api." + APP_DOMAIN
APP_OTEL_URL = "https://otel." + APP_DOMAIN
#WOPR_API_URL = os.getenv('WOPR_API_URL', APP_API_URL+"/api/v1")
WOPR_API_URL = APP_API_URL + "/api/v2"

APP_HOST = "0.0.0.0"
APP_PORT = 5000

# Service Configuration
SERVICE_NAME = os.getenv("SERVICE_NAME", APP_NAME)
SERVICE_HOST = os.getenv("SERVICE_HOST", APP_HOST)
SERVICE_PORT = int(os.getenv("SERVICE_PORT", APP_PORT))

HACK_CAMERA_DICT = {
    "1": {
        "id": "1",
        "name": "wopr-cam",
        "url": "http://wopr-cam.hangar.bpfx.org",
        "port": 5000,
        "capabilities": [ "games", "ml"]
    }
}