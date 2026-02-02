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
from lib.lib_training import train_yolo_model

from lib.safe_file import SafeFS

logger = setup_logger()

model_ctl = APIRouter(tags=["models"])


# FastAPI endpoint
@model_ctl.post("")
def model_control(body: dict[str, Any]):  # Removed unused Request
    """Model Control endpoint for model operations."""
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
        case "train":
            results = train_yolo_model(
                model_version=payload.get("model_version", {}),
                dataset=payload.get("dataset", {}),
                training_params=payload.get("training_params", {}),
                training_run=payload.get("training_run", {}),
            )
        case _:
            results = {"status": "error", "message": f"Unknown action: {action}"}

    return results
