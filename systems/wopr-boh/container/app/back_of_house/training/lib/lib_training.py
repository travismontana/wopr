import os
import requests
from lib.helpers import setup_logger
from label_studio_sdk import LabelStudio

logger = setup_logger()
LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://label-studio:8080")
LABEL_STUDIO_TOKEN = os.getenv("LABEL_STUDIO_TOKEN", "changeme")

try:
    client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_TOKEN)
except Exception as e:
    logger.error(f"Failed to connect to Label Studio: {e}")
    client = None


def list_all_projects():
    """List all projects in Label Studio."""
    results = []
    projects = None
    if client is None:
        results.append(
            {
                "status": "error",
                "type": "connection",
                "message": "No connection to Label Studio.",
            }
        )
        return results, projects
    try:
        projects = list(client.projects.list())  # Convert to list
        logger.info(f"Fetched {len(projects)} projects from Label Studio.")
        logger.debug(f"Projects details: {projects}")
        results.append(
            {
                "status": "success",
                "type": "fetch",
                "message": f"Successfully fetched {len(projects)} projects",
            }
        )
        return results, projects
    except Exception as e:
        logger.error(f"Error fetching projects: {e}")
        results.append(
            {
                "status": "error",
                "type": "fetch",
                "message": f"Could not fetch projects: {str(e)}",
            }
        )
        return results, projects
