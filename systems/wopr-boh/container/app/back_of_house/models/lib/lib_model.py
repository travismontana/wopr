import os
import requests
from django.utils.timezone import now

from core.models import ModelVersion, ModelBackup, ModelFamily
from django.forms.models import model_to_dict
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
    results = []

    model_fam = ModelFamily.objects.get(id=model.family_id)
    logger.info(f"Model family: {model_fam}")
    payload = {
        "action": "create_new_model_file",
        "filename": filename,
        "model_family": model_fam.shortname,
        "model": model_to_dict(model),
    }
    logger.info(f"Payload for model ctl: {payload}")

    filename_results = call_model_ctl(payload=payload)

    logger.info(f"Filename results: {filename_results}")

    if not filename_results or filename_results.get("status") != "success":
        logger.error(f"model_ctl failed: {filename_results}")
        return filename_results

    results.append(filename_results)

    new_version = ModelVersion.objects.create(
        version=1,
        artifact_uri=filename_results["file"],
        checksum=filename_results["checksum"],
        description="Initial version",
        note="",
        trained_at="",
        is_current=True,
        model_id=model.id,
        created_at=now(),
        updated_at=now(),
    )

    initial_backup = ModelBackup.objects.create(
        was_successful=False,
        artifact_uri="",
        model_version_id=new_version.id,
        created_at=now(),
        updated_at=now(),
        note="Initial backup record",
        taken_at=now(),
    )

    return results


def call_model_ctl(payload, url=None):
    url = url or os.getenv("MODEL_URL")

    try:
        response = requests.post(
            f"{url}/api/model_ctl",
            json={"payload": payload},
            timeout=300,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.Timeout:
        logger.error("model_ctl timed out after 5s | payload=%s", payload)
        return {"status": "timeout"}

    except requests.exceptions.ConnectionError:
        logger.error("model_ctl unreachable at %s | payload=%s", url, payload)
        return {"status": "unreachable"}

    except requests.exceptions.HTTPError as e:
        logger.error(
            "model_ctl returned %s | payload=%s | detail=%s",
            e.response.status_code,
            payload,
            e.response.text,
        )
        return {"status": "http_error", "detail": e.response.text}
