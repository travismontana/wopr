from typing import Any
from pathlib import Path
import hashlib
import inspect
from fastapi import APIRouter, Request


from lib.helpers import (
    setup_logger,
    update_operations,
    logit,
    check_for_file_in_dir,
    get_one,
    get_all,
    download_file,
    copy_file_to_dist,
    copy_modfam_to_model,
    backup_dist_file,
)

from lib.safe_file import SafeFS

from lib.wopr_api_client import Client
from lib.wopr_api_client.models.model_update import ModelUpdate
from lib.wopr_api_client.api.models import (
    update_item_api_v2_models_item_id_patch,
)
from lib.wopr_api_client.types import Response


logger = setup_logger()
WOPR_API_URL = "https://api.wopr.tailandtraillabs.org/api/v2"

woprclient = Client(base_url=WOPR_API_URL)

api_models = APIRouter(tags=["models"])


@api_models.post("/model_status", response_model=None)
async def model_status(data: Any, request: Request):
    """Get the status of the model, via post"""
    logger.info("Model status update received")
    logger.debug("Data: %s", data)

    config = request.app.state.config
    paths = request.app.state.paths
    try:
        model_name = data.name
    except Exception as e:
        logger.error("Error retrieving model name: %s", e)
        logger.info("Existing due to data not having a name")
        return update_operations(
            data,
            "Model did not have a name",
            {
                "config": config,
                "paths": paths,
            },
            "Fatal Error",
        )

    if model_status in data:
        logit("Model status found in data", data)
        has_existing_status = True
        filename = data.model_status.filename

    if not filename:
        logit(
            "Filename not provided, defaulting to {model_name}.pt",
            {"model_name": model_name},
        )
        filename = f"{model_name}.pt"
        data.model_status.filename = filename

    protected_path = SafeFS(Path(paths["modelspath"]))

    # Check for backups
    # only checks {paths['models_backup_path']}
    data.model_status.backup["has_backup"] = check_for_file_in_dir(
        filename, paths["models_backup_path"], protected_path
    )

    # Check for distfiles
    data.model_status.has_distfile = check_for_file_in_dir(
        filename,
        paths["models_distfiles_path"],
        protected_path,
    )

    if data.model_status.has_distfile:
        try:
            data.model_status.checksum = hashlib.sha256(
                f"{paths['models_path']}/{paths['models_distfiles_path']}/{filename}"
            )
        except Exception as e:
            logit(f"Error calculating checksum: {e}", data)

    logit("Status Complete", data)

    client = Client(base_url=WOPR_API_URL)
    async with client as client:
        response: Response[ModelUpdate] = (
            await update_item_api_v2_models_item_id_patch.asyncio(
                item_id=data.id, client=client, body=data
            )
        )
        logit("Model update response received", response)
    return data


@api_models.post("/activate")
def activate_model(model_dict: dict, request: Request):
    """Activate the model requested"""
    logger.info("Activating model")
    logger.debug(f"Activation data: {model_dict}")
    config = request.app.state.config
    paths = request.app.state.paths
    model_id = model_dict.get("model_id")
    try:
        model_info = get_one("models", model_id)
    except Exception as e:
        logit(f"Error retrieving model info: {e}")
        return False

    if model_info is None or not model_info:
        message = f"Model id ({model_id}) not found"
        logit(message, model_info)
        return message
    logit("Model info retrieved", model_info)

    model_families = get_all("model_family")
    logit("Model families retrieved", model_families)
    if "familyid" in model_info:
        family_id = model_info["familyid"]
        logit("Family ID retrieved", family_id)
        family = [m for m in model_families if m["id"] == family_id]
        logit("Family name retrieved", family)
    else:
        logit("No family ID found in model info", model_info)

    # Does the model_family exist?

    if not family:
        # Family doesnt exist
        # Add logic to fix this.
        logit("Family does not exist for family_id: %s", family_id)

    filename = f"{family[0]['name']}.pt"
    # Does the file exist?
    distfiles_path = f"{paths['models_path']}/{paths['models_distfiles_path']}"
    download_path = f"{paths['models_path']}/{paths['models_download_path']}"
    protected_path = SafeFS(Path(paths["models_path"]))

    logit("Checking if distfile exists for {filename}", filename)
    does_distfile_exist = check_for_file_in_dir(
        filename, paths["models_distfiles_path"], protected_path
    )
    logit("Checking if download exists for {filename}", filename)
    does_download_exist = check_for_file_in_dir(
        filename, paths["models_download_path"], protected_path
    )

    if not does_distfile_exist:
        logit(f"Distfile does not exist for {filename}", distfiles_path)
        if not does_download_exist:
            logit(f"Download does not exist for {filename}", download_path)
            url = family[0]["url"]
            results = download_file(url, filename, paths)
        else:
            logit(f"Download exists for {filename}", download_path)
            results = copy_file_to_dist(filename, paths, protected_path)
    else:
        logit(f"Distfile exists for {filename}", distfiles_path)
        results = True

    does_distfile_exist = check_for_file_in_dir(
        filename, paths["models_distfiles_path"], protected_path
    )

    does_download_exist = check_for_file_in_dir(
        filename, paths["models_download_path"], protected_path
    )

    if not does_distfile_exist:
        logit(
            f"Distfile still does not exist for {filename} after attempted copy",
            distfiles_path,
        )
        return "unable to copy distfile"
    if not does_download_exist:
        logit(
            f"Download still does not exist for {filename} after attempted copy",
            download_path,
        )
        return "unable to download file"

    model_filename = f"{model_info['name']}.pt"
    logit(f"Checking if model distfile exists for {model_filename}", model_filename)
    does_moddist_exist = check_for_file_in_dir(
        model_filename, paths["models_distfiles_path"], protected_path
    )

    if not does_moddist_exist:
        results = copy_modfam_to_model(filename, model_filename, paths, protected_path)

        if not results:
            logit(
                f"Failed to copy model family file to model file for {model_filename}"
            )
            return "unable to dist model file"

    # backup the file
    results = backup_dist_file(model_filename, paths, protected_path)
    return results
