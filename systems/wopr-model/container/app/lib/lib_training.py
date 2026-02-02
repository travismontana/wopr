# Training function
import os
from pathlib import Path
from ultralytics import YOLO
from .helpers import setup_logger, get_config

logger = setup_logger()
config = get_config()
logger.info("In lib_training.py")


def train_yolo_model(
    model_version: dict,  # Fixed name
    dataset: dict,
    training_params: dict,
    training_run: dict,
) -> dict:  # Single dict return, not list
    """Train a YOLO model using the ultralytics package."""
    logger.info("Starting YOLO model training...")
    logger.info(f"Model Version: {model_version}")
    logger.info(f"Dataset: {dataset}")
    logger.info(f"Training Params: {training_params}")
    logger.info(f"Training Run: {training_run}")

    # Load the YOLO model using correct key
    model_path = model_version.get("artifact_uri", "yolov8n.pt")
    logger.info(f"Loading YOLO model: {model_path}")

    try:
        model = YOLO(model_path)
    except Exception as e:
        logger.error(f"Model load failed: {e}")
        return {"status": "error", "type": "model_load", "message": str(e)}

    # Prepare training parameters
    epochs = training_params.get("epochs", 100)
    batch = training_params.get("batch_size", 16)  # Renamed for clarity
    imgsz = training_params.get("imgsz", 640)
    patience = training_params.get("patience", 50)

    # Construct data.yaml path
    dataset_path = dataset.get("artifact_uri", "")
    data_yaml = str(Path(dataset_path) / "data.yaml")

    logger.info(
        f"Training parameters - epochs: {epochs}, batch: {batch}, "
        f"imgsz: {imgsz}, patience: {patience}, data: {data_yaml}"
    )

    try:
        # Start training with all parameters
        training_results = model.train(
            data=data_yaml,
            epochs=epochs,
            batch=batch,  # Correct parameter name
            imgsz=imgsz,
            patience=patience,  # Now using it
            project=f"/ultralytics/runs/{training_run['uuid']}",  # Organize outputs
            name="train",
        )

        # Extract serializable metrics
        metrics = {
            "final_epoch": (
                training_results.epoch if hasattr(training_results, "epoch") else None
            ),
            "best_fitness": (
                float(training_results.best_fitness)
                if hasattr(training_results, "best_fitness")
                else None
            ),
            "save_dir": (
                str(training_results.save_dir)
                if hasattr(training_results, "save_dir")
                else None
            ),
        }

        logger.info(f"Training completed. Metrics: {metrics}")
        logger.debug(f"Training results object: {training_results}")

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
