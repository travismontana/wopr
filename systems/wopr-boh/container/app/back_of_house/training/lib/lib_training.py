import os
import requests
from lib.helpers import setup_logger
from django.forms.models import model_to_dict
from label_studio_sdk import LabelStudio

from core.models import TrainingRun, Dataset, Result

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
        logger.error(
            " list_all_projects - if client is None - No connection to Label Studio."
        )
        results.append(
            {
                "status": "error",
                "type": "connection",
                "message": "No connection to Label Studio.",
            }
        )
        return results, projects
    try:
        logger.info(f"Fetching projects from Label Studio...{LABEL_STUDIO_URL}...")
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
    # catch the timeout
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout error fetching projects: {e}")
        results.append(
            {
                "status": "error",
                "type": "timeout",
                "message": f"Timeout error fetching projects: {str(e)}",
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


def get_training_uuid(version, project_id, description="", notes=""):
    """Create a TrainingRun entry and return its UUID."""
    logger.info("Creating TrainingRun entry...")
    logger.info(f"Version ID: {version.id}, Project ID: {project_id}")
    results = []
    dataset, creates = Dataset.objects.get_or_create(
        artifact_uri="/dev/null", project_id=project_id
    )
    result = Result.objects.create(artifact_uri="/dev/null")
    training_run = TrainingRun.objects.create(
        model_version=version,
        description=description,
        note=project_id,
        dataset=dataset,
        result=result,
    )
    logger.info(
        f"Created TrainingRun with UUID: {training_run.uuid} for version ID: {version.id} and project ID: {project_id}"
    )
    results.append(
        {
            "status": "success",
            "type": "creation",
            "message": f"Created TrainingRun with UUID: {training_run.uuid}",
        }
    )
    return training_run, results
