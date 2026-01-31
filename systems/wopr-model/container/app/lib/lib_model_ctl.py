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
    logit("Filename: %s mod fam: %s" % (filename, model_family), "initialize_model")

    storage_paths = globals.storage_paths
    models_path = storage_paths["model_path"]
    distfiles_path = storage_paths["distfiles_path"]
    distfiles_subdir = "distfiles"
    downloads_path = storage_paths["downloads_path"]
    downloads_subdir = "downloads"
    protected_fs = SafeFS(models_path)
    has_dist = check_for_file_in_dir(distfiles_subdir, filename, protected_fs)

    if has_dist:
        logit(
            "initialize_model",
            f"Model file {filename} already found in distfiles.",
        )
        checksum = protected_fs.generate_checksum(Path(distfiles_subdir) / filename)
        return_payload = {
            "status": "exists",
            "location": "distfiles",
            "checksum": checksum,
        }
        return return_payload
    else:
        # chec(file, dir, pr)
        has_download = check_for_file_in_dir(downloads_subdir, filename, protected_fs)
        if has_download:
            logit(
                "initialize_model",
                f"Model file {filename} found in downloads. Copying to distfiles.",
            )
            protected_fs.copy_file(
                str(Path(downloads_subdir) / filename),
                str(Path(distfiles_subdir) / filename),
            )
            checksum = protected_fs.generate_checksum(Path(distfiles_subdir) / filename)
            return_payload = {
                "status": "copied",
                "location": "distfiles",
                "checksum": checksum,
            }
            return return_payload
        else:
            logit(
                "initialize_model",
                f"Model file {filename} not found locally. Downloading using ultralytics.",
            )
            logit(
                f"Settings {ultralytics.settings}",
                f"WEIGHTS: {ultralytics.settings['weights_dir']}",
            )
            model = ultralytics.YOLO(model_family)
            checksum = protected_fs.generate_checksum(Path(distfiles_subdir) / filename)
            return_payload = {
                "status": "downloaded",
                "location": "distfiles",
                "checksum": checksum,
            }
            return return_payload
