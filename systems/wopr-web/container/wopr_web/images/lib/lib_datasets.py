import os
import json
import shutil
from zipfile import ZipFile
from core.models import Game, GameLabelproj, Image, ImageGame, MLDataset
from lib.helpers import get_config, setup_logger
from .lib_labelstudio import export_and_download_snapshot, convert_snapshot
from sklearn.model_selection import train_test_split

logger = setup_logger()
config = get_config()

BASE_PATH = config["storage"]["base_path"]

IMAGES_SUBDIR = config["storage"]["images_subdir"]
INCOMING_SUBDIR = config["storage"]["incoming_subdir"]
ARCHIVE_SUBDIR = config["storage"]["archive_subdir"]
GAMES_SUBDIR = "games"
BACKUPS_SUBDIR = "backups"
LABEL_SUBDIR = config["storage"]["label_subdir"]
LABEL_SOURCE_SUBDIR = config["storage"]["label_source_subdir"]
LABEL_TARGET_SUBDIR = config["storage"]["label_target_subdir"]

MODELS_SUBDIR = config["storage"]["models_subdir"]
WEIGHTS_SUBDIR = config["storage"]["weights_subdir"]
RUNS_SUBDIR = config["storage"]["runs_subdir"]
DISTFILES_SUBDIR = config["storage"]["distfiles_subdir"]
BACKUPS_SUBDIR = config["storage"]["backups_subdir"]
MODELS_ARCHIVE_SUBDIR = config["storage"]["archive_subdir"]

IMAGES_URL = config["api"]["images_url"]
THUMBS_URL = config["api"]["thumbs_url"]
THUMB_URL_BASE = f"{THUMBS_URL}/insecure/resize:fill:300:200/plain"

WOPRS = {
    "images": {
        "incoming": f"{BASE_PATH}/{IMAGES_SUBDIR}/{INCOMING_SUBDIR}",
        "archive": f"{BASE_PATH}/{IMAGES_SUBDIR}/{ARCHIVE_SUBDIR}",
        "games": f"{BASE_PATH}/{IMAGES_SUBDIR}/{GAMES_SUBDIR}",
        "backups": f"{BASE_PATH}/{IMAGES_SUBDIR}/{BACKUPS_SUBDIR}",
    },
    "ls": {
        "source": f"{BASE_PATH}/{LABEL_SUBDIR}/{LABEL_SOURCE_SUBDIR}",
        "target": f"{BASE_PATH}/{LABEL_SUBDIR}/{LABEL_TARGET_SUBDIR}",
        "games": f"{BASE_PATH}/{LABEL_SUBDIR}",
    },
    "models": {
        "weights": f"{BASE_PATH}/{MODELS_SUBDIR}/{WEIGHTS_SUBDIR}",
        "datasets": f"{BASE_PATH}/{MODELS_SUBDIR}/datasets",
        "runs": f"{BASE_PATH}/{MODELS_SUBDIR}/{RUNS_SUBDIR}",
        "distfiles": f"{BASE_PATH}/{MODELS_SUBDIR}/{DISTFILES_SUBDIR}",
        "backups": f"{BASE_PATH}/{MODELS_SUBDIR}/{BACKUPS_SUBDIR}",
        "archive": f"{BASE_PATH}/{MODELS_SUBDIR}/{MODELS_ARCHIVE_SUBDIR}",
    },
}


def work_datasets_mgmt(game_id):
    """Actual implementation for managing datasets for a specific game"""
    logger.info("Managing datasets for game_id: %s", game_id)
    results = []
    game = Game.objects.get(id=game_id)
    ml_datasets = MLDataset.objects.filter(game=game)
    logger.info("Found %d datasets for game_id: %s", ml_datasets.count(), game_id)
    results.append({"status": "success", "message": ml_datasets})
    return results


