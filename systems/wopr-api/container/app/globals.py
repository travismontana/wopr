# app/globals.py
"""
Global constants and configuration for WOPR API.
Single source of truth for all static values.
"""
import os

CONFDB_URL = (
    'postgresql://' + 
    os.getenv('CONFDBUSER', 'config_user') + ":" + 
    os.getenv('CONFDBPASSWORD', 'config_password') + "@" + 
    os.getenv('DBHOST', 'config_db_host') + ":" + 
    os.getenv('DBPORT', '5432') + "/" + 
    os.getenv('CONFDBNAME', 'config_db_name')
)





HACK_CAMERA_DICT = {
    "1": {
        "id": "1",
        "name": "wopr-cam",
        "url": "http://wopr-cam.hangar.bpfx.org",
        "port": 5000,
        "capabilities": [ "games", "ml"]
    }
}



# So, we're going redo this file, so this is the line in the sand for now.
# Anything above this will be removed at somepoint.
#
# These env variables are required:
#   WOPR_VERSION: "v0.1.5-alpha"
#   WOPR_ENVIRONMENT: "production
#
# If not then we'll kill the app, but that's a diffrent thread.
# 
# 
DIRECTUS_HOST = "http://wopr-directus"
ENVIRONMENT = os.getenv('WOPR_ENVIRONMENT', 'development')

if ENVIRONMENT != 'production':
    DIRECTUS_HOST += "-{ENVIRONMENT}"

DIRECTUS_URL = f"{DIRECTUS_HOST}:8055"

# Now, we'll get DIRECTUS_TOKEN from the environment, no fallbacks.
DIRECTUS_TOKEN = os.getenv('DIRECTUS_TOKEN')

# Now grab the config from directus, if the token is set great, use  it, if not, then fine, get the config without it.
if DIRECTUS_TOKEN:
    HEADERS = {
        "Authorization": f"Bearer {DIRECTUS_TOKEN}"
    }
else:
    HEADERS = {}
DIRECTUS_CONFIG_ENDPOINT = f"{DIRECTUS_URL}/items/woprconfig?environment={ENVIRONMENT}"

def get_directus_config():
    """Fetch configuration from Directus CMS."""
    import requests
    try:
        response = requests.get(DIRECTUS_CONFIG_ENDPOINT, headers=HEADERS)
        response.raise_for_status()
        config_data = response.json()
        return config_data.get('data', [])
    except requests.RequestException as e:
        print(f"Error fetching config from Directus: {e}")
        return []

WOPR_CONFIG = get_directus_config()

if WOPR_CONFIG.get('nelson') != "haha":
    print("WOPR_CONFIG fetch failed or is invalid. Exiting.")
    exit(1)

APP_NAME = "wopr-api"
APP_TITLE = "WOPR API"
APP_VERSION = "0.1.5-alpha"
APP_DESCRIPTION = "WOPR API application package"
APP_AUTHOR = "Bob Bomar"
APP_AUTHOR_EMAIL = "bob@bomar.us"
# WOPR_CONFIG['baseDomain'] or wopr.tailandtraillabs.org
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

HOMEASSISTANT_URL = WOPR_CONFIG.get( 'homeAssistant.host', "http://homeassistant.local:8123" )

HOMEASSISTANT_TOKEN = os.getenv(
    "HOMEASSISTANT_TOKEN",
    ""  # Must be set via environment variable or secret
)

APP_HOST = "0.0.0.0"
APP_PORT = 8000

# Service Configuration
SERVICE_NAME = APP_NAME
SERVICE_HOST = APP_HOST
SERVICE_PORT = int(APP_PORT)

