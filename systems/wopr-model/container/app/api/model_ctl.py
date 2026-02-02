from typing import Any
from pathlib import Path
import hashlib
import inspect
import httpx
from fastapi import APIRouter, Request


from lib.helpers import (
    setup_logger,
    logit,
    check_for_file_in_dir,
    copy_file_to_dist,
    copy_modfam_to_model,
    backup_dist_file,
)

from lib.lib_model_ctl import initialize_model, generate_dataset

from lib.safe_file import SafeFS

logger = setup_logger()

model_ctl = APIRouter(tags=["models"])

@model_ctl.post("")
def model_control(request: Request, body: dict[str, Any]):
    """Model Control
    initalize:
      does the file exist in storage_paths["distfiles_path"]
      if not then check if it's in storage_paths["downloads_path"]
      if it's not there then download it using ultralytics.
    Args:
        request (Request): _description_
        body (dict[str, Any]): _description_
    """
    logit("model_control", f"body: {body}")
    payload = body.get("payload", {})
    action = payload.get("action", "")

    match action:
        case "create_new_model_file":
            filename = payload.get("filename", "")
            model_family = payload.get("model_family", "")
            results = initialize_model(filename, model_family)
        case "generate_dataset":
            dataset = payload.get("dataset", "")
            dataset_uuid = payload.get("dataset_uuid", "")
            results = generate_dataset(dataset_uuid, dataset)
        case _:
            results = {"status": "error", "message": f"Unknown action: {action}"}
    return results