def work_create_mldataset(game_id, ls_project_id, mldataset_name):
    """Create an ML dataset from a Label Studio project export.

    Args:
        game_id: Database ID of the game
        ls_project_id: Label Studio project ID
        mldataset_name: Name for the dataset directory
    """
    logger.info(
        "Creating ML dataset %s for game_id: %s, ls_project_id: %s",
        mldataset_name,
        game_id,
        ls_project_id,
    )
    game = Game.objects.get(id=game_id)
    game_shortname = game.shortname
    # directory setup
    dataset_base = f"{WOPRS['models']['datasets']}/{game_shortname}"
    dataset_path = f"{dataset_base}/{mldataset_name}"
    os.makedirs(dataset_path, exist_ok=True)
    logger.info(f"Created dataset directory at {dataset_path}")

    export_id = export_and_download_snapshot(ls_project_id, dataset_path)
    logger.info(f"Downloaded export snapshot with ID {export_id}")

    export_type = "JSON"
    convert_snapshot(ls_project_id, dataset_path, export_type, export_id)
    logger.info(f"Converted export snapshot to {export_type} format")

    export_type = "YOLO"
    convert_snapshot(ls_project_id, dataset_path, export_type, export_id)
    logger.info(f"Converted export snapshot to {export_type} format")

    fname = f"project_{ls_project_id}_export_{export_id}"
    json_fname = f"{dataset_path}/{fname}.json"
    yolo_file = f"{dataset_path}/{fname}.yolo"
    yolo_dir = f"{dataset_path}/yolo"
    logger.info(
        f"Came up with: json_fname={json_fname}, yolo_file={yolo_file}, yolo_dir={yolo_dir}"
    )

    os.makedirs(yolo_dir, exist_ok=True)
    with ZipFile(yolo_file, "r") as zip_ref:
        zip_ref.extractall(yolo_dir)

    stuff = {}
    stuff["mldataset_name"] = mldataset_name
    stuff["export_id"] = export_id
    stuff["json_fname"] = json_fname
    stuff["yolo_file"] = yolo_file
    stuff["yolo_dir"] = yolo_dir

    # train/val/test split
    labelsdir_list = os.listdir(f"{yolo_dir}/labels")
    train, temp = train_test_split(labelsdir_list, test_size=0.3, random_state=42)
    val, test = train_test_split(temp, test_size=0.5, random_state=42)
    logger.info(f"Lengths of train, val, test: {len(train)}, {len(val)}, {len(test)}")

    # create split directories
    labels_train_dir = f"{yolo_dir}/labels/train"
    images_train_dir = f"{yolo_dir}/images/train"
    os.makedirs(labels_train_dir, exist_ok=True)
    os.makedirs(images_train_dir, exist_ok=True)

    labels_val_dir = f"{yolo_dir}/labels/val"
    images_val_dir = f"{yolo_dir}/images/val"
    os.makedirs(labels_val_dir, exist_ok=True)
    os.makedirs(images_val_dir, exist_ok=True)

    labels_test_dir = f"{yolo_dir}/labels/test"
    images_test_dir = f"{yolo_dir}/images/test"
    os.makedirs(labels_test_dir, exist_ok=True)
    os.makedirs(images_test_dir, exist_ok=True)

    logger.info(
        f"Created image directories: {images_train_dir}, {images_val_dir}, {images_test_dir}"
    )
    logger.info(
        f"Created label directories: {labels_train_dir}, {labels_val_dir}, {labels_test_dir}"
    )

    # build lookup: short uuid -> image filename only
    with open(f"{json_fname}", "r") as json_file:
        tasks = json.load(json_file)

    # FIX 2: was storing full task dict — now stores just the image filename
    lookup = {}
    for task in tasks:
        url = task["data"]["image"]
        filename = url.split("/")[-1]  # full filename: a257ec6c-...-uuid.jpg
        short_uuid = filename.replace(".jpg", "")[:8]
        lookup[short_uuid] = filename
    logger.info(f"Created lookup dictionary with {len(lookup)} entries")

    def copy_image(label_filename, images_dest_dir):
        """Helper to resolve and copy an image for a given label file."""
        short_uuid = label_filename.replace("__.txt", "")
        image_filename = lookup.get(short_uuid)
        if not image_filename:
            logger.warning(f"No image found in lookup for label: {label_filename}")
            return
        source_image = f"{WOPRS['images']['games']}/{game_shortname}/{image_filename}"
        try:
            shutil.copy(source_image, images_dest_dir)
        except Exception as e:
            logger.error(
                f"Error copying image {source_image} to {images_dest_dir}: {e}"
            )

    # move labels and copy images for each split
    for f_train in train:
        shutil.move(f"{yolo_dir}/labels/{f_train}", labels_train_dir)
        copy_image(f_train, images_train_dir)

    # FIX 3: val and test were missing image copy logic entirely
    for f_val in val:
        shutil.move(f"{yolo_dir}/labels/{f_val}", labels_val_dir)
        copy_image(f_val, images_val_dir)

    for f_test in test:
        shutil.move(f"{yolo_dir}/labels/{f_test}", labels_test_dir)
        copy_image(f_test, images_test_dir)

    # FIX 4: generate dataset.yaml — ultralytics requires this for training
    classes_txt = f"{yolo_dir}/classes.txt"
    with open(classes_txt, "r") as f:
        class_names = [line.strip() for line in f.readlines() if line.strip()]

    dataset_yaml = f"{yolo_dir}/dataset.yaml"
    with open(dataset_yaml, "w") as f:
        f.write(f"path: {yolo_dir}\n")
        f.write(f"train: images/train\n")
        f.write(f"val: images/val\n")
        f.write(f"test: images/test\n")
        f.write(f"\n")
        f.write(f"nc: {len(class_names)}\n")
        f.write(f"names: {class_names}\n")
    logger.info(
        f"Generated dataset.yaml at {dataset_yaml} with {len(class_names)} classes"
    )

    stuff["dataset_yaml"] = dataset_yaml
    return stuff
