import ultralytics
from pathlib import Path
import lib.globals as globals
from lib.helpers import logit, setup_logger, check_for_file_in_dir

from lib.safe_file import SafeFS

logger = setup_logger()


def initialize_model(filename: str, model_family: str):
    """Initialize Model
    Check if the model file exists in distfiles_path.
    If not, check downloads_path.
    If not there, download using ultralytics.

    Args:
        model_name (str): Name of the model to initialize.
    """
    logit("Filename: %s mod fam: %s" % (filename, model_family))

    storage_paths = globals.storage_paths
    models_path = storage_paths["model_path"]
    distfiles_path = storage_paths["distfiles_path"]
    downloads_path = storage_paths["downloads_path"]
    protected_fs = SafeFS(models_path)
    has_dist = check_for_file_in_dir(distfiles_path, filename, protected_fs)

    if has_dist:
        logit(
            "initialize_model",
            f"Model file {filename} already found in distfiles.",
        )
        checksum = protected_fs.generate_checksum("distfiles" / filename)
        return_payload = {
            "status": "exists",
            "location": "distfiles",
            "checksum": checksum,
        }
        return
        payload = {"status": "exists", "location": "distfiles"}
