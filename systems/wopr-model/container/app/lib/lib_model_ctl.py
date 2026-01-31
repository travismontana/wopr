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
