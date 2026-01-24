from typing import Any
from pathlib import Path
import hashlib
import inspect
import httpx
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


async def do_api_things(action, base_url, route, path, payload):
    headers = {}  # Fix this too

    action_map = {
        "get": "GET",
        "post": "POST",
        "put": "PUT",
        "patch": "PATCH",
        "delete": "DELETE",
    }

    method = action_map[action.lower()]
    timeout = 30.0

    parts = [WOPR_API_URL, route, path]
    url = "/".join(str(p).strip("/") for p in parts if p)

    async with httpx.AsyncClient(timeout=timeout) as client:
        if method in ["POST", "PUT", "PATCH"] and payload:
            response = await client.request(method, url, json=payload, headers=headers)
        else:
            response = await client.request(
                method, url, params=payload, headers=headers
            )

        response.raise_for_status()
        return response.json()


@api_models.post("/model_status")
async def model_status(data: dict, request: Request):
    """Get the status of the model, via post"""
    logger.info("Model status update received")
    logger.debug("Data: %s", data)
    model_id = data.get("model_id")
    config = request.app.state.config
    paths = request.app.state.paths
    try:
        logger.info(f"Retrieving model info for model ID: {model_id}")
        model_info = await do_api_things("get", WOPR_API_URL, "models", model_id, None)
    except Exception as e:
        logit(f"Error retrieving model info: {e}")
        return False

    if model_info is None or not model_info:
        message = f"Model id ({model_id}) not found"
        logit(message, model_info)
        return message
    logit("Model info retrieved", model_info)

    return model_info


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
