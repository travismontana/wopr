import os

from lib.helpers import setup_logging
logger = setup_logging("wopr-api", "INFO", "/tmp/wopr-api.log")


DIRECTUS_HOST = os.getenv("DIRECTUS_HOST", "http://wopr-directus:8055")

ENVIRONMENT = os.getenv("WOPR_ENVIRONMENT", "production")

DIRECTUS_URL = f"{DIRECTUS_HOST}"

# Get DIRECTUS_TOKEN from environment, no fallbacks.
DIRECTUS_TOKEN = os.getenv("DIRECTUS_TOKEN")

# Set up Directus authentication headers
if DIRECTUS_TOKEN:
    DIRECTUS_HEADERS = {"Authorization": f"Bearer {DIRECTUS_TOKEN}"}
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
        return config_data.get("data", [])
    except requests.RequestException as e:
        logger.info(f"Directus: ({DIRECTUS_CONFIG_ENDPOINT}) Headers: ({DIRECTUS_HEADERS})")
        logger.info(f"Error fetching config from Directus: {e}")
        exit(1)


WOPR_CONFIG = get_directus_config()[0]["data"]
logger.info("WOPR_CONFIG: %s", WOPR_CONFIG)

if WOPR_CONFIG["nelson"] != "haha":
    logger.info("WOPR_CONFIG fetch failed or is invalid. Exiting.")
    exit(1)
    
APP_NAME = "wopr-api"
APP_VERSION = "0.0.1"
API_PREFIX = "/api/v3"
API_TITLE = "WOPR API"
API_DESCRIPTION = "WOPR API for managing resources"