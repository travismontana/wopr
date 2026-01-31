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
    logit("Filename: %s mod fam: %s" % (filename, model_family), "initialize_model")
    if Path(f"{globals.WEIGHTS_PATH}/{filename}").exists():
        logit(f"Model {filename} already exists", "initialize_model")
        return {"status": "skipped", "message": "Model already exists."}
    # let ultralytics handle the download if not found locally
    timenow = now().strftime("%Y%m%d%H%M%S")
    mod_fam = ultralytics.YOLO(model_family)
    mod_fam.save(f"{globals.WEIGHTS_PATH}/{timenow}_bak_{filename}")
    mod_fam.save(f"{globals.WEIGHTS_PATH}/{filename}")
    results = {
        "status": "success",
        "type": "model_info",
        "file_info": {
            "filename": filename,
            "filepath": f"{globals.WEIGHTS_PATH}/{filename}",
            "backup_filename": f"{timenow}_bak_{filename}",
            "backup_filepath": f"{globals.WEIGHTS_PATH}/{timenow}_bak_{filename}",
            "mod_info": mod_fam.info(),
        },
    }
    return results
