from typing import Any
from pathlib import Path
import hashlib
import inspect
import httpx
from fastapi import APIRouter, Request, BackgroundTasks
import requests

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

# Track active training
_training_active = False  # Simple flag for single-worker deployments
_active_training_id = None


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


def perform_training(payload: dict, callback_url: str):
    """Background task - actually does the training"""
    global _training_active, _active_training_id

    try:
        dataset = payload.get("dataset", {})
        model_version = payload.get("model_version", {})
        training_params = payload.get("training_params", {})
        training_run = payload.get("training_run", {})

        logger.info(f"Background training started for run {training_run.get('id')}")

        # Do the actual training
        result = train_yolo_model(
            model_version=model_version,
            dataset=dataset,
            training_params=training_params,
            training_run=training_run,
        )

        logger.info(f"Training complete: {result.get('status')}")

        # Call back to Django with results
        callback_payload = {
            "training_run_id": training_run.get("id"),
            "status": result.get("status"),
            "metrics": result.get("data", {}).get("metrics"),
            "model_path": result.get("data", {}).get("model_path"),
        }

        try:
            callback_response = requests.post(
                callback_url, json=callback_payload, timeout=300
            )
            logger.info(f"Callback sent: {callback_response.status_code}")
        except Exception as e:
            logger.error(f"Callback failed: {e}")

    except Exception as e:
        logger.error(f"Background training failed: {e}")
        try:
            requests.post(
                callback_url,
                json={
                    "training_run_id": payload.get("training_run", {}).get("id"),
                    "status": "error",
                    "error": str(e),
                },
                timeout=300,
            )
        except:
            logger.error("Failed to send error callback")
    finally:
        # Always clear the flag when done
        _training_active = False
        _active_training_id = None


@model_ctl.post("/api/model_ctl")
async def model_control(body: dict, background_tasks: BackgroundTasks):
    """
    Model control endpoint.
    For training: returns immediately, runs in background, calls back when done.
    For other actions: runs synchronously.
    """
    global _training_active, _active_training_id

    payload = body.get("payload", {})
    action = payload.get("action")

    logger.info(f"Note: (model_control)")
    logger.debug(f"Data: (body: {body})")

    match action:
        case "train":
            # Check if training already running
            if _training_active:
                logger.warning(
                    f"Training already in progress (run ID: {_active_training_id})"
                )
                return {
                    "status": "error",
                    "type": "training",
                    "message": "Training already in progress",
                    "active_training_run_id": _active_training_id,
                }

            # Get callback URL from payload
            callback_url = payload.get("callback_url")
            if not callback_url:
                logger.error("No callback_url provided for training")
                return {
                    "status": "error",
                    "message": "callback_url required for training",
                }

            # Mark training as active
            _training_active = True
            _active_training_id = payload.get("training_run", {}).get("id")

            # Queue training in background
            background_tasks.add_task(perform_training, payload, callback_url)

            return {
                "status": "started",
                "type": "training",
                "message": "Training started in background",
                "training_run_id": _active_training_id,
            }

        case "create_new_model_file":
            filename = payload.get("filename", "")
            model_family = payload.get("model_family", "")
            results = initialize_model(filename, model_family)

        case "generate_dataset":
            dataset = payload.get("dataset", "")
            results = generate_dataset(dataset)

        case _:
            results = {"status": "error", "message": f"Unknown action: {action}"}

    return results
