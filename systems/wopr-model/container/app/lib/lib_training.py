# Training function
import os
from pathlib import Path
from ultralytics import YOLO
from .helpers import setup_logger

logger = setup_logger()
logger.info("In lib_training.py")


def train_yolo_model(
    model_version: dict,
    dataset: dict,
    training_params: dict,
    training_run: dict,
) -> dict:
    """Train a YOLO model using the ultralytics package."""
    logger.info("Starting YOLO model training...")
    logger.info(f"Model Version: {model_version}")
    logger.info(f"Dataset: {dataset}")
    logger.info(f"Training Params: {training_params}")
    logger.info(f"Training Run: {training_run}")

    model_path = model_version.get("artifact_uri", "yolov8n.pt")
    logger.info(f"Loading YOLO model: {model_path}")

    try:
        model = YOLO(model_path)
    except Exception as e:
        logger.error(f"Model load failed: {e}")
        return {"status": "error", "type": "model_load", "message": str(e)}

    epochs = training_params.get("epochs", 100)
    batch = training_params.get("batch_size", 16)
    imgsz = training_params.get("imgsz", 640)
    patience = training_params.get("patience", 50)

    dataset_path = dataset.get("artifact_uri", "")
    data_yaml = str(Path(dataset_path) / "data.yaml")

    logger.info(
        f"Training parameters - epochs: {epochs}, batch: {batch}, "
        f"imgsz: {imgsz}, patience: {patience}, data: {data_yaml}"
    )

    try:
        training_results = model.train(
            data=data_yaml,
            epochs=epochs,
            batch=batch,
            imgsz=imgsz,
            patience=patience,
            project=f"/ultralytics/runs/{training_run['uuid']}",
            name="train",
        )

        # Extract the ACTUAL metrics that matter
        results_dict = (
            training_results.results_dict
            if hasattr(training_results, "results_dict")
            else {}
        )

        metrics = {
            "precision": results_dict.get("metrics/precision(B)"),
            "recall": results_dict.get("metrics/recall(B)"),
            "mAP50": results_dict.get("metrics/mAP50(B)"),
            "mAP50_95": results_dict.get("metrics/mAP50-95(B)"),
            "fitness": results_dict.get("fitness"),
            "final_epoch": (
                training_results.epoch if hasattr(training_results, "epoch") else None
            ),
            "save_dir": (
                str(training_results.save_dir)
                if hasattr(training_results, "save_dir")
                else None
            ),
        }

        # Optional: Per-class performance for debugging
        if hasattr(training_results, "maps"):
            # This is the per-class mAP array
            metrics["per_class_map"] = (
                training_results.maps.tolist()
                if hasattr(training_results.maps, "tolist")
                else None
            )

        if hasattr(training_results, "names"):
            # Class names for reference
            metrics["class_names"] = training_results.names

        logger.info(f"Training completed. Metrics: {metrics}")

        return {
            "status": "success",
            "type": "training",
            "data": {
                "metrics": metrics,
                "model_path": (
                    str(training_results.save_dir / "weights/best.pt")
                    if hasattr(training_results, "save_dir")
                    else None
                ),
            },
        }

    except Exception as e:
        logger.error(f"Training failed: {e}")
        return {"status": "error", "type": "training", "message": str(e)}
