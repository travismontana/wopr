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
