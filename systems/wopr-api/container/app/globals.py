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
APP_API_URL = "https://wopr-api." + APP_DOMAIN
APP_OTEL_URL = "https://otel.monitoring.abode.tailandtraillabs.org"
WOPR_API_URL = os.getenv('WOPR_API_URL', APP_API_URL+"/api/v1")
DATABASE_URL = 'postgresql://' + os.getenv('WOPR_DB_USER') + ":" + os.getenv('WOPR_DB_PASSWORD') + "@wopr-config-db-cluster-rw.wopr.svc:5432/wopr-db"

APP_HOST = "0.0.0.0"
APP_PORT = 8000

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