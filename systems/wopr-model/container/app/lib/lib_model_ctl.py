import os
import time
import json
import yaml
import shutil
import random
import ultralytics
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

import lib.globals as globals
from lib.helpers import logit, setup_logger
from lib.safe_file import SafeFS
from label_studio_sdk import LabelStudio
from label_studio_sdk.converter import Converter
from label_studio_sdk._extensions.label_studio_tools.core.utils.io import get_local_path

logger = setup_logger()
LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://label-studio:8080")
LABEL_STUDIO_TOKEN = os.getenv("LABEL_STUDIO_TOKEN", "changeme")

try:
    logger.info(f"Connecting to Label Studio at {LABEL_STUDIO_URL}")
    client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_TOKEN)
except Exception as e:
    logger.error(f"Failed to connect to Label Studio: {e}")
    client = None


def initialize_model(filename: str, model_family: str):
    """Initialize Model
    Let ultralytics handle the download if not found locally.
    save the model to the specified new model filename.

    Args:
        filename (str): The filename to save the model to.
        model_family (str): The model family to initialize.
    """
    timenow = datetime.now().strftime("%Y%m%d%H%M%S")
    protected_path = SafeFS(Path(globals.WEIGHTS_PATH))
    fixed_filename = f"{globals.WEIGHTS_PATH}/{filename}"
    fixed_backup_filename = f"{globals.WEIGHTS_PATH}/{timenow}_bak_{filename}"
    logit("Filename: %s mod fam: %s" % (filename, model_family), "initialize_model")
    logit(f"Checking if file {fixed_filename} exists", "initialize_model")
    if Path(f"{fixed_filename}").exists():
        checksum = protected_path.generate_checksum(filename)
        mod = ultralytics.YOLO(fixed_filename)
        logit(f"file {fixed_filename} exists, loading model", "initialize_model")
        results = {
            "status": "success",
            "type": "model_exists",
            "data": {
                "mod_info": mod.info(),
                "checksum": checksum,
                "fixed_filename": fixed_filename,
            },
        }
    else:
        mod_fam = ultralytics.YOLO(model_family)
        if not Path(fixed_backup_filename).exists():
            logit(f"Backing up file to {fixed_backup_filename}", "initialize_model")
            mod_fam.save(fixed_backup_filename)
        else:
            logit(
                f"File {fixed_filename} exists, no backup created", "initialize_model"
            )
        if not Path(fixed_filename).exists():
            logit(f"Saving model to {fixed_filename}", "initialize_model")
            mod_fam.save(fixed_filename)
        else:
            logit(f"File {fixed_filename} exists, not saving model", "initialize_model")
        checksum = protected_path.generate_checksum(filename)
        backup_checksum = protected_path.generate_checksum(f"{timenow}_bak_{filename}")
        results = {
            "status": "success",
            "type": "model_info",
            "data": {
                "mod_info": mod_fam.info(),
                "checksum": checksum,
                "fixed_filename": fixed_filename,
                "fixed_backup_filename": fixed_backup_filename,
                "backup_checksum": backup_checksum,
            },
        }
    return results


