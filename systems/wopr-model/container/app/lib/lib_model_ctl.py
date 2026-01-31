import ultralytics
from pathlib import Path
from datetime import datetime as now
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
    timenow = now().strftime("%Y%m%d%H%M%S")
    fixed_filename = f"{globals.WEIGHTS_PATH}/{filename}"
    fixed_backup_filename = f"{globals.WEIGHTS_PATH}/{timenow}_bak_{filename}"
    logit("Filename: %s mod fam: %s" % (filename, model_family), "initialize_model")
    if Path(f"/ultralytics/{fixed_filename}").exists():
        mod = ultralytics.YOLO(fixed_filename)
        logit(f"file {fixed_filename} exists, loading model", "initialize_model")
        results = {
            "status": "error",
            "type": "model_exists",
            "info": {
                "mod_info": mod.info(),
                "fixed_filename": fixed_filename,
                "fixed_backup_filename": fixed_backup_filename,
            },
        }
        return
    # let ultralytics handle the download if not found locally

    mod_fam = ultralytics.YOLO(model_family)
    mod_fam.save(fixed_backup_filename)
    mod_fam.save(fixed_filename)
    results = {
        "status": "success",
        "type": "model_info",
        "file_info": {
            "filename": filename,
            "filepath": fixed_filename,
            "backup_filename": f"{timenow}_bak_{filename}",
            "backup_filepath": fixed_backup_filename,
            "mod_info": mod_fam.info(),
        },
    }
    return results
