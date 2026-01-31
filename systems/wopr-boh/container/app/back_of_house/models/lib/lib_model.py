import os
import requests
from django.utils.timezone import now

from core.models import ModelVersion, ModelBackup, ModelFamily

from lib.helpers import setup_logger

logger = setup_logger()

def build_vers(model):
    """
    Build initial version data for a given model.
    This function creates a new ModelVersion instance and initializes
    its status and backup records.

    Args:
        model (ModelInfo): The model for which to build the version.
    Returns:
        results (dict): A dictionary containing the created version,
    """
    logger.info(f"Building version for model: {model}")
    if model is None:
        return None
    name = model.name
    filename = f"{name}_v1.pt"

    model_fam = ModelFamily.objects.get(id=model.family_id)
    logger.info(f"Model family: {model_fam}")
    payload = {
        "action": "create_new_model_file",
        "filename": filename,
        "model_family": model_fam.shortname,
    }
    logger.info(f"Payload for model ctl: {payload}")
    try:
        filename_results = call_model_ctl(model=name, payload=payload)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling model ctl: {e}")
        return None
    logger.info(f"Filename results: {filename_results.json()}")
    filename_results = filename_results.json()
    # Create a new ModelVersion instance
    new_version = ModelVersion.objects.create(
        version = 1,
        artifact_uri=filename_results.file,
        checksum=filename_results.checksum,
        description="Initial version",
        note="",
        trained_at="",
        is_current=True,
        model_id=model.id,
        created_at=now(),
        updated_at=now(),
    )

    # Create an initial ModelBackup for the new version
    initial_backup = ModelBackup.objects.create(
        was_successful=False,
        artifact_uri="",
        model_version_id=new_version.id,
        created_at=now(),
        updated_at=now(),
        note="Initial backup record",
        taken_at=now(),
    )

    # now save the to the db
    results = {
        "model_version": new_version,
        "model_backup": initial_backup,
    }

    new_version.save()
    initial_backup.save()

    return results


def call_model_ctl(model, payload, url=None):
    url = url or os.getenv("MODEL_URL")
    return requests.post(
        f"{url}/api/model_ctl",
        json={"model": model, "payload": payload},
        timeout=5,  # Don't hang forever if the other side is down
    )