def generate_dataset(dataset_uuid: str, dataset: dict):
    """Generate Dataset from Label Studio project.

    Exports project annotations in YOLO format and downloads all images.

    Args:
        project_id (int): Label Studio project ID
        dataset_uuid (str): UUID for the dataset directory
        view_id (int, optional): Specific view to export

    Returns:
        dict: Results with status and dataset info
    """
    if client is None:
        return {
            "status": "error",
            "message": "No connection to Label Studio",
        }

    try:
        # Setup paths
        logger.info("Starting dataset generation process")
        logger.debug(f"Dataset UUID: {dataset_uuid}, Dataset info: {dataset}")
        project_id = dataset.get("project_id", "")
        if dataset_uuid == "":
            return {
                "status": "error",
                "message": "Dataset UUID is required",
            }
        view_id: int = None
        dataset_path = Path(globals.DATASETS_PATH) / str(dataset_uuid)
        logit(
            f"Generating dataset {dataset_uuid} for project {project_id}",
            "generate_dataset",
        )
        # Check if dataset already exists
        if dataset_path.exists() and any(dataset_path.iterdir()):
            logger.warning(f"Dataset {dataset_uuid} already exists")
            return {
                "status": "error",
                "message": f"Dataset {dataset_uuid} already exists",
            }

        # Create dataset directory
        dataset_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created dataset directory: {dataset_path}")

        # Get project
        logger.info(f"Retrieving project {project_id}")
        project = client.projects.get(id=project_id)

        # Create export snapshot
        logger.info("Creating export snapshot")
        create_kwargs = {"title": f"YOLO Export {dataset_uuid}"}
        if view_id is not None:
            create_kwargs["task_filter_options"] = {"view": view_id}

        export = client.projects.exports.create(project_id, **create_kwargs)

        # Wait for export to complete
        logger.info("Waiting for export to complete...")
        max_wait = 300  # 5 minutes
        elapsed = 0
        while export.status == "in_progress":
            if elapsed >= max_wait:
                raise TimeoutError("Export timed out")
            time.sleep(3)
            elapsed += 3
            export = client.projects.exports.get(id=project_id, export_pk=export.id)
            logger.debug(f"Export status: {export.status} ({elapsed}s)")

        if export.status != "completed":
            raise Exception(f"Export failed with status: {export.status}")

        # Download annotations
        logger.info("Downloading annotations")
        snapshot_path = dataset_path / f"project_{project_id}_export.json"
        data_iter = client.projects.exports.download(
            id=project_id, export_pk=export.id, export_type="JSON"
        )

        with open(snapshot_path, "wb") as f:
            for data in data_iter:
                f.write(data)

        # Load exported tasks
        with open(snapshot_path) as f:
            exported_tasks = json.load(f)

        logger.info(f"Loaded {len(exported_tasks)} tasks from export")

        # Convert to YOLO format
        logger.info("Converting to YOLO format")
        label_config = project.label_config
        converter = Converter(
            config=label_config, project_dir=str(dataset_path), download_resources=False
        )

        yolo_output_dir = dataset_path / "yolo"
        converter.convert_to_yolo(
            input_data=str(snapshot_path), output_dir=str(yolo_output_dir), is_dir=False
        )

        # Create images directory
        images_dir = yolo_output_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        # Download images with retry logic
        logger.info("Downloading images")
        downloaded_count = 0
        failed_count = 0

        for task in tqdm(exported_tasks, desc="Downloading images"):
            image_url = next(iter(task["data"].values()), None)
            if not image_url:
                logger.warning(f"No image URL for task {task['id']}")
                continue

            max_retries = 5
            retry_delay = 1

            for attempt in range(1, max_retries + 1):
                try:
                    local_image_path = get_local_path(
                        url=image_url,
                        hostname=LABEL_STUDIO_URL,
                        access_token=LABEL_STUDIO_TOKEN,
                        task_id=task["id"],
                        download_resources=True,
                    )

                    # Extract filename and copy to images dir
                    # name = os.path.basename(local_image_path).split("__", 1)[-1]
                    name = os.path.basename(local_image_path) + ".jpg"
                    destination_path = images_dir / name
                    shutil.copy2(local_image_path, destination_path)

                    downloaded_count += 1
                    logger.debug(f"Downloaded: {name}")
                    break

                except Exception as e:
                    if attempt < max_retries:
                        sleep_time = retry_delay * (2 ** (attempt - 1))
                        logger.debug(
                            f"Retry {attempt}/{max_retries} after {sleep_time}s: {e}"
                        )
                        time.sleep(sleep_time)
                    else:
                        logger.error(
                            f"Failed to download image for task {task['id']}: {e}"
                        )
                        failed_count += 1

        logger.info(f"Downloaded {downloaded_count} images, {failed_count} failed")

        # Split into train/val
        stats = split_yolo_train_val(yolo_output_dir, val_ratio=0.2, seed=42)
        logger.info(f"Dataset split stats: {stats}")

        # Write data.yaml for split
        data_yaml_path = write_data_yaml_for_split(yolo_output_dir)
        logger.info(f"Updated data.yaml at {data_yaml_path}")

        # Return results
        return {
            "status": "success",
            "message": f"Dataset {dataset_uuid} created successfully",
            "data": {
                "dataset_path": str(dataset_path),
                "yolo_path": str(yolo_output_dir),
                "images_path": str(images_dir),
                "data_yaml": data_yaml_path,
                "total_tasks": len(exported_tasks),
                "images_downloaded": downloaded_count,
                "images_failed": failed_count,
            },
        }

    except Exception as e:
        logger.error(f"Error generating dataset: {e}")
        return {
            "status": "error",
            "message": f"Dataset generation failed: {str(e)}",
        }


