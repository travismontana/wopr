import ultralytics
from pathlib import Path
from datetime import datetime
import lib.globals as globals
from lib.helpers import logit, setup_logger

from lib.safe_file import SafeFS

logger = setup_logger()


def initialize_model(filename: str, model_family: str):
    """Initialize Model
    Let ultralytics handle the download if not found locally.
    save the model to the specified new model filename.

    Args:
        filename (str): The filename to save the model to.
        model_family (str): The model family to initialize.
    """
    timenow = datetime.now().strftime("%Y%m%d%H%M%S")
    fixed_filename = f"{globals.WEIGHTS_PATH}/{filename}"
    fixed_backup_filename = f"{globals.WEIGHTS_PATH}/{timenow}_bak_{filename}"
    logit("Filename: %s mod fam: %s" % (filename, model_family), "initialize_model")
    logit(f"Checking if file {fixed_filename} exists", "initialize_model")
    if Path(f"{fixed_filename}").exists():
        mod = ultralytics.YOLO(fixed_filename)
        logit(f"file {fixed_filename} exists, loading model", "initialize_model")
        results = {
            "status": "success",
            "type": "model_exists",
            "data": {
                "mod_info": {
                    "names": mod.names,
                    "device": mod.device,
                    "transforms": mod.transforms,
                    "task_map": mod.task_map,
                },
                "fixed_filename": fixed_filename,
                "fixed_backup_filename": fixed_backup_filename,
            },
        }
        return results
    # let ultralytics handle the download if not found locally

    mod_fam = ultralytics.YOLO(model_family)
    if not Path(fixed_backup_filename).exists():
        logit(f"Backing up file to {fixed_backup_filename}", "initialize_model")
        mod_fam.save(fixed_backup_filename)
    else:
        logit(f"File {fixed_filename} exists, no backup created", "initialize_model")
    if not Path(fixed_filename).exists():
        logit(f"Saving model to {fixed_filename}", "initialize_model")
        mod_fam.save(fixed_filename)
    else:
        logit(f"File {fixed_filename} exists, not saving model", "initialize_model")

    results = {
        "status": "success",
        "type": "model_info",
        "data": {
            "filename": filename,
            "filepath": fixed_filename,
            "backup_filename": f"{timenow}_bak_{filename}",
            "backup_filepath": fixed_backup_filename,
            "mod_info": mod_fam.info(detailed=True, verbose=True),
        },
    }
    return results