def create_data_yaml(dataset_path: str):
    """Create data.yaml for YOLO training.

    Args:
        dataset_path (str): Path to the dataset directory

    Returns:
        str: Path to created data.yaml file
    """
    dataset_path = Path(dataset_path)
    yolo_path = dataset_path / "yolo"
    classes_file = yolo_path / "classes.txt"

    # Read class names
    with open(classes_file, "r") as f:
        class_names = [line.strip() for line in f.readlines()]

    # Create data.yaml structure
    data_yaml = {
        "path": str(yolo_path.absolute()),
        "train": "images",  # relative to path
        "val": "images",  # using same for now, could split later
        "nc": len(class_names),
        "names": {i: name for i, name in enumerate(class_names)},
    }

    # Write data.yaml
    yaml_file = yolo_path / "data.yaml"
    with open(yaml_file, "w") as f:
        yaml.dump(data_yaml, f, default_flow_style=False)

    logger.info(f"Created data.yaml at {yaml_file}")
    logger.debug(f"Classes: {class_names}")

    return str(yaml_file)


def split_yolo_train_val(
    yolo_dir: Path,
    val_ratio: float = 0.2,
    seed: int = 42,
    image_exts: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp"),
) -> dict:
    """
    Split YOLO dataset into train/val by moving files:
      yolo/images/*.jpg  -> yolo/images/train|val/
      yolo/labels/*.txt  -> yolo/labels/train|val/

    Assumes label filename stem matches image filename stem (YOLO convention).
    Creates empty label files if missing (valid for "no objects").

    Returns counts and any mismatches.
    """
    yolo_dir = Path(yolo_dir)
    images_root = yolo_dir / "images"
    labels_root = yolo_dir / "labels"

    if not images_root.exists():
        raise FileNotFoundError(f"Missing images dir: {images_root}")
    if not labels_root.exists():
        raise FileNotFoundError(f"Missing labels dir: {labels_root}")

    train_images = images_root / "train"
    val_images = images_root / "val"
    train_labels = labels_root / "train"
    val_labels = labels_root / "val"

    for d in (train_images, val_images, train_labels, val_labels):
        d.mkdir(parents=True, exist_ok=True)

    # Only take images that are currently in the root (not already split)
    images = [
        p
        for p in images_root.iterdir()
        if p.is_file() and p.suffix.lower() in image_exts
    ]
    images.sort(key=lambda p: p.name)  # stable before shuffle

    rng = random.Random(seed)
    rng.shuffle(images)

    n_val = int(round(len(images) * val_ratio))
    val_set = set(images[:n_val])

    stats = {
        "total_images_seen": len(images),
        "val_ratio": val_ratio,
        "seed": seed,
        "moved_train": 0,
        "moved_val": 0,
        "missing_label_created": 0,
        "orphan_labels_remaining_in_root": 0,
    }

    for img in images:
        stem = img.stem
        lbl = labels_root / f"{stem}.txt"

        if img in val_set:
            img_dst = val_images / img.name
            lbl_dst = val_labels / f"{stem}.txt"
            bucket = "val"
        else:
            img_dst = train_images / img.name
            lbl_dst = train_labels / f"{stem}.txt"
            bucket = "train"

        img.rename(img_dst)

        if lbl.exists():
            lbl.rename(lbl_dst)
        else:
            # Valid YOLO: empty file = no objects
            lbl_dst.write_text("")
            stats["missing_label_created"] += 1

        if bucket == "val":
            stats["moved_val"] += 1
        else:
            stats["moved_train"] += 1

    # Count any leftover label files still sitting in labels_root (usually means mismatch)
    leftover_labels = [
        p for p in labels_root.iterdir() if p.is_file() and p.suffix.lower() == ".txt"
    ]
    stats["orphan_labels_remaining_in_root"] = len(leftover_labels)

    return stats


def write_data_yaml_for_split(yolo_dir: Path) -> str:
    """
    Writes/overwrites yolo/data.yaml to use images/train and images/val.
    Preserves existing names if present; otherwise derives from classes.txt.
    """
    yolo_dir = Path(yolo_dir)
    yaml_path = yolo_dir / "data.yaml"

    # Try to preserve any existing YAML content
    existing = {}
    if yaml_path.exists():
        try:
            existing = yaml.safe_load(yaml_path.read_text()) or {}
        except Exception:
            existing = {}

    classes_file = yolo_dir / "classes.txt"
    class_names = []
    if classes_file.exists():
        class_names = [
            line.strip()
            for line in classes_file.read_text().splitlines()
            if line.strip()
        ]

    # Prefer existing names mapping if present
    names = existing.get("names")
    if not names:
        names = {i: n for i, n in enumerate(class_names)}

    data_yaml = {
        "path": str(yolo_dir.absolute()),
        "train": "images/train",
        "val": "images/val",
        "names": names,
    }

    # Optional but harmless
    if class_names:
        data_yaml["nc"] = len(class_names)

    yaml_path.write_text(yaml.safe_dump(data_yaml, sort_keys=False))
    return str(yaml_path)
